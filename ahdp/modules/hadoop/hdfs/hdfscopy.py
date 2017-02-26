#!/usr/bin/python
# -*- coding: utf-8 -*-
## (c) 2016, Yassine Azzouz <yassine.azzouz@gmail.com>

DOCUMENTATION = '''
---
module: hdfscopy
short_description: copy hdfs files or directorys.
extends_documentation_fragment: hdfs
description:
     - Copy hdfs files or directories recursively.
     - Modify the copied files attributes based on parameters.
version_added: "1.9"
requirements: [ pywhdfs ]
author: "Yassine Azzouz"
options:
  dest:
    description:
      - 'Destination path where the file should be copied to. If the destination does not exist the source will be copied under the basename.'
    required: true
    default: []
  src:
    description:
      - 'source path of the file to copy, if the path is a directory the C(recursive) option is needed.'
    required: true
    default: []
  owner:
    description:
      - 'name of the user that should own the copied file/directory, mutually exclusive with C(preserve).'
    required: false
    default: null
  mode:
    description:
      - 'mode to be set on the copied file or directory. This should be an octal numbers (like 0644),
         mutually exclusive with C(preserve).'
    required: false
    default: null
  group:
    description:
      - 'name of the group that should own the copied file/directory, mutually exclusive with C(preserve).'
    required: false
    default: null
  replication:
    description:
      - 'If set this will apply the replication value for all copied files, mutually exclusive with C(preserve).'
    required: false
    default: null
  force:
    description:
      - the default is C(yes), which will replace the destination file/directory when contents
        are different than the source. If C(no), the file/directory will only be transferred
        if the destination does not exist.
    required: false
    choices: [ "yes", "no" ]
    default: "yes"
  preserve:
    description:
      - 'This will cause the destination file/directory to have the same attributes as the source file/directory. The
         attributes that are preserved are : owner,group,mode,replication. 
         mutually exclusive with C(owner),C(group),C(mode) and C(replication)'
    required: false
    default: "no"
  backup:
    description:
      - Create a backup file including the timestamp information so you can get
        the original file back if you somehow clobbered it incorrectly.
    required: false
    choices: [ "yes", "no" ]
    default: "no"
'''

EXAMPLES = '''
- name: Copy File
  hdfscopy:
    authentication: "kerberos"
    principal: "hdfs@HADOOP.LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    src: "/user/ansible/testfile.csv"
    dest: "/tmp/test/hdfscopy"
    preserve: True
    force: True
    urls: "{{namenodes_urls}}"
- name: Copy directory
  hdfscopy:
    authentication: "kerberos"
    principal: "hdfs@HADOOP.LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    src: "/user/ansible/data"
    dest: "/tmp/data"
    preserve: True
    urls: "{{namenodes_urls}}"
'''

import os
import os.path as osp

# import module snippets
from ansible.module_utils.basic import AnsibleModule
from ahdp.module_utils.hdfsbase import *

