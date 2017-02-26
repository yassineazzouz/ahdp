#!/usr/bin/python
# -*- coding: utf-8 -*-
## (c) 2016, Yassine Azzouz <yassine.azzouz@gmail.com>

DOCUMENTATION = '''
---
module: hdfsupload
short_description: upload a list of files in parallel from the destination server to hdfs.
extends_documentation_fragment: hdfs
description:
     - Upload files or directories recursively from local to remote hdfs path.
     - Use parallel uploads with glob expressions to transfer a big list of files and directories.
     - Modify the uploaded files attributes based on parameters.
version_added: "1.9"
requirements: [ pywhdfs ]
author: "Yassine Azzouz"
options:
  dest:
    description:
      - Remote absolute hdfs path where the file should be copied to. If the destination does not exist the source will be uploaded under the basename.
    required: true
    default: []
    aliases: ['hdfs_path']
  src:
    description:
      - Local path to a file to copy to hdfs; can be absolute or relative.
      - If path is a directory, it is copied recursively This can also be a glob expressions that specify a list of files and directories to upload in parallel
      - If the path ends with * only files inside the source directory will be uploaded.
      - Patterns are very useful if you want to upload a huge list of files and want to make use of the parallelism offred by this module.
    required: true
    default: []
    aliases: ['local_path']
  owner:
    description:
      - name of the user that should own the hdfs file/directory.
    required: false
    default: null
  mode:
    description:
      - mode the hdfs file or directory should be. This should be an octal numbers (like 644). do not leave the leading zero.
    required: false
    default: null
  group:
    description:
      - name of the group that should own the hdfs file/directory.
    required: false
    default: null
  replication:
    description:
      - If set this will apply the replication value for all files uploaded.
    required: false
    default: null
  force:
    description:
      - the default is C(yes), which will replace the hdfs file/directory when content is different than the source.
      - If C(no), the file/directory will only be transferred if the destination does not exist.
    required: false
    choices: [ "yes", "no" ]
    default: "yes"
  preserve:
    description:
      - This will cause the hdfs file/directory to have the same attributes as the source local file/directory.
      - The attributes that are preserved are : owner,group,mode,modification time,access time.
    required: false
    default: "no"
  backup:
    description:
      - Create a backup file including the timestamp information so you can get the original file back if you somehow clobbered it incorrectly.
    version_added: "0.7"
    required: false
    choices: [ "yes", "no" ]
    default: "no"
'''

EXAMPLES = '''
# Upload file with preserve permissions
- hdfsupload:
    authentication: "kerberos"
    principal: "hdfs@LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    nameservices: "{{nameservices | to_json}}"
    src: "/home/admin/test"
    dest: "/user/ansible/test"
    preserve: True

# Upload file and set attributes
- hdfsupload:
    authentication: "kerberos"
    principal: "hdfs@LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    nameservices: "{{nameservices | to_json}}"
    src: "/home/admin/test"
    dest: "/user/ansible/test"
    owner: "hadoop"
    group: "supergroup"
    mode: 0766
    replication: 2
'''

import os
import os.path as osp

# import module snippets
from ansible.module_utils.basic import AnsibleModule
from ahdp.module_utils.hdfsbase import *

