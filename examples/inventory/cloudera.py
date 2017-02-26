#!/usr/bin/env python

#
# (c) 2016 Yassine Azzouz, <yassine.azzouz@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

'''
Cloudera Inventory Script
=======================
Author: Yassine Azzouz
Description:
  Retrieve information about hosts, roles, services and clusters from the
  Cloudera Manager server.
  This script will attempt to read configuration from an INI file with the same
  base filename if present, or `/etc/ansible/cm.ini` if not.  It is possible to create
  symlinks to the inventory script to support multiple configurations.
  The path to an INI file may also be specified via the `CM_INI` environment
  variable, in which case the filename matching rules above will not apply.
  Host and authentication parameters may be specified via the `CM_HOST`,
  `CM_USERNAME` and `CM_PASSWORD` environment variables; these options will
  take precedence over options present in the INI file.  An INI file is not
  required if these options are specified using environment variables.
'''

import sys
import os
import argparse
import re
import optparse
import ConfigParser
import time

import cm_api
from cm_api.api_client import ApiResource
from cm_api.endpoints import host_templates
from cm_api.endpoints import clusters
from cm_api.endpoints import hosts
from cm_api.endpoints import roles
from cm_api.endpoints import services

from functools import partial
from six.moves import configparser
from multiprocessing.pool import ThreadPool
from threading import Lock

try:
    import json
except ImportError:
    import simplejson as json

CM_CONFIG_FILES = [ os.path.abspath(sys.argv[0]).rstrip('.py') + '.ini',
                    os.path.expanduser(os.environ.get('ANSIBLE_CONFIG', "~/cm.ini")),
                    "/etc/ansible/cm.ini"
]

