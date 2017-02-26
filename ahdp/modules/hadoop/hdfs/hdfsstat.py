#!/usr/bin/python
# -*- coding: utf-8 -*-
## (c) 2016, Yassine Azzouz <yassine.azzouz@gmail.com>

DOCUMENTATION = '''
---
module: hdfs-stat
short_description: retrieve hdfs file status
extends_documentation_fragment: hdfs
description:
     - Retrieves facts for a file similar to the linux/unix 'stat' command.
version_added: "1.9"
requirements: [ pywhdfs ]
author: "Yassine Azzouz"
options:
  path:
    description:
      - The full path of the file/object to get the facts of
    required: true
    default: null
    aliases: []
  get_checksum:
    description:
      - Whether to return the md5 sum of the file.  Will return None if we're unable to use md5
    required: false
    default: yes
    aliases: []
'''

EXAMPLES = '''
# Obtain the stats of /etc/foo.conf, and check that the file still belongs
# to 'root'. Fail otherwise.
- stat: path=/etc/foo.conf
  register: st
- fail: msg="Whoops! file ownership has changed"
  when: st.stat.pw_name != 'root'
'''

RETURN = '''
stat:
    description: dictionary containing all the stat data
    returned: success
    type: dictionary
    contains:
        exists:
            description: if the destination path actually exists or not
            returned: success
            type: boolean
            sample: True
        path:
            description: The full path of the file/object to get the facts of
            returned: success and if path exists
            type: string
            sample: '/path/to/file'
        pathSuffix:
            description: The Path Suffix of the file/object to get the facts of
            returned: success and if path exists
            type: string
            sample: '/path/to/file'
        type:
            description: The Type of the objects to get the facts of
            returned: success and if path exists
            type: string
            sample: 'FILE'
        owner:
            description: User name of owner
            returned: success, path exists and user can read stats and installed python supports it
            type: string
            sample: httpd
        group:
            description: Group name of owner
            returned: success, path exists and user can read stats and installed python supports it
            type: string
            sample: www-data
        permission:
            description: Unix permissions of the file in octal
            returned: success, path exists and user can read stats
            type: octal
            sample: 1755
        isdir:
            description: Tells if the path is a directory
            returned: success, path exists and user can read stats
            type: boolean
            sample: False
        isfile:
            description: Tells if the path is a file
            returned: success, path exists and user can read stats
            type: boolean
            sample: False
        length:
            description: Size in bytes for a plain file, ammount of data for some special files
            returned: success, path exists and user can read stats
            type: int
            sample: 203
        childrenNum:
            description: Number of children if the path is a directory
            returned: success, path exists and user can read stats
            type: int
            sample: 203
        replication:
            description: The replication factor of the file/object to get the facts of
            returned: success, path exists and user can read stats
            type: int
            sample: 1
        storagePolicy:
            description: The Storage policy of the file/object to get the facts of
            returned: success, path exists and user can read stats
            type: int
            sample: 1
        fileId:
            description: The File Id.
            returned: success, path exists and user can read stats
            type: int
            sample: 16387
        blockSize:
            description: The block size of the file
            returned: success, path exists and user can read stats
            type: int
            sample: 134217728
        accessTime:
            description: Time of last access
            returned: success, path exists and user can read stats
            type: int
            sample: 1449325194796
        modificationTime:
            description: Time of last modification
            returned: success, path exists and user can read stats
            type: int
            sample: 1448200788121
        spaceConsumed:
            description: THe space on disk consumed by the file/object
            returned: success, path exists and user can read stats
            type: int
            sample: 1448200788121
        quota:
            description: The name Quota of the file/object
            returned: success, path exists and user can read stats
            type: int
            sample: 1448200788121
        spaceQuota:
            description: The space Quota of the file/object
            returned: success, path exists and user can read stats
            type: int
            sample: 1448200788121
        directoryCount:
            description: The number of sub directories of the file/object
            returned: success, path exists and user can read stats
            type: int
            sample: 100
        fileCount:
            description: The number of files of the file/object
            returned: success, path exists and user can read stats
            type: int
            sample: 100
        wusr:
            description: Tells you if the owner has write permission
            returned: success, path exists and user can read stats
            type: boolean
            sample: True
        rusr:
            description: Tells you if the owner has read permission
            returned: success, path exists and user can read stats
            type: boolean
            sample: True
        xusr:
            description: Tells you if the owner has execute permission
            returned: success, path exists and user can read stats
            type: boolean
            sample: True
        wgrp:
            description: Tells you if the owner's group has write permission
            returned: success, path exists and user can read stats
            type: boolean
            sample: False
        rgrp:
            description: Tells you if the owner's group has read permission
            returned: success, path exists and user can read stats
            type: boolean
            sample: True
        xgrp:
            description: Tells you if the owner's group has execute permission
            returned: success, path exists and user can read stats
            type: boolean
            sample: True
        woth:
            description: Tells you if others have write permission
            returned: success, path exists and user can read stats
            type: boolean
            sample: False
        roth:
            description: Tells you if others have read permission
            returned: success, path exists and user can read stats
            type: boolean
            sample: True
        xoth:
            description: Tells you if others have execute permission
            returned: success, path exists and user can read stats
            type: boolean
            sample: True
        isuid:
            description: Tells you if the invoking user's id matches the owner's id
            returned: success, path exists and user can read stats
            type: boolean
            sample: False
        isgid:
            description: Tells you if the invoking user's group id matches the owner's group id
            returned: success, path exists and user can read stats
            type: boolean
            sample: False
        checksum:
            description: hash of the path
            returned: success, path exists, user can read stats, path supports hashing and supplied checksum algorithm is available
            type: string
            sample: 50ba294cdf28c0d5bcde25708df53346825a429f
        checksum_length:
            description: length of the hash
            returned: success, path exists, user can read stats
            type: int
            sample: 120
        checksum_algorithm:
            description: The hashing algorithm
            returned: success, path exists, user can read stats
            type: string
            sample: MD5-of-0MD5-of-512CRC32C
'''

