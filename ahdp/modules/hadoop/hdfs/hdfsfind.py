#!/usr/bin/python
# -*- coding: utf-8 -*-
## (c) 2016, Yassine Azzouz <yassine.azzouz@gmail.com>

DOCUMENTATION = '''
---
module: hdfsfind
short_description: return a list of hdfs files based on specific criteria
extends_documentation_fragment: hdfs
description:
    - Return a list of files in HDFS based on specific criteria. This module is inspired from the base ansible find module.
version_added: "1.9"
requirements: [ pywhdfs ]
author: "Yassine Azzouz"
options:
    age:
        required: false
        default: null
        description:
            - Select files whose age is equal to or greater than the specified time.
              Use a negative age to find files equal to or less than the specified time.
              You can choose seconds, minutes, hours, days, or weeks by specifying the
              first letter of any of those words (e.g., "1w").
    patterns:
        required: false
        default: '*'
        description:
            - One or more (shell or regex) patterns, which type is controled by C(use_regex) option.
            - The patterns restrict the list of files to be returned to those whose basenames match at
              least one of the patterns specified. Multiple patterns can be specified using a list.
        aliases: ['pattern']
    contains:
        required: false
        default: null
        description:
            - One or more re patterns which should be matched against the file content.
    paths:
        required: true
        aliases: [ "name", "path" ]
        description:
            - List of paths to the file or directory to search. All paths must be fully qualified.
    file_type:
        required: false
        description:
            - Type of file to select
        choices: [ "file", "directory" ]
        default: "file"
    recurse:
        required: false
        default: "no"
        choices: [ "yes", "no" ]
        description:
            - If target is a directory, recursively descend into the directory looking for files.
    size:
        required: false
        default: null
        description:
            - Select files whose size is equal to or greater than the specified size.
              Use a negative size to find files equal to or less than the specified size.
              Unqualified values are in bytes, but b, k, m, g, and t can be appended to specify
              bytes, kilobytes, megabytes, gigabytes, and terabytes, respectively.
              Size is not evaluated for directories.
    age_stamp:
        required: false
        default: "mtime"
        choices: [ "atime", "mtime", "ctime" ]
        description:
            - Choose the file property against which we compare age. Default is mtime.
    get_checksum:
        required: false
        default: "False"
        choices: [ True, False ]
        description:
            - Set this to true to retrieve a file's sha1 checksum
    use_regex:
        required: false
        default: "False"
        choices: [ True, False ]
        description:
            - If false the patterns are file globs (shell) if true they are python regexes
'''


EXAMPLES = '''
# Recursively find /tmp files older than 2 days
- find: paths="/tmp" age="2d" recurse=yes

# Recursively find /tmp files older than 4 weeks and equal or greater than 1 megabyte
- find: paths="/tmp" age="4w" size="1m" recurse=yes

# Recursively find /var/tmp files with last access time greater than 3600 seconds
- find: paths="/var/tmp" age="3600" age_stamp=atime recurse=yes

# find /var/log files equal or greater than 10 megabytes ending with .old or .log.gz
- find: paths="/var/tmp" patterns="'*.old','*.log.gz'" size="10m"

# find /var/log files equal or greater than 10 megabytes ending with .old or .log.gz via regex
- find: paths="/var/tmp" patterns="^.*?\.(?:old|log\.gz)$" size="10m" use_regex=True
'''

RETURN = '''
files:
    description: all matches found with the specified criteria (see stat module for full output of each dictionary)
    returned: success
    type: list of dictionaries
    sample: [
        { path="/var/tmp/test1",
          mode=0644,
          ...,
          checksum=16fac7be61a6e4591a33ef4b729c5c3302307523
        },
        { path="/var/tmp/test2",
          ...
        },
        ]
matched:
    description: number of matches
    returned: success
    type: string
    sample: 14
examined:
    description: number of filesystem objects looked at
    returned: success
    type: string
    sample: 34
'''

import os
import stat
import fnmatch
import time
import re

# import module snippets
from ansible.module_utils.basic import AnsibleModule
from ahdp.module_utils.hdfsbase import *

def pfilter(f, patterns=None, use_regex=False):
    '''filter using glob patterns'''

    if patterns is None:
        return True

    if use_regex:
        for p in patterns:
            r =  re.compile(p)
            if r.match(f):
                return True
    else:

        for p in patterns:
            if fnmatch.fnmatch(f, p):
                return True

    return False