def upload_file(hdfs_module, local_path, hdfs_path, preserve=False, owner=None, 
                group=None, permission=None, replication=None, overwrite=False):
    """ Upload a single file from local to HDFS.
        :return upload_tuple: a dictionary having the upload result
          local_path  : the local file path
          hdfs_path   : the remote hdfs file path
          backup_path : if the original file have been backed up it would be different than hdfs_path 
                        if it is None it means the file didn't exist and was uploaded
                        if it is the same as hdfs_path it means the file is there but it was not uploaded
          changed     : If something have changed or not in the file, including file attributes changes if
                        the file already exist.
    """

    chunk_size=2 ** 16
    base_module = hdfs_module.module
    client = hdfs_module.client

    changed = False

    if not osp.isfile(local_path):
        hdfs_module.hdfs_fail_json(msg='Local Path %r does not exist.' % local_path, changed=False)

    basedir_status = hdfs_module.hdfs_status(osp.dirname(hdfs_path), strict=False)
    upload_tuple = dict()

    if basedir_status is None:
        changed = True
        # Split the path so we can apply filesystem attributes recursively from the root (/) directory for absolute paths or the base path
        # of a relative path.  We can then walk the appropriate directory path to apply attributes.
        curpath = ''
        root_dir = None
        for dirname in osp.dirname(hdfs_path).strip('/').split('/'):
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
                    localstat = os.stat(local_path)
                    hdfs_module.hdfs_set_attributes( path=curpath, 
                                                     owner=pwd.getpwuid(localstat.st_uid).pw_name, 
                                                     group=grp.getgrgid(localstat.st_gid).gr_name, 
                                                     permission=oct(stat.S_IMODE(localstat.st_mode)) 
                                                   )
                    hdfs_module.hdfs_set_times( curpath, access_time=int(localstat.st_atime * 1000), modification_time=int(localstat.st_mtime  * 1000))
                else:
                    hdfs_module.hdfs_set_attributes( path=curpath, owner=owner, group=group, replication=replication, permission=permission )
        # upload the file itself
        with open(local_path, 'rb') as reader:
            client.write(hdfs_path, reader.read(chunk_size))
        upload_tuple = dict({ 'local_path' : local_path, 'hdfs_path' : hdfs_path, 'backup_path' : None })

        if preserve:
            localstat = os.stat(local_path)
            hdfs_module.hdfs_set_attributes( path=hdfs_path, 
                                             owner=pwd.getpwuid(localstat.st_uid).pw_name, 
                                             group=grp.getgrgid(localstat.st_gid).gr_name, 
                                             permission=oct(stat.S_IMODE(localstat.st_mode)) 
                                           )
            hdfs_module.hdfs_set_times( hdfs_path, access_time=int(localstat.st_atime * 1000), modification_time=int(localstat.st_mtime  * 1000))
        else:
            hdfs_module.hdfs_set_attributes( path=hdfs_path, owner=owner, group=group, replication=replication, permission=permission )

    elif basedir_status['type'] == 'DIRECTORY':
        file_status = hdfs_module.hdfs_status(hdfs_path, strict=False)
        if file_status is None:
            # file does not exist and parent dir is there
            changed = True
            hdfs_module.cleanup_on_failure(hdfs_path)
            with open(local_path, 'rb') as reader:
                client.write(hdfs_path, reader.read(chunk_size))
            upload_tuple = dict( { 'local_path'   : local_path, 'hdfs_path'    : hdfs_path, 'backup_path'  : None } )
        elif file_status['type'] == 'DIRECTORY':
            # file exist and is a directory
            hdfs_module.hdfs_fail_json(msg='Conflicting Remote and local paths types.', changed=False)
        else:
            # file exist and is a normal file
            if not overwrite:
                hdfs_module.hdfs_fail_json(msg='Remote path %r already exists.' % hdfs_path, changed=False)
            checksum_local = base_module.sha1(local_path)
            checksum_hdfs = hdfs_module.hdfs_sha1(hdfs_path)
            if checksum_local != checksum_hdfs:
                changed = True

                ext = time.strftime("%Y-%m-%d@%H:%M:%S~", time.localtime(time.time()))
                backup_path = '%s.%s' % (hdfs_path, ext)

                client.rename(hdfs_path, backup_path)
                hdfs_module.restore_on_failure(restore_path=hdfs_path, backup_path=backup_path)

                with open(local_path, 'rb') as reader:
                    client.write(hdfs_path, reader.read(chunk_size))
                upload_tuple = dict( { 'local_path' : local_path, 'hdfs_path' : hdfs_path, 'backup_path' : backup_path } )
            else:
                # file is there and Same checksum, do not upload
                upload_tuple = dict({ 'local_path' : local_path, 'hdfs_path' : hdfs_path, 'backup_path' : hdfs_path })

        if preserve:
            localstat = os.stat(local_path)
            changed |= hdfs_module.hdfs_set_attributes( path=hdfs_path, owner=pwd.getpwuid(localstat.st_uid).pw_name, 
                                                                 group=grp.getgrgid(localstat.st_gid).gr_name, 
                                                                 permission=oct(stat.S_IMODE(localstat.st_mode)), 
                                                                 replication=replication )
                
            # we are not going to consider times for changed variable self.client.
            hdfs_module.hdfs_set_times( hdfs_path, access_time=int(localstat.st_atime * 1000), modification_time=int(localstat.st_mtime  * 1000))
        else:
            changed |= hdfs_module.hdfs_set_attributes( path=hdfs_path, owner=owner, group=group, replication=replication, permission=permission )
    else:
        # basedir is a file does not make sense
        hdfs_module.hdfs_fail_json(path=hdfs_path, msg="Invalide destination path, base directory %r is a file." % osp.dirname(hdfs_path))

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
            replication = dict(required=False,default=None, type='int'),
            force  = dict(default=False, type='bool'),
            preserve  = dict(default=False, type='bool'),
            backup  = dict(default=False, type='bool'),
        )
    )

    required_together = hdfs_required_together()
    mutually_exclusive = hdfs_mutually_exclusive()

    mutually_exclusive.extend(upload_mutually_exclusive())

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=required_together,
        mutually_exclusive=mutually_exclusive
    )

    hdfs = HDFSAnsibleModule(module=module)

    ''' Get all hdfs arguments '''
    params       = module.params
    local_path   = params['src']
    hdfs_path    = params['dest']
    owner        = params['owner']
    group        = params['group']
    mode         = params['mode']
    replication  = params['replication']
    force        = params['force']
    preserve     = params['preserve']
    backup       = params['backup']

    changed = False

    # Normalise local and remote paths
    destination_copy = hdfs_path.endswith(os.sep)
    content_copy = local_path.endswith(os.sep)

    local_path = osp.normpath( local_path )
    hdfs_path = hdfs.hdfs_resolvepath( hdfs_path )

    # resolve remote path
    status = hdfs.hdfs_status(hdfs_path,strict=False) 

    if status is None:
      if destination_copy:
        hdfs.hdfs_fail_json(msg='Destination hdfs directory %r does not exist.' % hdfs_path, changed=False)
      # Remote path doesn't exist.
      # check if parent exist
      pstatus = hdfs.hdfs_status(osp.dirname(hdfs_path),strict=False)
      if pstatus is None:
        hdfs.hdfs_fail_json(msg='Parent directory of %r does not exist.' % hdfs_path, changed=False)
      if pstatus['type'] == 'FILE' :
        hdfs.hdfs_fail_json(msg='Detination hdfs parent directory %r is a file.' % hdfs_path, changed=False)

    else:
        # Remote path exists.
        if status['type'] == 'FILE':
          # Remote path exists and is a normal file.
          if not osp.isfile(local_path):
            hdfs.hdfs_fail_json(msg='Conflicting Remote and local paths types: can not overwrite remote file with a directory.', changed=False)          
        else:
          # Remote path exists and is a directory.
          if not content_copy:
            # Copy the whole directory recursively
            hdfs_path =  osp.join( hdfs_path, osp.basename(local_path) )


    # Then we figure out which files we need to upload, and where.
    to_upload_tuples = []

    if osp.isdir(local_path):
        local_fpaths = [
          osp.join(dpath, fpath)
          for dpath, _, fpaths in os.walk(local_path)
          for fpath in fpaths
        ]

        offset = len(local_path.rstrip(os.sep)) + len(os.sep)
        to_upload_tuples =  [ dict({ 'local_path' : fpath, 'hdfs_path'  : osp.join(hdfs_path, fpath[offset:].replace(os.sep, '/')) })
                                for fpath in local_fpaths
                            ]
    elif osp.exists(local_path):
        to_upload_tuples =  [ dict({ 'local_path' : local_path, 'hdfs_path'  : hdfs_path }) ]
    else:
        hdfs.hdfs_fail_json(msg='Local path %r does not exist.' % local_path, changed=False)

    uploaded_tuples = []
    for upload in to_upload_tuples:
          uploaded_tuples.append(
                    upload_file( hdfs_module=hdfs,
                                 hdfs_path=upload['hdfs_path'],
                                 local_path=upload['local_path'], 
                                 preserve=preserve, 
                                 owner=owner, 
                                 group=group, 
                                 permission=mode, 
                                 replication=replication,
                                 overwrite=force )
                                )
    # everything went fine
    for uploaded_file in uploaded_tuples:
      changed = changed or uploaded_file['changed']
      if not backup:
        if uploaded_file['backup_path'] is not None and uploaded_file['backup_path'] != uploaded_file['hdfs_path']:
          hdfs.hdfs_delete(uploaded_file['backup_path'], recursive=True)

    res_args = dict(
        dest = hdfs_path, src = local_path, changed = changed
    )

    module.exit_json(**res_args)

if __name__ == '__main__':
    main()
