#!/usr/bin/env python
# encoding: utf-8

import os
import re
import stat 
import json
import os.path as osp
import socket
from impala._thrift_api import TTransportException
from .hdfsbase import _check_required_if,_check_required_one_of_if,_check_invalid_if,kinit,kdestroy

try:
    import impala.dbapi as hs2
    has_lib_hs2 = True
except ImportError:
    has_lib_hs2 = False

def hs2_argument_spec():
    return dict(
        # Specify the authentication mechanism:
        #   NOSASL for unsecured Impala. 
        #   PLAIN for unsecured Hive (because Hive requires the SASL transport).
        #   GSSAPI for Kerberos
        #   LDAP for Kerberos with LDAP.
        authentication = dict(choices=['NOSASL','PLAIN','GSSAPI','LDAP'], default='NOSASL'),
        # LDAP user, if applicable.
        user = dict(required=False,default=None),
        # KERBEROS principal when using GSSAPI authentication
        principal = dict(required=False,default=None),
        # LDAP or Kerberos password, if applicable.
        password = dict(required=False,default=None, no_log=True),
        keytab= dict(required=False,default=None, no_log=True),
        # Authenticate to a particular `impalad` or hs2 service principal.
        kerberos_service_name = dict(required=False,default='hive', no_log=True),
        # The hostname for HS2. For Impala, this can be any of the impalads.
        host= dict(required=True,default=None, type='str'),
        # The port number for HS2. The Impala default is 21050. The Hive port is likely different.
        port= dict(required=False,default=10000, type='int'),
        # For secure connections whether to verify or not the server certificate
        verify= dict(required=False, default=False, type='bool'),
        # For secure connections the server certificate file(trust store) to trust.
        truststore= dict(required=False,default=None, no_log=True),
        # Connection timeout in seconds. Default is no timeout.
        timeout= dict(required=False, default=None, type='float'),
    )

def hs2_required_together():
    return []

def hs2_mutually_exclusive():
    return [['password', 'keytab'],['user', 'principal']]

def hs2_required_one_of_if():
	return [ ('authentication', 'GSSAPI', ['password','keytab']) ]

def hs2_required_if():
	return [ ('authentication', 'PLAIN', ['user','password']),('authentication', 'LDAP', ['user','password']),('authentication', 'GSSAPI', ['principal']) ]

def hs2_invalid_if():
    return [ ('verify', False, ['truststore']),('authentication', 'GSSAPI', ['user','password'])  ]

class NotSupportedError(Exception):
    pass

