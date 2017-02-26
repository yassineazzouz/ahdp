#!/usr/bin/python
# -*- coding: utf-8 -*-
## (c) 2016, Yassine Azzouz <yassine.azzouz@gmail.com>

DOCUMENTATION = '''
---
module: hdfsdownload
short_description: download a file or directory from hdfs.
extends_documentation_fragment: hdfs
description:
     - Download files or directories recursively from local to remote hdfs path.
     - Modify the downloaded files attributes based on parameters.
version_added: "1.9"
requirements: [ pywhdfs ]
author: "Yassine Azzouz"
options:
  dest:
    description:
      - 'Local path where the file should be downloaded to. If the destination does not exist the source will be uploaded under the basename.'
    required: true
    default: []
    aliases: ['local_path']
  src:
    description:
      - 'HDFS path of the file to download, if the path is a directory the recursive option is needed.'
    required: true
    default: []
    aliases: ['hdfs_path']
  owner:
    description:
      - 'name of the user that should own the local downloaded file/directory.'
    required: false
    default: null
  mode:
    description:
      - 'mode to be set on the local downloaded file or directory. This should be an octal numbers (like 0644).'
    required: false
    default: null
  group:
    description:
      - 'name of the group that should own the local downloaded file/directory.'
    required: false
    default: null
  force:
    description:
      - the default is C(yes), which will replace the local file/directory when contents
        are different than the source. If C(no), the file/directory will only be transferred
        if the destination does not exist.
    required: false
    choices: [ "yes", "no" ]
    default: "yes"
  preserve:
    description:
      - 'This will cause the local file/directory to have the same attributes as the source local file/directory. The
         attributes that are preserved are : owner,group,mode.'
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
- name: Fetch file with preserve
  hdfsdownload:
    authentication: "kerberos"
    principal: "hdfs@HADOOP.LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    src: "/user/ansible/testfile.csv"
    dest: "/home/admin/test"
    preserve: True
    urls: "{{namenodes_urls}}"
- name: Fetch directory
  hdfsdownload:
    authentication: "kerberos"
    principal: "hdfs@HADOOP.LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    src: "/user/ansible/data"
    dest: "/tmp/data"
    owner: yarn
    group: hadoop
    mode: 0777
    force: True
    urls: "{{namenodes_urls}}"
'''

import os
import os.path as osp

# import module snippets
from ansible.module_utils.basic import AnsibleModule
from ahdp.module_utils.hdfsbase import *