class CMInventory(object):

    def _empty_inventory(self):
        return {"_meta" : {"hostvars" : {}}}

    def __init__(self):
        ''' Main execution path '''

        self.config = ConfigParser.SafeConfigParser()
        if os.environ.get('CM_INI', ''):
            config_files = [os.environ['CM_INI']]
        else:
            config_files =  CM_CONFIG_FILES
        for config_file in config_files:
            if os.path.exists(config_file):
                self.config.read(config_file)
                break

        # Load up connections info based on config and then environment variables
        username = (self.config.get('auth', 'username') or
                    os.environ.get('CM_USERNAME', None))
        password = (self.config.get('auth', 'password') or
                   os.environ.get('CM_PASSWORD', None))
        host     = (self.config.get('auth', 'host') or
                    os.environ.get('CM_HOST', None))
        if self.config.has_option('auth', 'port'):
            port = self.config.get('auth', 'port')
        else:
            port = os.environ.get('CM_PORT', None)
        if self.config.has_option('auth', 'use_tls'):
            use_tls = self.config.get('auth', 'use_tls')
        else:
            use_tls = os.environ.get('CM_USETLS', False)
        if self.config.has_option('auth', 'version'):
            version = self.config.get('auth', 'version')
        else:
            version = os.environ.get('CM_VERSION', None)

        # Limit the clusters being scanned
        self.filter_clusters = os.environ.get('CM_CLUSTERS')
        if not self.filter_clusters and self.config.has_option('defaults', 'clusters'):
            self.filter_clusters = self.config.get('defaults', 'clusters')
        if self.filter_clusters:
            self.filter_clusters = [x.strip() for x in self.filter_clusters.split(',') if x.strip()]

        self.inv_lock = Lock()
        self.cm = ApiResource(host, port, username, password, use_tls)


    def _put_cache(self, name, value):
        '''
        Saves the value to cache with the name given.
        '''
        if self.config.has_option('defaults', 'cache_dir'):
            cache_dir = os.path.expanduser(self.config.get('defaults', 'cache_dir'))
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            cache_file = os.path.join(cache_dir, name)
            with open(cache_file, 'w') as cache:
                json.dump(value, cache)

    def _get_cache(self, name, default=None):
        '''
        Retrieves the value from cache for the given name.
        '''
        if self.config.has_option('defaults', 'cache_dir'):
            cache_dir = self.config.get('defaults', 'cache_dir')
            cache_file = os.path.expanduser( os.path.join(cache_dir, name) )
            print cache_file
            if os.path.exists(cache_file):
                print "here"
                if self.config.has_option('defaults', 'cache_max_age'):
                    cache_max_age = self.config.getint('defaults', 'cache_max_age')
                else:
                    cache_max_age = 0
                cache_stat = os.stat(cache_file)
                if (cache_stat.st_mtime + cache_max_age) >= time.time():
                    with open(cache_file) as cache:
                        return json.load(cache)
        return default

    def get_host(self, hostname):
        inv = self._get_cache(hostname, None)
        if inv is not None:
            return inv

        if inv is None:
            try:
                inv = hosts.get_host(self.cm, hostname)
            except ObjectNotFoundError:
                pass

        if inv is not None:
            self._put_cache(hostname, inv)
        return inv or {}

    def _add_host(self, inv, parent_group, host_name):
        '''
        Add the host to the parent group in the given inventory.
        '''
        with self.inv_lock:
            p_group = inv.setdefault(parent_group, [])

        if isinstance(p_group, dict):
            group_hosts = p_group.setdefault('hosts', [])
        else:
            group_hosts = p_group
        if host_name not in group_hosts:
            group_hosts.append(host_name)

    def _add_child(self, inv, parent_group, child_group):
        '''
        Add a child group to a parent group in the given inventory.
        '''
        if parent_group != 'all':
            with self.inv_lock:
                p_group = inv.setdefault(parent_group, {})

            if not isinstance(p_group, dict):
                with self.inv_lock:
                    inv[parent_group] = {'hosts': p_group}
                    p_group = inv[parent_group]
            group_children = p_group.setdefault('children', [])
            if child_group not in group_children:
                group_children.append(child_group)
        with self.inv_lock:
            inv.setdefault(child_group, [])

    def get_inventory(self, meta_hostvars=True, n_threads=5):
        '''
        Reads the inventory from cache or VMware API via pSphere.
        '''
        # Use different cache names for guests only vs. all hosts.
        cache_name = '__inventory_all__'

        inv = self._get_cache(cache_name, None)
        if inv is not None:
            print "Here"
            return inv


        def _build_host_inventory(hostRef,inv,meta_hostvars):
            host = hosts.get_host(self.cm, hostRef.hostId)
            #print host.hostname

            self._add_host(inv, 'all', host.hostname)
            if meta_hostvars:
                inv['_meta']['hostvars'][host.hostname] = host.to_json_dict(preserve_ro=True)
            self._put_cache(host.hostname, host.to_json_dict(preserve_ro=True))

            # Group by cluster
            if host.clusterRef:
                cluster = clusters.get_cluster(self.cm, host.clusterRef.clusterName)
                self._add_child(inv, 'all', cluster.displayName)
                self._add_host(inv, cluster.displayName, host.hostname)

                if host.roleRefs:
                    for roleRef in host.roleRefs:
                        role = roles.get_role(self.cm, roleRef.serviceName, roleRef.roleName, roleRef.clusterName)

                        # Group by service
                        service = services.get_service(self.cm, roleRef.serviceName, roleRef.clusterName)

                        # There is no way to ensure that service display name is unique across clusters
                        # The only simple and unique representation of the service that can be used
                        # is the concatination of the service name and the cluster's name
                        service_group = cluster.displayName + '-' + service.displayName
                        self._add_child(inv, 'all', service.type)
                        self._add_child(inv, service.type, service_group)
                        self._add_child(inv, cluster.displayName, service_group)
                        self._add_host(inv, service_group, host.hostname)

                        # Group by role, roles depend on services and clusters, so the only unique and
                        # simple representation of a Group is the concatination of the role type, service
                        # name and the cluster name
                        role_group = cluster.displayName + '-' + service.displayName + '-' + role.type
                        self._add_child(inv, 'all', role.type)
                        #self._add_child(inv, role.type, service_group)
                        #self._add_child(inv, service_group, role_group)
                        self._add_child(inv, role.type, role_group)
                        self._add_host(inv, role_group, host.hostname)

                        # Group by role Group
                        role_group = role.roleConfigGroupRef.roleConfigGroupName
                        self._add_child(inv, role.type, role_group)
                        self._add_host(inv, role_group, host.hostname)

                        # Group by role template
                        for template in host_templates.get_all_host_templates(self.cm, host.clusterRef.clusterName):
                            self._add_child(inv, 'all', template.name)
                            for group in template.roleConfigGroupRefs:
                                if role_group == group.roleConfigGroupName:
                                    self._add_child(inv, template.name, role_group)
                    else:
                        self._add_child(inv, 'all', 'no_role')
                        self._add_host(inv, 'no_role', host.hostname)

                # Group by Rack
                self._add_child(inv, 'all', host.rackId)
                self._add_host(inv, host.rackId, host.clusterRef.clusterName)
            else:
                cluster_group = "no_cluster"
                self._add_child(inv, 'all', cluster_group)
                self._add_host(inv, cluster_group, host.hostname)


        inv = {'all': {'hosts': []}}
        if meta_hostvars:
            inv['_meta'] = {'hostvars': {}}

        if self.filter_clusters:
            # Loop through clusters and find hosts:
            hosts_list = []
            for host in self.cm.get_all_hosts():
                if host.clusterRef:
                    if clusters.get_cluster(self.cm, host.clusterRef.clusterName).displayName  in self.filter_clusters:
                        hosts_list.append(host)
        else:
            # Get list of all hosts
            hosts_list =  self.cm.get_all_hosts()


        if n_threads == 1:
            for hostRef in hosts_list:
                _build_host_inventory(inv,hostRef,meta_hostvars)
        else:
            _partial_build_host_inventory = partial(_build_host_inventory, inv=inv,meta_hostvars=meta_hostvars)
            pool = ThreadPool(n_threads)
            if sys.version_info <= (2, 6):
                pool.map(_partial_build_host_inventory, hosts_list)
            else:
                pool.map_async(_partial_build_host_inventory, hosts_list).get(1 << 31)


        self._put_cache(cache_name, inv)
        return inv

def main():
    parser = optparse.OptionParser()

    parser = optparse.OptionParser()
    parser.add_option('--list', action='store_true', dest='list',
                      default=False, help='Output inventory groups and hosts')
    parser.add_option('--host', dest='host', default=None, metavar='HOST',
                      help='Output variables only for the given hostname')
    parser.add_option('--threads', type="int", dest='n_threads',
                      default=5, help='Number of threads to use.')
    # Additional options for use when running the script standalone, but never
    # used by Ansible.
    parser.add_option('--pretty', action='store_true', dest='pretty',
                      default=False, help='Output nicely-formatted JSON')
    parser.add_option('--no-meta-hostvars', action='store_false',
                      dest='meta_hostvars', default=True,
                      help='Exclude [\'_meta\'][\'hostvars\'] with --list')

    options, args = parser.parse_args()

    cm_inventory = CMInventory()

    if options.host is not None:
        inventory = cm_inventory.get_host(options.host)
    else:
        inventory = cm_inventory.get_inventory(options.meta_hostvars, options.n_threads)

    json_kwargs = {}
    if options.pretty:
        json_kwargs.update({'indent': 4, 'sort_keys': True})
    json.dump(inventory, sys.stdout, **json_kwargs)


if __name__ == '__main__':
    main()