class HS2AnsibleModule(object):

    def __init__(self, module, bypass_checks=False,required_if=None,required_one_of_if=None,invalid_if=None):
        self.module = module

        if not has_lib_hs2:
            self.module.fail_json(msg="python library impyla required: pip install impyla")

        authentication = self.module.params.get('authentication')

        self.file_cleanup_onfail = []
        self.file_restore_onfail = []
        self.local_file_cleanup_onfail = []
        self.local_file_restore_onfail = []

        self.hs2_required_if = hs2_required_if()
        self.hs2_required_one_of_if = hs2_required_one_of_if()
        self.hs2_invalid_if = hs2_invalid_if()

        if required_if is not None:
             self.hs2_required_if.extend(required_if)
        if required_one_of_if is not None:
             self.hs2_required_one_of_if.extend(required_one_of_if)
        if invalid_if is not None:
             self.hs2_invalid_if.extend(invalid_if)

        # Need to be performed here since ansible does not provide yet a way to check
        # required one of with if
        if not bypass_checks:
            _check_required_if(module,self.hs2_required_if)
            _check_required_one_of_if(module,self.hs2_required_one_of_if)
            _check_invalid_if(module,self.hs2_invalid_if)

        # Request a TGT if the authentication uses kerberos
        if authentication == 'GSSAPI':
            principal = module.params['principal']
            password = module.params['password']
            keytab = module.params['keytab']
            try:
               kinit(principal, password, keytab)
            except Exception, e:
               self.hdfs_fail_json(msg="Kerberos authentication failed: %s." % str(e))

        ## Get the client
        self.connnection = self.get_connnection()
        ## Create a Cursor
        self.cursor = self.connnection.cursor()

    def __del__(self):
        self.cursor.close()
        self.connnection.close()
        authentication = self.module.params.get('authentication')
    	if authentication == 'GSSAPI':
            try:
    	       kdestroy()
            except Exception, e:
               self.hdfs_fail_json(msg="failed to clean kerberos TGT: %s." % str(e))

    def get_connnection(self):
        """Load HS2 client.

        Further calls to this method for the same alias will return the same client
        instance (in particular, any option changes to this alias will not be taken
        into account).

        """
        params                = self.module.params
        auth_mechanism        = params.get('authentication')
        user                  = params.get('user', None)
        password              = params.get('password', None)
        kerberos_service_name = params.get('kerberos_service_name', None)
        host                  = params.get('host')
        port                  = params.get('port')
        use_ssl               = params.get('verify', None)
        ca_cert               = params.get('truststore', None)
        timeout               = params.get('timeout', None)

        try:
            connnection = hs2.connect( host=host, port=port, auth_mechanism=auth_mechanism, user=user, password=password,
        	                       kerberos_service_name=kerberos_service_name, use_ssl=use_ssl, ca_cert=ca_cert, timeout=timeout)
        except socket.error, e:
        	self.module.fail_json(msg="Failed to open socket, %s." % str(e))
        except TTransportException, e:
            self.module.fail_json(msg="Failed to open transport, %s." % str(e))
        except Exception, e:
            self.module.fail_json(msg="Unknown Exception, %s." % str(e))
        return connnection

    def db_exists(self, db_name):
    	exists = self.cursor.database_exists(db_name)
    	return exists

    def set_db_owner(self, db, otype, owner):
        query = "ALTER DATABASE %s SET OWNER %s `%s`" % ( db, otype, owner)
        self.cursor.execute(query)
        return True

    def set_db_location(self, db, location):
        query = "ALTER DATABASE %s SET OWNER %s `%s`" % ( db, otype, owner)
        self.cursor.execute(query)
        return True

    def get_db_info(self, db):
        query = "DESCRIBE DATABASE EXTENDED " + db
        self.cursor.execute(query)
        db_info = self.cursor.fetchone()
        return   {
                 'name': db_info[0],
                 'comment' : db_info[1],
                 'location' : db_info[2],
                 'owner_name' : db_info[3],
                 'owner_type' : db_info[4],
                 'properties' : { pty.split('=')[0].strip() : pty.split('=')[1].strip() for pty in db_info[5].replace("{","").replace("}","").split(',') } if db_info[5] else {},
                 }       

    def set_bd_properties(self, db_name, properties):
        query = "ALTER DATABASE " + db_name + " SET DBPROPERTIES (" + ','.join( str( "'" + prop + "'" + "=" + "'" + properties[prop] + "'") for prop in properties) + ")"
        self.cursor.execute(query)
        return True


    def db_delete(self, db):
        if self.db_exists(db):
            query = "DROP DATABASE %s" % db
            self.cursor.execute(query)
            return True
        else:
            return False

    def db_create(self, db, comment=None, location=None, properties=None, otype="USER", owner=None):
        if not self.db_exists( db):
            query_fragments = ['CREATE DATABASE %s' % db]
            if comment:
                query_fragments.append('COMMENT "%s"' % comment)
            if location:
                query_fragments.append('LOCATION "%s"' % location)
            if properties:
                query_fragments.append("SET DBPROPERTIES (" + ','.join( str( "'" + prop + "'" + "=" + "'" + properties[prop] + "'") for prop in properties) + ")")
            query = ' '.join(query_fragments)
            self.cursor.execute(query)

            if owner:
                self.set_db_owner(db,otype,owner)

            return True
        else:
            changed = False
            db_info = self.get_db_info(db)
            if (location and location != db_info['location']):
                raise NotSupportedError(
                    'Changing database location is not supported. '
                    'Current location: %s' % db_info['location']
                )
            elif comment and comment != db_info['comment']:
                raise NotSupportedError(
                    'Changing comment is not supported. '
                    'Current comment: %s' % db_info['comment']
                )
            elif properties:
                for key in properties:
                    if key in db_info['properties']:
                        if db_info['properties'][key] != properties[key]:
                            self.set_bd_properties(db,properties)
                            changed = True
                            break
                    else:
                        self.set_bd_properties(db,properties)
                        changed = True
                        break

            elif (owner and owner != db_info['owner_name']) or (otype and otype != db_info['owner_type']):
                return self.set_db_owner(db, otype ,owner)
                changed = True
            
            return changed

    def db_matches(self, comment=None, location=None, properties=None, otype="USER", owner=None):
        if not self.db_exists(db):
            return False
        else:
            db_info = self.get_db_info(db)
            if location and location != db_info['location']:
                return False
            elif comment and comment != db_info['comment']:
                return False
            elif owner and owner != db_info['owner_name']:
                return False
            elif otype and otype != db_info['owner_type']:
                return False
            elif properties:
                for key in properties:
                    if key in db_info['properties']:
                        if db_info['properties'][key] != properties[key]:
                            return False
                    else:
                        return False
            else:
                return True

    def db_set(self, db):
        self.cursor.execute("USE %s" % db)
        return True

    #################################################################################################################
    #                                     Authorization Functions
    #################################################################################################################

    def drop_role(self, role):
        query = "DROP ROLE %s" % role
        self.cursor.execute(query)
        return True

    def create_role(self, role):
        query = "CREATE ROLE %s" % role
        self.cursor.execute(query)
        return True

    # In Sentry roles can only be granted to GROUPS
    def grant_role(self, role, group):
        query = "GRANT ROLE %s TO GROUP %s" % (role,group)
        self.cursor.execute(query)
        return True

    def revoke_role(self, role, group):
        query = "REVOKE ROLE %s FROM GROUP %s" % (role,group)
        self.cursor.execute(query)
        return True

    def grant_previlege(self, role, previlege, obj, obj_type, revoke=False, grant_option=False):
        switch_database = None
        if revoke == False:
          query_fragments = ['GRANT %s' % previlege]
        else:
          query_fragments = ['REVOKE %s' % previlege]

        if obj_type == 'column':
          try:
              database, table, column = obj.split('.')
          except:
              raise Error('Illegal column format: "%s".' % obj)
          switch_database = database
          query_fragments.append('(%s) ON TABLE %s' % (column, table))
        elif obj_type == 'table':
          try:
              database, table = obj.split('.')
          except:
              raise Error('Illegal table format: "%s".' % obj)
          switch_database = database
          query_fragments.append(' ON TABLE %s' % table)
        elif obj_type == 'database':
          query_fragments.append(' ON DATABASE %s' % obj)
        elif obj_type == 'server':
          query_fragments.append(' ON SERVER %s' % obj)
        elif obj_type == 'uri':
          query_fragments.append(' ON URI "%s"' % obj)
        else:
          raise Error('Illegal grant object type format: "%s".' % obj_type)
        
        if revoke == False:
          query_fragments.append(' TO ROLE %s' % role)
        else:
          query_fragments.append(' FROM ROLE %s' % role)

        if grant_option == True:
          query_fragments.append(' WITH GRANT OPTION')

        query = ''.join(query_fragments)

        # need to switch database before setting priveleges on Table
        if switch_database:
          self.db_set(switch_database)

        self.cursor.execute(query)
        return True

    def get_roles(self):
        query = "SHOW ROLES"
        self.cursor.execute(query)
        return [t[0] for t in self.cursor.fetchall()]

    def get_role_privs(self, role, obj=None, obj_type=None):
        query_fragments = ['SHOW GRANT ROLE %s' % role]
        if (obj_type != None) & (obj != None):
            query_fragments.append('ON %s %s' % (obj_type, obj))
        query = ' '.join(query_fragments)
        self.cursor.execute(query)
        privs = []
        for t in self.cursor.fetchall():
            privs.append( {
                     'database': t[0] if t[0] else "",
                     'table': t[1] if t[1] else "",
                     'partition': t[2] if t[2] else "",
                     'column': t[3] if t[3] else "",
                     'principal_name': t[4] if t[4] else "",
                     'principal_type': t[5] if t[5] else "",
                     'previlege': t[6] if t[6] else "",
                     'grant_option': t[7] if t[7] else "",
                     'grant_time': t[8] if t[8] else "",
                     'grantor': t[9] if t[9] else "",
                  }
                )
        return privs

    def get_group_roles(self, group):
        query = "SHOW ROLE GRANT GROUP `%s`" % group
        self.cursor.execute(query)
        return [t[0] for t in self.cursor.fetchall()]