def download_file( hdfs_module, local_path, hdfs_path, preserve=False, owner=None,  
                   group=None, mode=None, overwrite=False):
  """Download a single file."""

  chunk_size=2 ** 16
  base_module = hdfs_module.module
  client = hdfs_module.client

  def _resolve_file_common_arguments(hpath):
    status = hdfs_module.hdfs_status(hpath, strict=False)
    if status is None:
        return {}
    _mode = status['permission']
    _group = status['group']
    _owner = status['owner']
    if _mode is not None:
      if len(_mode) == 3:
        _mode = "0" + str(_mode)
    return dict(
        path=hpath, mode=_mode, owner=_owner, group=_group,
        seuser=None, serole=None, setype=None,
        selevel=None, secontext=None,
    )

  changed = False

  if not hdfs_module.hdfs_is_file(hdfs_path):
    hdfs_module.hdfs_fail_json(msg='hdfs Path %r does not exist.' % hdfs_path, changed=False)

  upload_tuple = dict()

  if not osp.exists(osp.dirname(local_path)):
    changed = True
    # Split the path so we can apply filesystem attributes recursively from the root (/) directory for absolute paths or the base path
    # of a relative path.  We can then walk the appropriate directory path to apply attributes.
    curpath = ''
    root_dir = None
    for dirname in osp.dirname(local_path).strip('/').split('/'):
      curpath = '/'.join([curpath, dirname])
      if not osp.exists(curpath):
        # HERE we create directories, need to keep track of it for clean up
        # In case things go wrong we need to capture this for deletion
        if root_dir is not None:
          # the whole directory need to be cleaned up on failure
          hdfs_module.local_cleanup_on_failure(curpath)
          root_dir = curpath
        try:
          os.mkdir(curpath)
        except OSError, ex:
          hdfs_module.hdfs_fail_json(path=curpath, msg="OS error, could not create directory %s : %s" % (curpath,str(e)))
        if preserve:
          tmp_file_args = _resolve_file_common_arguments(hdfs_path)
          tmp_file_args['path']=curpath
          changed = base_module.set_fs_attributes_if_different(tmp_file_args, changed)
        else:
          tmp_file_args = dict( path=curpath, mode=mode, owner=owner, group=group, seuser=None, serole=None, setype=None, selevel=None, secontext=None )
          changed = base_module.set_fs_attributes_if_different(tmp_file_args, changed)

    # download the file itself
    with open(local_path, 'wb') as _writer:
      with client.read(hdfs_path) as _reader:
        _writer.write(_reader.read(chunk_size))

    upload_tuple = dict({ 'local_path' : local_path, 'hdfs_path' : hdfs_path, 'backup_path' : None })

    if preserve:
      tmp_file_args = _resolve_file_common_arguments(hdfs_path)
      tmp_file_args['path']=local_path
      changed = base_module.set_fs_attributes_if_different(tmp_file_args, changed)
    else:
      tmp_file_args = dict( path=local_path, mode=mode, owner=owner, group=group, seuser=None, serole=None, setype=None, selevel=None, secontext=None )
      changed = base_module.set_fs_attributes_if_different(tmp_file_args, changed)

  elif osp.isdir(osp.dirname(local_path)):
    if  not osp.exists(local_path):
      # file does not exist and parent dir is there
      changed = True
      hdfs_module.local_cleanup_on_failure(local_path)

      # download the file itself
      with open(local_path, 'wb') as _writer:
        with client.read(hdfs_path) as _reader:
          _writer.write(_reader.read(chunk_size))

      upload_tuple = dict( { 'local_path'   : local_path, 'hdfs_path'    : hdfs_path, 'backup_path'  : None } )

    elif osp.isdir(local_path):
      # file exist and is a directory
      hdfs_module.hdfs_fail_json(msg='Conflicting Remote and local paths types.', changed=False)
    else:
      # file exist and is a normal file
      if not overwrite:
        hdfs_module.hdfs_fail_json(msg='Local path %r already exists.' % local_path, changed=False)
                
      checksum_local = base_module.sha1(local_path)
      checksum_hdfs = hdfs_module.hdfs_sha1(hdfs_path)
      if checksum_local != checksum_hdfs:
        changed = True
        ext = time.strftime("%Y-%m-%d@%H:%M:%S~", time.localtime(time.time()))
        backup_path = '%s.%s' % (local_path, ext)
        os.rename(local_path, backup_path)
        hdfs_module.local_restore_on_failure(restore_path=local_path, backup_path=backup_path)

        with open(local_path, 'wb') as _writer:
          with client.read(hdfs_path) as _reader:
            _writer.write(_reader.read(chunk_size))
            
        upload_tuple = dict( { 'local_path' : local_path, 'hdfs_path' : hdfs_path, 'backup_path' : backup_path } )
      else:
        # file is there and Same checksum, do not download
        upload_tuple = dict({ 'local_path' : local_path, 'hdfs_path' : hdfs_path, 'backup_path' : local_path })

    if preserve:
      tmp_file_args = _resolve_file_common_arguments(hdfs_path)
      tmp_file_args['path']=local_path
      changed = base_module.set_fs_attributes_if_different(tmp_file_args, changed)
    else:
      tmp_file_args = dict( path=local_path, mode=mode, owner=owner, group=group, seuser=None, serole=None, setype=None, selevel=None, secontext=None )
      changed = base_module.set_fs_attributes_if_different(tmp_file_args, changed)
  else:
    # basedir is a file does not make sense
    hdfs_module.hdfs_fail_json(path=hdfs_path, msg="Invalide destination path, base directory %r is a file." % osp.dirname(local_path))

  upload_tuple['changed'] = changed
  return upload_tuple

# if preserve is used other attributes can not be used
def upload_mutually_exclusive():
    return [ ['preserve', 'owner'],['preserve', 'mode'],['preserve', 'group'] ]