def agefilter(status, now, age, timestamp):
    '''filter files older than age'''
    if age is None or \
      (age >= 0 and now - int(status["%s" % timestamp]/1000) >= abs(age)) or \
      (age < 0 and now - int(status["%s" % timestamp]/1000) <= abs(age)):

        return True
    return False


def sizefilter(status, size):
    '''filter files greater than size'''
    if size is None or \
       (size >= 0 and status['length'] >= abs(size)) or \
       (size < 0 and status['length'] <= abs(size)):

        return True

    return False

def contentfilter(hdfs, fsname, pattern):
    '''filter files which contain the given expression'''
    if pattern is None: return True

    try:
        prog = re.compile(pattern)
        with hdfs.client.read(fsname, delimiter='\n', encoding='utf-8') as _reader:
            for line in _reader:
                if prog.match (line):
                    return True
    except:
       pass
    return False

def statinfo(status,content):
    d = {
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
    return d

def main():
    argument_spec = hdfs_argument_spec()
    argument_spec.update( dict(
            paths         = dict(required=True, aliases=['name','path'], type='list'),
            patterns      = dict(default=['*'], type='list', aliases=['pattern']),
            contains      = dict(default=None, type='str'),
            file_type     = dict(default="file", choices=['file', 'directory'], type='str'),
            age           = dict(default=None, type='str'),
            age_stamp     = dict(default="modificationTime", choices=['modificationTime','accessTime'], type='str'),
            size          = dict(default=None, type='str'),
            recurse       = dict(default='no', type='bool'),
            get_checksum  = dict(default="False", type='bool'),
            use_regex     = dict(default="False", type='bool'),
        )
    )

    required_together = hdfs_required_together()
    mutually_exclusive = hdfs_mutually_exclusive()
    required_if = hdfs_required_if()

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=required_together,
        mutually_exclusive=mutually_exclusive
    )

    hdfs = HDFSAnsibleModule(module)

    params = module.params


    filelist = []

    if params['age'] is None:
        age = None
    else:
        # convert age to seconds:
        m = re.match("^(-?\d+)(s|m|h|d|w)?$", params['age'].lower())
        seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
        if m:
            age = int(m.group(1)) * seconds_per_unit.get(m.group(2), 1)
        else:
            module.fail_json(age=params['age'], msg="failed to process age")

    if params['size'] is None:
        size = None
    else:
        # convert size to bytes:
        m = re.match("^(-?\d+)(b|k|m|g|t)?$", params['size'].lower())
        bytes_per_unit = {"b": 1, "k": 1024, "m": 1024**2, "g": 1024**3, "t": 1024**4}
        if m:
            size = int(m.group(1)) * bytes_per_unit.get(m.group(2), 1)
        else:
            module.fail_json(size=params['size'], msg="failed to process size")

    # convert to seconds
    now = int(time.time())
    msg = ''
    looked = 0
    for npath in params['paths']:
        if hdfs.hdfs_is_dir(npath):

            for root,dirs,files in hdfs.client.walk(npath):
                looked = looked + len(files) + len(dirs)
                for fsobj in (files + dirs):
                    fsname=os.path.normpath(os.path.join(root, fsobj))

                    try:
                        status = hdfs.client.status(fsname, strict=False)
                        content = hdfs.client.content(fsname, strict=False)
                    except:
                        msg+="%s was skipped as it does not seem to be a valid file or it cannot be accessed\n" % fsname
                        continue

                    r = {'path': fsname}
                    if status['type'] == 'DIRECTORY' and params['file_type'] == 'directory':
                        if pfilter(fsobj, params['patterns'], params['use_regex']) and agefilter(status, now, age, params['age_stamp']):

                            r.update(statinfo(status,content))
                            filelist.append(r)

                    elif status['type'] == 'FILE' and params['file_type'] == 'file':
                        if pfilter(fsobj, params['patterns'], params['use_regex']) and \
                           agefilter(status, now, age, params['age_stamp']) and \
                           sizefilter(status, size) and \
                           contentfilter(hdfs, fsname, params['contains']):

                            r.update(statinfo(status,content))
                            if params['get_checksum']:
                                r['checksum'] = self.hdfs.hdfs_sha1(fsname)
                            filelist.append(r)

                if not params['recurse']:
                    break
        else:
            msg+="%s was skipped as it does not seem to be a valid directory or it cannot be accessed\n" % npath

    matched = len(filelist)
    module.exit_json(files=filelist, changed=False, msg=msg, matched=matched, examined=looked)

if __name__ == '__main__':
   main()
