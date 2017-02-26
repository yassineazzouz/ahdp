#!/usr/bin/python
# -*- coding: utf-8 -*-
## (c) 2016, Yassine Azzouz <yassine.azzouz@gmail.com>

DOCUMENTATION = '''
---
module: hdfsacl
short_description: Sets and retrieves file ACL information on hdfs.
extends_documentation_fragment: hdfs
description:
    - Sets and retrieves file ACL information on hdfs.
version_added: "1.9"
requirements: [ pywhdfs ]
author: "Yassine Azzouz"
options:
  path:
    required: true
    default: null
    description:
      - The full path of the file or object.
    aliases: ['name']
  state:
    required: false
    default: query
    choices: [ 'query', 'present', 'absent' ]
    description:
      - defines whether the ACL should be present or not.  The C(query) state gets the current acl without changing it, for use in register operations.
      - if state is query, entries need to be null
      - if state is absent, then we remove acls, entries can be null to say remove everything. otherwise if provided the entity need to be provided and permissions need to be null in all acl entries
      - if state is present, then we add/overwrite acls. You can use overwrite to replace existing acls but you must include entries for user, group, and others for compatibility with permission bits.
  entries:
    required: false
    default: null
    description:
      - Defines a list of acl entries, An ACL entry have an optional default field to specify, if it is a default acl or not, a type (user, group, mask, or other), an optional name called entity (referring to a specific user or group) and a set of permissions (any combination of read, write and execute). A single acl entry is a string having three/or four identifiers separated by a colon default, type, entity, permissions.
    aliases: ['aclspec']
  recursive:
    required: false
    default: no
    choices: [ 'yes', 'no' ]
    description:
      - Recursively sets the specified ACL. Incompatible with C(state=query).
  overwrite:
    required: false
    default: no
    choices: [ 'yes', 'no' ]
    description:
      - If used acls will be completely replaced. Fully replaces ACL of files and directories, discarding all existing entries.
      - Note that default acls are not overwritten by the overwrite parameter, you can change default acls either delelting all acls or by using the scope default in acl entries with state absent or prensent to modify/delete individual default acls.
notes:
    - The "acl" module requires that hdfs acls are enabled on your cluster using dfs.namenode.acls.enabled.
    - Note when using this module do not use the folded block scalar ">" after the module name like "hdfsacl >" because the list parameters will be interpreted as string argument.
'''

EXAMPLES = '''
# List specific file or directory acls
- hdfsacl: 
    path: "/user/yassine" 
    state: "query" 
    url: "http://localhost:50070"
  register: acl_info

# Add file or directory acls
- hdfsacl:
    state: 'present'
    entries:
        - 'default:user::rwx'
        - 'default:group::rwx'
        - 'user:yassine:rwx'
        - 'group:yassine:rwx'
    path: "/user/yassine"
    url: "http://localhost:50070"

# Set overwrite directory acls recursively
- hdfsacl:
    state: 'present'
    entries: :
        - 'user::r--'
        - 'group::r--'
        - 'other::r--'
        - 'mask::r--'
    overwrite: True
    recursive: True
    path: "/user/yassine"
    url: "http://localhost:50070"

# Remove some acls recursively
- hdfsacl:
    state: 'absent'
    entries:
        - 'default:user::'
        - 'user:yassine:'
    recursive: True
    path: "/user/yassine"
    url: "http://localhost:50070"

# Remove all file/directory acls
- hdfsacl:
    state: 'absent'
    recursive: True
    path: "/user/yassine"
    url: "http://localhost:50070"
'''

RETURN = '''
acls:
    description: Current acl on provided path (after changes, if any)
    returned: success
    type: list
    sample: [ "user::rwx", "group::rwx", "other::rwx" ]
'''

import json

from ahdp.module_utils.hdfsbase import *
from ansible.module_utils.basic import AnsibleModule

def invalid_if():
    return [ ('state', 'query', ['recursive','entries','overwrite']),('state', 'absent', ['overwrite']) ]

def hdfs_required_if():
    return [ ('state', 'present', ['entries'])  ]

def main():

    argument_spec = hdfs_argument_spec()

    argument_spec.update( dict(
            path=dict(required=True, aliases=['name'], type='str'),
            entries=dict(required=False, aliases=['aclspec'], type='list'),
            state=dict(
                required=False,
                default='query',
                choices=['query', 'present', 'absent'],
                type='str'
            ),
            overwrite=dict(required=False, type='bool', default=False),
            recursive=dict(required=False, type='bool', default=False),
        )
    )

    required_together = hdfs_required_together()
    mutually_exclusive = hdfs_mutually_exclusive()
    required_if = hdfs_required_if()

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=required_together,
        mutually_exclusive=mutually_exclusive
#        required_if=required_if
    )

    hdfs = HDFSAnsibleModule(module,invalid_if=invalid_if())


    params    = module.params
    hdfs_path    = params['path']
    entries      = params['entries']
    state        = params['state']
    overwrite    = params['overwrite']
    recursive    = params['recursive']

    if entries is not None:
        hdfs.validate_acl_entries(entries=entries)

    # Fail if the does not exist
    status = hdfs.hdfs_status(hdfs_path,strict=False)
    if status is None:
        hdfs.hdfs_fail_json(msg='Destination hdfs path %r does not exist.' % hdfs_path, changed=False)

    # Start the check
    # if state is query, entries need to be null
    # if state is absent, then we remove acls, entries can be null to say remove everything, 
    #    otherwise if provided the entity need to be provided and permissions need to be null in all acl entries
    # if state is present, then we add/overwrite acls. You can use overwrite to replace existing acls but 
    #    you must include entries for user, group, and others for compatibility with permission bits.
    # Note that default acls are not overwritten by the overwrite parameter, you can change default acls either
    # delelting all acls or by using the scope default in acl entries with state absent or prensent to modify/delete
    # individual default acls.

    changed = False

    if state == 'present':
        # if state present all entries need to have permissions
        for entry in entries:
            if (entry[0] == 'default' and entry[3] == "") or (entry[0] != 'default' and entry[2] == ""):
                 hdfs.hdfs_fail_json(msg='Invalid acl to be set %r null permission.' % entry, changed=False)

        if overwrite:
            # will overwrite all existing acls
            changed = hdfs.hdfs_setacls(path=hdfs_path, entries=entries, recursive=recursive, strict=False)
        else:
            # add acls
            changed = hdfs.hdfs_addacls(path=hdfs_path, entries=entries, recursive=recursive, strict=False)

    elif state == 'absent':
        if entries is None:
            # Remove all acls
            changed = hdfs.hdfs_remove_allacls(path=hdfs_path, recursive=recursive, strict=False)
        else:
            # Remove specified entries
            changed = hdfs.hdfs_remove_acls(path=hdfs_path, entries=entries, recursive=recursive, strict=False)
    elif state == 'query':
        # Nothing to do
        changed = False
    else:
        hdfs.hdfs_fail_json(changed=False, msg='unexpected position reached')

    acls = hdfs.hdfs_getacls(path=hdfs_path,strict=False)
    module.exit_json(changed=changed, path=hdfs_path, acls=acls)

if __name__ == '__main__':
    main()
