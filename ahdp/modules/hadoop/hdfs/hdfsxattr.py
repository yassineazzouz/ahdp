#!/usr/bin/python
# -*- coding: utf-8 -*-
## (c) 2016, Yassine Azzouz <yassine.azzouz@gmail.com>

DOCUMENTATION = '''
---
module: hdfsxattr
short_description: set/retrieve hdfs extended attributes
extends_documentation_fragment: hdfs
description:
     - Manages hdfs user defined extended attributes, requires that they are enabled
       on the target cluster using the dfs.namenode.xattrs.enabled option.
version_added: "1.9"
requirements: [ pywhdfs ]
author: "Yassine Azzouz"
options:
  name:
    required: true
    default: None
    aliases: ['path']
    description:
      - The full path of the file/object to get the facts of
  key:
    required: false
    default: None
    description:
      - The name of a specific Extended attribute key to set/retrieve
  value:
    required: false
    default: None
    description:
      - The value to set the named name/key to, it automatically sets the C(state) to 'set'
  state:
    required: false
    default: get
    choices: [ 'read', 'present', 'all', 'keys', 'absent' ]
    description:
      - defines which state you want to do.
        C(read) retrieves the current value for a C(key) (default)
        C(present) sets C(name) to C(value), default if value is set
        C(all) dumps all data
        C(keys) retrieves all keys
        C(absent) deletes the key
author: "Yassine Azzouz (yassine.azzouz@gmail.com)"
'''

EXAMPLES = '''
# Obtain the extended attributes  of /etc/foo.conf
- xattr: name=/etc/foo.conf
# Sets the key 'foo' to value 'bar'
- xattr: path=/etc/foo.conf key=user.foo value=bar
# Removes the key 'foo'
- xattr: name=/etc/foo.conf key=user.foo state=absent
'''

# import module snippets
from ansible.module_utils.basic import AnsibleModule
from ahdp.module_utils.hdfsbase import *


def required_if():
  return [ ('state', 'present', ['key','value']),('state', 'absent', ['key']),('state', 'read', ['key']) ]

def invalid_if():
    return [ ('state', 'absent', ['value']),('state', 'keys', ['key','value']),('state', 'all', ['key','value']),('state', 'read', ['value']) ]

def main():

    argument_spec = hdfs_argument_spec()

    argument_spec.update( dict(
            path = dict(required=True, aliases=['name']),
            key = dict(required=False, default=None),
            value = dict(required=False, default=None),
            state = dict(required=False, default='read', choices=[ 'read', 'present', 'all', 'keys', 'absent' ], type='str'),
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

    params = module.params
    path  = params['path']
    key   = params['key']
    value = params['value']
    state = params['state']

    if not hdfs.hdfs_exist(path):
        hdfs.hdfs_fail_json(msg='Destination hdfs path %r does not exist or not accessible!' % path, changed=False)

    changed=False
    msg = ""
    res = {}

    # All xattr must begin in user namespace
    if key is not None and not re.match('^user\.',key):
        key = 'user.%s' % key

    if (state == 'present' or value is not None):
        changed |= hdfs.hdfs_setxattr(path=path,key=key,value=value)

        res=hdfs.hdfs_getxattrs(path=path)
        msg="%s set to %s" % (key, value)
    elif state == 'absent':
        changed |= hdfs.hdfs_rmxattr(path=path,key=key,strict=False)

        res=hdfs.hdfs_getxattrs(path=path)
        msg="%s removed" % (key)
    elif state == 'keys':
        res=hdfs.hdfs_listxattrs(path=path)
        msg="returning all keys"
    elif state == 'all':
        res=hdfs.hdfs_getxattrs(path=path)
        msg="dumping all"
    else:
        res=hdfs.hdfs_getxattrs(path=path,key=key)
        msg="returning %s" % key

    module.exit_json(changed=changed, msg=msg, xattr=res)

if __name__ == '__main__':
    main()