# import module snippets
from ansible.module_utils.basic import AnsibleModule
from ahdp.module_utils.hdfsbase import *

def main():

    argument_spec = hdfs_argument_spec()
    argument_spec.update(dict(
            path = dict(required=True),
            get_checksum = dict(default='yes', type='bool')
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

    hdfs = HDFSAnsibleModule(module)
    path = module.params.get('path')
    get_checksum = module.params.get('get_checksum')

    status = hdfs.hdfs_status(path)
    content = hdfs.hdfs_content(path)

    if status is None:
        d = { 'exists' : False }
        module.exit_json(changed=False, stat=d)

    # back to ansible
    d = {
        'exists'            : True,
        'path'              : path,
        'pathSuffix'        : status['pathSuffix'],
        'type'              : status['type'],
        'owner'             : status['owner'],
        'group'             : status['group'],
        'permission'        : status['permission'],
        'isdir'             : bool(status['type'] == 'DIRECTORY'),
        'isfile'            : bool(status['type'] == 'FILE'),
        'childrenNum'       : status['childrenNum'],
        'replication'       : status['replication'],
        'storagePolicy'     : status['storagePolicy'],
        'fileId'            : status['fileId'],
        'blockSize'         : status['blockSize'],
        'accessTime'        : status['accessTime'],
        'modificationTime'  : status['modificationTime'],
        'length'            : content['length'],
        'spaceConsumed'     : content['spaceConsumed'],
        'quota'             : content['quota'],
        'spaceQuota'        : content['spaceQuota'],
        'directoryCount'    : content['directoryCount'],
        'fileCount'         : content['fileCount'],
        # First Byte of permissions for owner
        'rusr'              : bool( (int(status['permission'][0]) >> 2) & 1),
        'wusr'              : bool( (int(status['permission'][0]) >> 1) & 1),
        'xusr'              : bool( int(status['permission'][0]) & 1),
        # Second byte of permission for owner's group
        'rgrp'              : bool( (int(status['permission'][1]) >> 2) & 1),
        'wgrp'              : bool( (int(status['permission'][1]) >> 1) & 1),
        'xgrp'              : bool( int(status['permission'][1]) & 1),
        # Third byte of permissions for others
        'roth'              : bool( (int(status['permission'][2]) >> 2) & 1),
        'woth'              : bool( (int(status['permission'][2]) >> 1) & 1), 
        'xoth'              : bool( int(status['permission'][2]) & 1),
        }


    if status['type'] == 'FILE' and get_checksum:
        checksum = hdfs.hdfs_checksum(path, strict=False)
        d['checksum'] = checksum['bytes']
        d['checksum_length'] = checksum['length']
        d['checksum_algorithm'] = checksum['algorithm']

    module.exit_json(changed=False, stat=d)

if __name__ == '__main__':
   main()