def copy_file( hdfs_module, dest_path, src_path, preserve=False, owner=None,  
                   group=None, mode=None, replication=None, overwrite=False):
  """Copy a single file."""

  chunk_size=2 ** 16
  base_module = hdfs_module.module
  client = hdfs_module.client

  changed = False

  if not hdfs_module.hdfs_is_file(src_path):
    hdfs_module.hdfs_fail_json(msg='hdfs Path %r does not exist.' % src_path, changed=False)

  status = hdfs_module.hdfs_status(src_path)
  content = hdfs_module.hdfs_content(src_path)

  copy_tuple = dict()

  if not hdfs_module.hdfs_exist(osp.dirname(dest_path)):
    changed = True
    # Split the path so we can apply filesystem attributes recursively from the root (/) directory for absolute paths or the base path
    # of a relative path.  We can then walk the appropriate directory path to apply attributes.
    curpath = ''
    root_dir = None
    for dirname in osp.dirname(dest_path).strip('/').split('/'):
      curpath = '/'.join([curpath, dirname])
      if not hdfs_module.hdfs_exist(curpath):
        # HERE we create directories, need to keep track of it for clean up
        # In case things go wrong we need to capture this for deletion
        if root_dir is not None:
          # the whole directory need to be cleaned up on failure
          hdfs_module.cleanup_on_failure(curpath)
          root_dir = curpath
        hdfs_module.hdfs_makedirs(curpath)
        if preserve:
          hdfs_module.hdfs_set_attributes( path=curpath, 
                                           owner=status['owner'], 
                                           group=status['group'],
                                           permission=status['permission'],
                                           replication=status['replication'] )
          hdfs_module.hdfs_set_times( curpath, access_time=status['accessTime'], modification_time=status['modificationTime'])
        else:
          hdfs_module.hdfs_set_attributes( path=curpath, owner=owner, group=group, replication=replication, permission=mode )

    # copy the file itself
    with client.write(dest_path) as _writer:
      with client.read(src_path) as _reader:
        _writer.write(_reader.read(chunk_size))

    copy_tuple = dict({ 'src_path' : src_path, 'dest_path' : dest_path, 'backup_path' : None })

    if preserve:
      hdfs_module.hdfs_set_attributes( path=dest_path, 
                                       owner=status['owner'], 
                                       group=status['group'],
                                       permission=status['permission'],
                                       replication=status['replication'] )
      hdfs_module.hdfs_set_times( path=dest_path, access_time=status['accessTime'], modification_time=status['modificationTime'])
    else:
      hdfs_module.hdfs_set_attributes( path=dest_path, owner=owner, group=group, replication=replication, permission=mode )

  elif hdfs_module.hdfs_is_dir(osp.dirname(dest_path)):
    if not hdfs_module.hdfs_exist(dest_path):
      # file does not exist and parent dir is there
      changed = True
      hdfs_module.cleanup_on_failure(dest_path)

      with client.write(dest_path) as _writer:
        with client.read(src_path) as _reader:
          _writer.write(_reader.read(chunk_size))

      copy_tuple = dict( { 'src_path' : src_path, 'dest_path' : dest_path, 'backup_path' : None } )

    elif hdfs_module.hdfs_is_dir(dest_path):
      # file exist and is a directory
      hdfs_module.hdfs_fail_json(msg='Conflicting destination and source paths types.', changed=False)
    else:
      # file exist and is a normal file
      if not overwrite:
        hdfs_module.hdfs_fail_json(msg='Destination path %r already exists.' % dest_path, changed=False)
      
      checksum_dest = hdfs_module.hdfs_checksum(dest_path)
      checksum_src = hdfs_module.hdfs_checksum(src_path)
      if checksum_dest['bytes'] != checksum_src['bytes']:
        changed = True
        ext = time.strftime("%Y-%m-%d@%H:%M:%S~", time.localtime(time.time()))
        backup_path = '%s.%s' % (dest_path, ext)
        client.rename(dest_path, backup_path)
        hdfs_module.restore_on_failure(restore_path=dest_path, backup_path=backup_path)

        with client.write(dest_path) as _writer:
          with client.read(src_path) as _reader:
            _writer.write(_reader.read(chunk_size))
            
        copy_tuple = dict( { 'src_path' : src_path, 'dest_path' : dest_path, 'backup_path' : backup_path } )
      else:
        # file is there and Same checksum, do not copy
        copy_tuple = dict({ 'src_path' : src_path, 'dest_path' : dest_path, 'backup_path' : dest_path })

    if preserve:
      changed |= hdfs_module.hdfs_set_attributes( path=dest_path, 
                                                  owner=status['owner'], 
                                                  group=status['group'],
                                                  permission=status['permission'],
                                                  replication=status['replication'] )
      hdfs_module.hdfs_set_times( path=dest_path, access_time=status['accessTime'], modification_time=status['modificationTime'])
    else:
      changed |= hdfs_module.hdfs_set_attributes( path=dest_path, owner=owner, group=group, replication=replication, permission=mode )
  else:
    # basedir is a file does not make sense
    hdfs_module.hdfs_fail_json(path=src_path, msg="Invalide destination path, base directory %r is a file." % osp.dirname(dest_path))

  copy_tuple['changed'] = changed
  return copy_tuple

# if preserve is used other attributes can not be used
def copy_mutually_exclusive():
    return [ ['preserve', 'owner'],['preserve', 'mode'],['preserve', 'group'],['preserve', 'group'] ]

