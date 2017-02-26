#!/usr/bin/python
# -*- coding: utf-8 -*-
## (c) 2016, Yassine Azzouz <yassine.azzouz@gmail.com>

DOCUMENTATION = '''
---
module: hdfs_snapshot
short_description: create/delete/rename and list HDFS snapshots.
extends_documentation_fragment: hdfs
description:
     - Performs hdfs hdfs snapshots operations.
version_added: "1.9"
requirements: [ pywhdfs ]
author: "Yassine Azzouz"
options:
  path:
    required: true
    default: None
    description:
      - The full path of the directory to perform a snapshot on, the directory need to be snapshottable.
  rename:
    required: false
    default: None
    description:
      - The new name of the snapshot, valid only with C(operation) C(rename)
  name:
    required: false
    default: None
    description:
      - Name of the snapshot to perform the operation on.
  operation:
    required: false
    default: list
    choices: [ 'create', 'delete', 'rename', 'list' ]
    description:
      - defines which operation you want to perform.
        C(create) create a hdfs snapshot for the provided path.
        C(delete) deletes the snapshot with C(name) for C(path)
        C(rename) rename the snapshot with C(name) to C(rename)
        C(list) list all snapshots for C(path).
'''

EXAMPLES = '''
- name: List all snapshots
  hdfs_snapshot:
    authentication: "kerberos"
    principal: "hdfs@HADOOP.LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    operation: "list"
    path: "/user/yassine"
    urls: "{{namenodes_urls}}"
  register: snapshots
- name: Create a snapshot
  hdfs_snapshot:
    authentication: "kerberos"
    principal: "hdfs@HADOOP.LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    operation: "create"
    name: "s1"
    path: "/user/yassine"
    urls: "{{namenodes_urls}}"
  register: snapshots
- name: Rename the created snapshot
  hdfs_snapshot:
    authentication: "kerberos"
    principal: "hdfs@HADOOP.LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    operation: "rename"
    name: "{{snapshots.snapshot}}"
    rename: "s2"
    path: "/user/yassine"
    urls: "{{namenodes_urls}}"
  register: ss
- name: List all snapshots
  hdfs_snapshot:
    authentication: "kerberos"
    principal: "hdfs@HADOOP.LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    operation: "list"
    path: "/user/yassine"
    urls: "{{namenodes_urls}}"
  register: ss
- name: Delete all snapshots
  hdfs_snapshot:
    authentication: "kerberos"
    principal: "hdfs@HADOOP.LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    operation: "delete"
    name: "{{item}}"
    path: "/user/yassine"
    urls: "{{namenodes_urls}}"
  with_items: ss.snapshot
'''

# import module snippets
from ansible.module_utils.basic import AnsibleModule
from ahdp.module_utils.hdfsbase import *

def required_if():
  return [ ('operation', 'delete', ['name']),('operation', 'rename', ['name','rename']) ]

def invalid_if():
    return [ ('operation', 'create', ['rename']),('operation', 'delete', ['rename']),('operation', 'list', ['name','rename']) ]

def main():

    argument_spec = hdfs_argument_spec()

    argument_spec.update( dict(
            path = dict(required=True),
            rename = dict(required=False, default=None),
            name = dict(required=False, default=None),
            operation = dict(required=False, default='list', choices=[ 'list', 'rename', 'delete', 'create' ], type='str'),
        )
    )

    required_together = hdfs_required_together()
    mutually_exclusive = hdfs_mutually_exclusive()

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=required_together,
        mutually_exclusive=mutually_exclusive
    )

    hdfs = HDFSAnsibleModule(
        module=module,
        invalid_if=invalid_if(),
        required_if=required_if()
    )

    params    = module.params
    path      = params['path']
    rename    = params['rename']
    name      = params['name']
    operation = params['operation']

    if not hdfs.hdfs_exist(path):
        hdfs.hdfs_fail_json(msg='Destination hdfs path %r is not a valid snapshottable directory or is not accessible!' % path, changed=False)

    if operation == 'create':
      res = hdfs.hdfs_create_snapshot(path=path,name=name)
      module.exit_json(changed=True, path=path, snapshot=osp.basename(res))
    elif operation == 'delete':
      hdfs.hdfs_delete_snapshot(path=path,name=name)
      module.exit_json(changed=True, path=path, snapshot=name)
    elif operation == 'rename':
      hdfs.hdfs_rename_snapshot(path=path,old_name=name,new_name=rename)
      module.exit_json(changed=True, path=path, snapshot=rename)
    else:
      snapshots=hdfs.hdfs_list_snapshots(path=path)
      module.exit_json(changed=True, path=path, snapshot=snapshots)

    hdfs.hdfs_fail_json(path=path, msg='unexpected position reached')

if __name__ == '__main__':
   main()