def main():
    
    argument_spec = hdfs_argument_spec()
    argument_spec.update( dict(
            src  = dict(aliases=['local_path'], required=True),
            dest  = dict(aliases=['hdfs_path'], required=True),
            owner = dict(required=False,default=None),
            group = dict(required=False,default=None),
            mode = dict(required=False,default=None),
            force  = dict(default=False, type='bool'),
            preserve  = dict(default=False, type='bool'),
            backup  = dict(default=False, type='bool'),
        )
    )

    required_together = hdfs_required_together()
    mutually_exclusive = hdfs_mutually_exclusive()
    required_if = hdfs_required_if()

    mutually_exclusive.extend(upload_mutually_exclusive())

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=required_together,
        mutually_exclusive=mutually_exclusive
    )

    hdfs = HDFSAnsibleModule(module)

    ''' Get all hdfs arguments '''
    params       = module.params
    hdfs_path    = params['src']
    local_path   = params['dest']
    owner        = params['owner']
    group        = params['group']
    mode         = params['mode']
    force        = params['force']
    preserve     = params['preserve']
    backup       = params['backup']

    changed = False

    # Normalise local and remote paths
    content_copy = hdfs_path.endswith(os.sep)
    destination_copy = local_path.endswith(os.sep)

    local_path = osp.normpath( local_path )
    hdfs_path = hdfs.hdfs_resolvepath( hdfs_path )

    if not osp.exists(local_path):
      if destination_copy:
        hdfs.hdfs_fail_json(msg='Destination local directory %r does not exist.' % local_path, changed=False)
      # Local path doesn't exist.
      # check if parent exist
      if osp.exists(osp.dirname(local_path)):
        hdfs.hdfs_fail_json(msg='Parent directory of %r does not exist.' % local_path, changed=False)
      if osp.isfile(osp.dirname(local_path)):
        hdfs.hdfs_fail_json(msg='Detination local parent directory %r is a file.' % local_path, changed=False)

    else:
        # Local path exists.
        if osp.isfile(local_path):
          # Local path exists and is a normal file.
          if not hdfs.hdfs_is_file(hdfs_path):
            hdfs.hdfs_fail_json(msg='Conflicting Remote and local paths types: can not overwrite remote file with a directory.', changed=False)          
        else:
          # Local path exists and is a directory.
          if not content_copy:
            # Copy the whole directory recursively
            local_path =  osp.join( local_path, osp.basename(hdfs_path) )

    # Then we figure out which files we need to download, and where.
    to_download_tuples = []

    if hdfs.hdfs_is_dir(hdfs_path):
        remote_fpaths = [
          osp.join(dpath, fpath)
          for dpath, _, fpaths in hdfs.client.walk(hdfs_path)
          for fpath in fpaths
        ]

        offset = len(hdfs_path.rstrip(os.sep)) + len(os.sep)
        to_download_tuples =  [ dict({ 'hdfs_path' : fpath, 'local_path'  : osp.join(local_path, fpath[offset:].replace(os.sep, '/')) })
                                for fpath in remote_fpaths
                            ]
    elif hdfs.hdfs_exist(hdfs_path):
        to_download_tuples =  [ dict({ 'local_path' : local_path, 'hdfs_path'  : hdfs_path }) ]
    else:
        hdfs.hdfs_fail_json(msg='HDFS path %r does not exist.' % hdfs_path, changed=False)

    downloaded_tuples = []
    for download in to_download_tuples:
          downloaded_tuples.append(
                      download_file( hdfs_module=hdfs,
                                     hdfs_path=download['hdfs_path'],
                                     local_path=download['local_path'], 
                                     preserve=preserve, 
                                     owner=owner, 
                                     group=group, 
                                     mode=mode,
                                     overwrite=force )
                                   )
    # everything went fine
    for downloaded_file in downloaded_tuples:
      changed = changed or downloaded_file['changed']
      if not backup:
        if downloaded_file['backup_path'] is not None and downloaded_file['backup_path'] != downloaded_file['local_path']:
          os.remove(downloaded_file['backup_path'])

    res_args = dict(
        dest = local_path , src = hdfs_path, changed = changed
    )

    module.exit_json(**res_args)

if __name__ == '__main__':
    main()