def main():
    
    argument_spec = hdfs_argument_spec()
    argument_spec.update( dict(
            src  = dict(required=True),
            dest  = dict(required=True),
            owner = dict(required=False,default=None),
            group = dict(required=False,default=None),
            mode = dict(required=False,default=None, type='str'),
            replication = dict(required=False,default=None, type='int'),
            force  = dict(default=False, type='bool'),
            preserve  = dict(default=False, type='bool'),
            backup  = dict(default=False, type='bool'),
        )
    )

    required_together = hdfs_required_together()
    mutually_exclusive = hdfs_mutually_exclusive()
    required_if = hdfs_required_if()

    mutually_exclusive.extend(copy_mutually_exclusive())

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=required_together,
        mutually_exclusive=mutually_exclusive
    )

    hdfs = HDFSAnsibleModule(module)

    ''' Get all hdfs arguments '''
    params       = module.params
    src_path     = params['src']
    dest_path    = params['dest']
    owner        = params['owner']
    group        = params['group']
    mode         = params['mode']
    replication  = params['replication']
    force        = params['force']
    preserve     = params['preserve']
    backup       = params['backup']

    if mode != None and not re.compile("^(1|0)?[0-7]{3}$").match(mode):
      hdfs.hdfs_fail_json(msg='invalid mode value %r.' % mode, changed=False)

    changed = False

    # Normalise source and destination paths
    content_copy = src_path.endswith(os.sep)
    destination_copy = dest_path.endswith(os.sep)

    dest_path = hdfs.hdfs_resolvepath( dest_path )
    src_path = hdfs.hdfs_resolvepath( src_path )

    if not hdfs.hdfs_exist(dest_path):
      if destination_copy:
        hdfs.hdfs_fail_json(msg='Destination destination directory %r does not exist.' % dest_path, changed=False)
      # Dest path doesn't exist.
      # check if parent exist
      if hdfs.hdfs_exist(osp.dirname(dest_path)):
        hdfs.hdfs_fail_json(msg='Parent directory of %r does not exist.' % dest_path, changed=False)
      if hdfs.hdfs_is_file(osp.dirname(dest_path)):
        hdfs.hdfs_fail_json(msg='Detination parent directory %r is a file.' % dest_path, changed=False)

    else:
        # Dest path exists.
        if hdfs.hdfs_is_file(dest_path):
          # Local path exists and is a normal file.
          if not hdfs.hdfs_is_file(src_path):
            hdfs.hdfs_fail_json(msg='Conflicting source and destination paths types: can not overwrite remote file with a directory.', changed=False)          
        else:
          # Local path exists and is a directory.
          if not content_copy:
            # Copy the whole directory recursively
            dest_path =  osp.join( dest_path, osp.basename(src_path) )

    # Then we figure out which files we need to copy, and where.
    to_copy_tuples = []

    if hdfs.hdfs_is_dir(src_path):
        copy_fpaths = [
          osp.join(dpath, fpath)
          for dpath, _, fpaths in hdfs.client.walk(src_path)
          for fpath in fpaths
        ]

        offset = len(src_path.rstrip(os.sep)) + len(os.sep)
        to_copy_tuples =  [ dict({ 'src_path' : fpath, 'dest_path'  : osp.join(dest_path, fpath[offset:].replace(os.sep, '/')) })
                                for fpath in copy_fpaths
                            ]
    elif hdfs.hdfs_exist(src_path):
        to_copy_tuples =  [ dict({ 'dest_path' : dest_path, 'src_path'  : src_path }) ]
    else:
        hdfs.hdfs_fail_json(msg='source path %r does not exist.' % src_path, changed=False)

    copied_tuples = []
    for copy in to_copy_tuples:
          copied_tuples.append(
                          copy_file( hdfs_module=hdfs,
                                     src_path=copy['src_path'],
                                     dest_path=copy['dest_path'], 
                                     preserve=preserve, 
                                     owner=owner, 
                                     group=group, 
                                     mode=mode,
                                     replication=replication,
                                     overwrite=force )
                              )
    # everything went fine
    for copied_file in copied_tuples:
      changed = changed or copied_file['changed']
      if not backup:
        if copied_file['backup_path'] is not None and copied_file['backup_path'] != copied_file['dest_path']:
          hdfs.hdfs_delete(copied_file['backup_path'], recursive=True)

    res_args = dict(
        dest = dest_path , src = src_path, changed = changed
    )

    module.exit_json(**res_args)

if __name__ == '__main__':
    main()
