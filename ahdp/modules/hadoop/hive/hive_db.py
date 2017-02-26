#!/usr/bin/python
# -*- coding: utf-8 -*-
## (c) 2016, Yassine Azzouz <yassine.azzouz@gmail.com>

DOCUMENTATION = '''
---
module: hive_db
short_description: Add or remove HIVE or Impala databases from a remote hive server 2 or impala host.
extends_documentation_fragment: hs2
description:
   - Add or remove Hive or impala databases from a remote host.
version_added: "1.9"
author: "Yassine Azzouz"
options:
  db:
    description:
      - name of the database to add or remove
    required: true
    default: null
  location:
    description:
      - The DB location in HDFS.
    required: false
    default: null
  comment:
    description:
      - A description or comment on the DB.
    required: false
    default: null
  owner:
    description:
      - The USER or ROLE owner of the database.
    required: false
    default: null
  owner_type:
    description:
      - The type of the owner, required with owner option.
    required: false
    default: null
    choices: [ "USER", "ROLE" ]
  properties:
    description:
      - Properties to associate to the database.
    required: false
    default: null
  state:
    description:
      - The type of operation to perform on the database
    required: false
    default: present
    choices: [ "query", "present", "absent" ]
requirements: [ impyla ]
'''

EXAMPLES = '''
# Create a database
- hive_db:
   authentication: "PLAIN"
   user: "hive"
   password: "{{hive_ldap_password}}"
   host: "localhost"
   port: 10000
   db: "ansible"
   owner: "ansible"
   properties:
      db.owner: "ansible"
      db.purpse: "test"
   state: "present"

# Query database attributes
- hive_db:
    authentication: "PLAIN"
    user: "hive"
    password: "{{hive_ldap_password}}"
    host: "localhost"
    port: 10000
    db: "ansible"
    state: "query"
    register: db_info
- debug: msg="{{db_info}}"

# Delete a Database
- hive_db:
    authentication: "PLAIN"
    user: "hive"
    password: "{{hive_ldap_password}}"
    host: "localhost"
    port: 10000
    db: "ansible"
    state: "absent"
'''

try:
    import impala
    from impala.error import *
except ImportError:
    impyla_found = False
else:
    impyla_found = True

# import module snippets
from ahdp.module_utils.hs2base import *
from ansible.module_utils.basic import *

def main():

    if not impyla_found:
        module.fail_json(msg="the python impyla module is required")

    argument_spec = hs2_argument_spec()

    argument_spec.update( dict(
            db=dict(required=True, aliases=['name']),
            location=dict(required=False,default=None),
            comment=dict(required=False,default=None),
            owner=dict(required=False,default=None),
            owner_type=dict(default="USER", choices=['USER', 'ROLE']),
            properties=dict(required=False, aliases=['dbproperties'], type='dict'),
            state=dict(
                required=False,
                default='query',
                choices=['query', 'present', 'absent'],
                type='str'
            ),
        )
    )

    required_together = hs2_required_together()
    mutually_exclusive = hs2_mutually_exclusive()
    required_if = hs2_required_if()

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=required_together,
        mutually_exclusive=mutually_exclusive,
        supports_check_mode = True
    )


    hs2 = HS2AnsibleModule(module)

    params    = module.params
    db = params["db"]
    location = params["location"]
    owner = params["owner"]
    comment = params["comment"]
    owner_type = params["owner_type"]
    properties = params["properties"]
    state = params["state"]
    changed = False

    try:
        if module.check_mode:
            if state == "absent":
                changed = not hs2.db_exists(db)
            elif state == "present":
                changed = not hs2.db_matches( db=db, comment=comment, location=location, 
                               properties=properties, otype=owner_type, owner=owner )
            module.exit_json(changed=changed,db=db)

        if state == "absent":
            try:
                changed = hs2.db_delete(db)
            except (DatabaseError,RPCError), e:
                #e = module.get_exception()
                module.fail_json(msg=str(e))

        elif state == "present":
            try:
                changed = hs2.db_create(db=db, comment=comment, location=location, 
                               properties=properties, otype=owner_type, owner=owner)
            except (DatabaseError,RPCError), e:
                #e = module.get_exception()
                module.fail_json(msg=str(e))
        elif state == "query":
               if hs2.db_exists(db):
                  db_info = hs2.get_db_info(db)
                  module.exit_json(changed=False, db=db, stats=db_info)
               else:
                  module.exit_json(changed=False, db=db)
    except NotSupportedError, e:
        #e = module.get_exception()
        module.fail_json(msg=str(e))
    except Exception, e:
        #e = module.get_exception()
        module.fail_json(msg="Database query failed: %s" % e)

    module.exit_json(changed=changed, db=db)

if __name__ == '__main__':
    main()
