#!/usr/bin/python
# -*- coding: utf-8 -*-
## (c) 2016, Yassine Azzouz <yassine.azzouz@gmail.com>

DOCUMENTATION = """
---
module: hive_privs
version_added: "1.9"
short_description: Manage privileges on HIVE database objects.
extends_documentation_fragment: hs2
description:
  - Grant or revoke privileges on HIVE database objects.
  - This module support connection to a Hive server 2 or impala deamons
    and uses their thrift apis to perform previlege operations.
author: "Yassine Azzouz"
options:
  obj:
    description:
      - The object name to target, corresponding to the type specified by
        C(objtype).
    required: yes
  state:
    description:
      - If C(present), the specified privileges are granted, if C(absent) they
        are revoked.
    required: no
    default: present
    choices: [present, absent]
  privilege:
    description:
      - The type of previlege to grant or revoke.
    required: no
    choices: [select, insert, all]
  objtype:
    description:
      - Type of the object to set privileges on.
    required: no
    choices: [table, server, column, database,
              uri, group]
  role:
    description:
      - The role name to set permissions for.
    required: yes
  grant_option:
    description:
      - Whether C(role) may grant/revoke the specified privileges/group
        memberships to others.
      - Set to C(no) to revoke GRANT OPTION, leave unspecified to
        make no changes.
      - I(grant_option) only has an effect if I(state) is C(present).
      - 'Alias: I(admin_option)'
    required: no
    choices: ['yes', 'no']
requirements: [impyla,thrift_sasl]
"""

EXAMPLES = """
# Create a role named test
- hive_privs:
   authentication: "PLAIN"
   user: "hive"
   password: "{{hive_ldap_password}}"
   host: "localhost"
   port: 10000
   role: "test"
   state: "present"

# Assign the ROLE test to the group test
- hive_privs:
   authentication: "PLAIN"
   user: "hive"
   password: "{{hive_ldap_password}}"
   host: "localhost"
   port: 10000
   role: "test"
   objtype: "group"
   obj: "test"
   state: "present"

# Grant the role test sect access on database db
- hive_privs:
   authentication: "PLAIN"
   user: "hive"
   password: "{{hive_ldap_password}}"
   host: "localhost"
   port: 10000
   role: "test"
   objtype: "database"
   obj: "db"
   privilege: "select"
   state: "present"

# grant the role test all previleges on table tb
- hive_privs:
   authentication: "PLAIN"
   user: "hive"
   password: "{{hive_ldap_password}}"
   host: "localhost"
   port: 10000
   role: "test"
   objtype: "table"
   obj: "db.tb"
   privilege: "all"
   state: "present"

# grant the role test all previleges on column id of table tb2
- hive_privs:
   authentication: "PLAIN"
   user: "hive"
   password: "{{hive_ldap_password}}"
   host: "localhost"
   port: 10000
   role: "test"
   objtype: "column"
   obj: "db.tb2.id"
   privilege: "select"
   state: "present"

# grant role test all previleges on uri
- hive_privs:
   authentication: "PLAIN"
   user: "hive"
   password: "{{hive_ldap_password}}"
   host: "localhost"
   port: 10000
   role: "test"
   objtype: "uri"
   obj: "hdfs:///hive/metastore/db/tb"
   privilege: "all"
   grant_option: True
   state: "present"

# REVOKE previleges on table tb for role test
- hive_privs:
   authentication: "PLAIN"
   user: "hive"
   password: "{{hive_ldap_password}}"
   host: "localhost"
   port: 10000
   role: "test"
   objtype: "table"
   obj: "db.tb"
   privilege: "all"
   state: "absent"
"""

try:
    import impala
    from impala.error import *
except ImportError:
    impyla_found = False
else:
    impyla_found = True

# import module snippets
from ansible.module_utils.basic import *
from ahdp.module_utils.hs2base import *

def _invalid_if():
    return [ ('objtype', 'group', ['privilege','grant_option'])]

def _required_if():
    return [ 
             ('objtype', 'server', ['privilege']),
             ('objtype', 'table', ['privilege']),
             ('objtype', 'database', ['privilege']),
             ('objtype', 'column', ['privilege']),
             ('objtype', 'uri', ['privilege'])
           ]

def _required_together():
    return [ ['objtype', 'obj']]

def main():

    if not impyla_found:
        module.fail_json(msg="the python impyla module is required")

    argument_spec = hs2_argument_spec()

    argument_spec.update( dict(
            state=dict(default='present', choices=['present', 'absent']),
            privilege=dict(required=False, aliases=['priv'], choices=['select','insert','all'],default=None),
            objtype=dict(required=False,
                         default=None,
                         choices=['server',
                                  'table',
                                  'database',
                                  'column',
                                  'uri',
                                  'group']),
            obj=dict(required=False,default=None),
            role=dict(required=True),
            grant_option=dict(required=False, type='bool', aliases=['admin_option'],default=None)
        )
    )

    required_together = hs2_required_together()
    mutually_exclusive = hs2_mutually_exclusive()
    required_together.extend(_required_together())

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=required_together,
        mutually_exclusive=mutually_exclusive,
        supports_check_mode = True
    )


    hs2 = HS2AnsibleModule(module,required_if=_required_if(),invalid_if=_invalid_if())


    params       = module.params
    state        = params["state"]
    privilege    = params["privilege"]
    objtype      = params["objtype"]
    obj          = params["obj"]
    role         = params["role"]
    grant_option = params["grant_option"]
    changed = False

    if not objtype:
      # Create role
      if state == 'present':
        if role not in hs2.get_roles():
          hs2.create_role(role)
          changed = True
      else:
        if role in hs2.get_roles():
          hs2.drop_role(role)
          changed = True       
    elif objtype == 'group':
      # assign role to group
      if state == 'present':
        if role not in hs2.get_group_roles(obj):
          hs2.grant_role(role, obj)
          changed = True
      else:
        if role in hs2.get_group_roles(obj):
          hs2.revoke_role(role, obj)
          changed = True
    else:
      # Assign previlege to role
      privs_before = hs2.get_role_privs(role)
      revoke = False if state == 'present' else True
      hs2.grant_previlege(role=role, previlege=privilege, obj=obj, obj_type=objtype, revoke=revoke, grant_option=grant_option)
      privs_after = hs2.get_role_privs(role)
      for new_priv in privs_after:
        if new_priv not in privs_before:
          changed = True
      for old_priv in privs_before:
        if old_priv not in privs_after:
          changed = True

    module.exit_json(changed=changed)

if __name__ == '__main__':
    main()
