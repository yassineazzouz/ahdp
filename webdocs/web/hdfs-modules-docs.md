# HDFS Modules

---
### Requirements

---
### Modules

  * [hdfsfind - return a list of hdfs files based on specific criteria](#hdfsfind)
  * [hdfs-stat - retrieve hdfs file status](#hdfs-stat)
  * [hdfsfile - sets attributes of hdfs files](#hdfsfile)
  * [hdfs_snapshot - create/delete/rename and list hdfs snapshots.](#hdfs_snapshot)
  * [hdfsxattr - set/retrieve hdfs extended attributes](#hdfsxattr)
  * [hdfsupload - upload a list of files in parallel from the destination server to hdfs.](#hdfsupload)
  * [hdfstoken - manage hdfs delegation tokens.](#hdfstoken)
  * [hdfsdownload - download a file or directory from hdfs.](#hdfsdownload)
  * [hdfscopy - copy hdfs files or directorys.](#hdfscopy)
  * [hdfsacl - sets and retrieves file acl information on hdfs.](#hdfsacl)

---

## hdfsfind
return a list of hdfs files based on specific criteria

  * Synopsis
  * Options
  * Examples

#### Synopsis
 Return a list of files in HDFS based on specific criteria. This module is inspired from the base ansible find module.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| file_type  |   no  |  file  | <ul> <li>file</li>  <li>directory</li> </ul> |  Type of file to select  |
| size  |   no  |  | |  Select files whose size is equal to or greater than the specified size. Use a negative size to find files equal to or less than the specified size. Unqualified values are in bytes, but b, k, m, g, and t can be appended to specify bytes, kilobytes, megabytes, gigabytes, and terabytes, respectively. Size is not evaluated for directories.  |
| paths  |   yes  |  | |  List of paths to the file or directory to search. All paths must be fully qualified.  |
| keytab  |   no  |  | |  The keytab used to authenticate the principle, this is only valid with C(authentication=kerberos) only one credentials type can be used so this is mutually exclusive with C(password).  |
| verify  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  For secure connections whether to verify or not the server certificate.  |
| contains  |   no  |  | |  One or more re patterns which should be matched against the file content.  |
| authentication  |   no  |  none  | <ul> <li>none</li>  <li>kerberos</li>  <li>token</li> </ul> |  {u'The authentication type to use': u'if C(local), the user issuing the requests will be the current user.'}  if C(kerberos), the C(principal) and C(keytab) or C(password) will be used to kinit.  if C(token), the C(token) will be used to authenticate the user.  |
| get_checksum  |   no  |  False  | <ul> <li>True</li>  <li>False</li> </ul> |  Set this to true to retrieve a file's sha1 checksum  |
| principal  |   no  |  | |  When security is on, the authentication is performed against a kerberos server with the principal, specified by this parameter.  This applies only to C(authentication=kerberos)  |
| age_stamp  |   no  |  mtime  | <ul> <li>atime</li>  <li>mtime</li>  <li>ctime</li> </ul> |  Choose the file property against which we compare age. Default is mtime.  |
| user  |   no  |  | |  Identity of the user running the query, (applies only to C(authentication=local)). When security is off the authenticated user is the username specified in the user.name query parameter, specified by this parameter. Defaults to the current user (as determined by I(whoami)).  |
| use_regex  |   no  |  False  | <ul> <li>True</li>  <li>False</li> </ul> |  If false the patterns are file globs (shell) if true they are python regexes  |
| nameservices  |   yes  |  | |  A json list of nameservices to connect to, each nameservice is a dict having a list of namenodes urls and the associated mount points.  You can create the spec in yml then use the to_json filter.  |
| password  |   no  |  | |  The kerberos password used to authenticate the principle, this is only valid with C(authentication=kerberos).  |
| age  |   no  |  | |  Select files whose age is equal to or greater than the specified time. Use a negative age to find files equal to or less than the specified time. You can choose seconds, minutes, hours, days, or weeks by specifying the first letter of any of those words (e.g., "1w").  |
| recurse  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  If target is a directory, recursively descend into the directory looking for files.  |
| patterns  |   no  |  *  | |  One or more (shell or regex) patterns, which type is controled by C(use_regex) option.  The patterns restrict the list of files to be returned to those whose basenames match at least one of the patterns specified. Multiple patterns can be specified using a list.  |
| token  |   no  |  | |  When security is on you can use a delegation token instead of having to authenticate every time with kerberos.  |
| truststore  |   no  |  | |  For secure connections the server certificate file(trust store) to trust.  |
| timeout  |   no  |  | |  Connection timeouts, forwarded to the request handler. This determines how long to wait for the server to send data before giving up.  |
| root  |   no  |  | |  Root path, this will be prefixed to all HDFS paths passed. If the root is relative, the path will be assumed relative to the user home directory.  |
| proxy  |   no  |  | |  User to proxy as, theorically make sense only with C(authentication=kerberos) or C(authentication=token) but works for both secure and Insecure.  |


 
#### Examples

```
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

```



---


## hdfs-stat
retrieve hdfs file status

  * Synopsis
  * Options
  * Examples

#### Synopsis
 Retrieves facts for a file similar to the linux/unix 'stat' command.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| keytab  |   no  |  | |  The keytab used to authenticate the principle, this is only valid with C(authentication=kerberos) only one credentials type can be used so this is mutually exclusive with C(password).  |
| timeout  |   no  |  | |  Connection timeouts, forwarded to the request handler. This determines how long to wait for the server to send data before giving up.  |
| principal  |   no  |  | |  When security is on, the authentication is performed against a kerberos server with the principal, specified by this parameter.  This applies only to C(authentication=kerberos)  |
| verify  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  For secure connections whether to verify or not the server certificate.  |
| token  |   no  |  | |  When security is on you can use a delegation token instead of having to authenticate every time with kerberos.  |
| authentication  |   no  |  none  | <ul> <li>none</li>  <li>kerberos</li>  <li>token</li> </ul> |  {u'The authentication type to use': u'if C(local), the user issuing the requests will be the current user.'}  if C(kerberos), the C(principal) and C(keytab) or C(password) will be used to kinit.  if C(token), the C(token) will be used to authenticate the user.  |
| truststore  |   no  |  | |  For secure connections the server certificate file(trust store) to trust.  |
| user  |   no  |  | |  Identity of the user running the query, (applies only to C(authentication=local)). When security is off the authenticated user is the username specified in the user.name query parameter, specified by this parameter. Defaults to the current user (as determined by I(whoami)).  |
| get_checksum  |   no  |  True  | |  Whether to return the md5 sum of the file.  Will return None if we're unable to use md5  |
| nameservices  |   yes  |  | |  A json list of nameservices to connect to, each nameservice is a dict having a list of namenodes urls and the associated mount points.  You can create the spec in yml then use the to_json filter.  |
| path  |   yes  |  | |  The full path of the file/object to get the facts of  |
| password  |   no  |  | |  The kerberos password used to authenticate the principle, this is only valid with C(authentication=kerberos).  |
| root  |   no  |  | |  Root path, this will be prefixed to all HDFS paths passed. If the root is relative, the path will be assumed relative to the user home directory.  |
| proxy  |   no  |  | |  User to proxy as, theorically make sense only with C(authentication=kerberos) or C(authentication=token) but works for both secure and Insecure.  |


 
#### Examples

```
# Obtain the stats of /etc/foo.conf, and check that the file still belongs
# to 'root'. Fail otherwise.
- stat: path=/etc/foo.conf
  register: st
- fail: msg="Whoops! file ownership has changed"
  when: st.stat.pw_name != 'root'

```



---


## hdfsfile
Sets attributes of hdfs files

  * Synopsis
  * Options
  * Examples

#### Synopsis
 create HDFS files or directories
 Sets attributes of HDFS files and directories
 Removes HDFS files/directories.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| keytab  |   no  |  | |  The keytab used to authenticate the principle, this is only valid with C(authentication=kerberos) only one credentials type can be used so this is mutually exclusive with C(password).  |
| recursive  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  recursively set the specified file attributes (applies only to state=directory)  |
| principal  |   no  |  | |  When security is on, the authentication is performed against a kerberos server with the principal, specified by this parameter.  This applies only to C(authentication=kerberos)  |
| verify  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  For secure connections whether to verify or not the server certificate.  |
| nameservices  |   yes  |  | |  A json list of nameservices to connect to, each nameservice is a dict having a list of namenodes urls and the associated mount points.  You can create the spec in yml then use the to_json filter.  |
| authentication  |   no  |  none  | <ul> <li>none</li>  <li>kerberos</li>  <li>token</li> </ul> |  {u'The authentication type to use': u'if C(local), the user issuing the requests will be the current user.'}  if C(kerberos), the C(principal) and C(keytab) or C(password) will be used to kinit.  if C(token), the C(token) will be used to authenticate the user.  |
| spacequota  |   no  |  | |  The space quota to be applied to the directory. This option applies only to directories.  |
| replication  |   no  |  | |  The replication factor to be applied to the file. This option applies only to files.  |
| state  |   no  |  file  | <ul> <li>file</li>  <li>directory</li>  <li>touch</li>  <li>absent</li> </ul> |  If C(directory), all immediate subdirectories will be created if they do not exist, they will be created with the supplied permissions. If C(file), the file will NOT be created if it does not exist. If C(absent), directories and files will be recursively deleted. If C(touch), an empty file will be created if the C(path) does not exist, while an existing file or directory will receive updated file access and modification times (similar to the way `touch` works from the command line).  |
| truststore  |   no  |  | |  For secure connections the server certificate file(trust store) to trust.  |
| user  |   no  |  | |  Identity of the user running the query, (applies only to C(authentication=local)). When security is off the authenticated user is the username specified in the user.name query parameter, specified by this parameter. Defaults to the current user (as determined by I(whoami)).  |
| timeout  |   no  |  | |  Connection timeouts, forwarded to the request handler. This determines how long to wait for the server to send data before giving up.  |
| path  |   yes  |  []  | |  path to the file being managed.  Aliases: I(dest), I(name)  |
| owner  |   no  |  | |  name of the user that should own the file/directory, as would be fed to I(chown)  |
| group  |   no  |  | |  name of the group that should own the file/directory, as would be fed to I(chown)  |
| namequota  |   no  |  | |  The name quota to be applied to the directory. This option applies only to directories.  |
| password  |   no  |  | |  The kerberos password used to authenticate the principle, this is only valid with C(authentication=kerberos).  |
| root  |   no  |  | |  Root path, this will be prefixed to all HDFS paths passed. If the root is relative, the path will be assumed relative to the user home directory.  |
| proxy  |   no  |  | |  User to proxy as, theorically make sense only with C(authentication=kerberos) or C(authentication=token) but works for both secure and Insecure.  |
| token  |   no  |  | |  When security is on you can use a delegation token instead of having to authenticate every time with kerberos.  |
| mode  |   no  |  | |  mode the file or directory should be. For those used to I(/usr/bin/chmod) remember that modes are actually octal numbers (like 0644). Leaving off the leading zero will likely have unexpected results. The mode may be specified as a symbolic mode (for example, C(u+rwx) or C(u=rw,g=r,o=r)).  |


 
#### Examples

```
- name: "Create test Folder"
  hdfsfile:
    authentication: "kerberos"
    principal: "hdfs@HADOOP.LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    verify: True
    truststore: "/opt/cloudera/security/cacerts/platform-ca.crt"
    state: "directory"
    path: "/user/yassine"
    urls: "{{namenodes_urls}}"
    mode: "u=rw,g=r,o=rwX"
- name: "Create subdirectory"
  hdfsfile:
    authentication: "kerberos"
    principal: "hdfs@HADOOP.LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    verify: True
    truststore: "/opt/cloudera/security/cacerts/platform-ca.crt"
    state: "directory"
    path: "/user/yassine/subdir"
    owner: "hadoop"
    group: "supergroup"
    mode: 0766
    urls: "{{namenodes_urls}}"
- name: "Remove directory"
  hdfsfile:
    authentication: "kerberos"
    principal: "hdfs@HADOOP.LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    verify: True
    truststore: "/opt/cloudera/security/cacerts/platform-ca.crt"
    state: "absent"
    path: "/user/yassine/subdir"
    urls: "{{namenodes_urls}}"

```



---


## hdfs_snapshot
create/delete/rename and list HDFS snapshots.

  * Synopsis
  * Options
  * Examples

#### Synopsis
 Performs hdfs hdfs snapshots operations.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| rename  |   no  |    | |  The new name of the snapshot, valid only with C(operation) C(rename)  |
| keytab  |   no  |  | |  The keytab used to authenticate the principle, this is only valid with C(authentication=kerberos) only one credentials type can be used so this is mutually exclusive with C(password).  |
| name  |   no  |    | |  Name of the snapshot to perform the operation on.  |
| principal  |   no  |  | |  When security is on, the authentication is performed against a kerberos server with the principal, specified by this parameter.  This applies only to C(authentication=kerberos)  |
| verify  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  For secure connections whether to verify or not the server certificate.  |
| token  |   no  |  | |  When security is on you can use a delegation token instead of having to authenticate every time with kerberos.  |
| authentication  |   no  |  none  | <ul> <li>none</li>  <li>kerberos</li>  <li>token</li> </ul> |  {u'The authentication type to use': u'if C(local), the user issuing the requests will be the current user.'}  if C(kerberos), the C(principal) and C(keytab) or C(password) will be used to kinit.  if C(token), the C(token) will be used to authenticate the user.  |
| truststore  |   no  |  | |  For secure connections the server certificate file(trust store) to trust.  |
| user  |   no  |  | |  Identity of the user running the query, (applies only to C(authentication=local)). When security is off the authenticated user is the username specified in the user.name query parameter, specified by this parameter. Defaults to the current user (as determined by I(whoami)).  |
| timeout  |   no  |  | |  Connection timeouts, forwarded to the request handler. This determines how long to wait for the server to send data before giving up.  |
| nameservices  |   yes  |  | |  A json list of nameservices to connect to, each nameservice is a dict having a list of namenodes urls and the associated mount points.  You can create the spec in yml then use the to_json filter.  |
| path  |   yes  |    | |  The full path of the directory to perform a snapshot on, the directory need to be snapshottable.  |
| operation  |   no  |  list  | <ul> <li>create</li>  <li>delete</li>  <li>rename</li>  <li>list</li> </ul> |  defines which operation you want to perform. C(create) create a hdfs snapshot for the provided path. C(delete) deletes the snapshot with C(name) for C(path) C(rename) rename the snapshot with C(name) to C(rename) C(list) list all snapshots for C(path).  |
| password  |   no  |  | |  The kerberos password used to authenticate the principle, this is only valid with C(authentication=kerberos).  |
| root  |   no  |  | |  Root path, this will be prefixed to all HDFS paths passed. If the root is relative, the path will be assumed relative to the user home directory.  |
| proxy  |   no  |  | |  User to proxy as, theorically make sense only with C(authentication=kerberos) or C(authentication=token) but works for both secure and Insecure.  |


 
#### Examples

```
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

```



---


## hdfsxattr
set/retrieve hdfs extended attributes

  * Synopsis
  * Options
  * Examples

#### Synopsis
 Manages hdfs user defined extended attributes, requires that they are enabled on the target cluster using the dfs.namenode.xattrs.enabled option.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| key  |   no  |    | |  The name of a specific Extended attribute key to set/retrieve  |
| keytab  |   no  |  | |  The keytab used to authenticate the principle, this is only valid with C(authentication=kerberos) only one credentials type can be used so this is mutually exclusive with C(password).  |
| name  |   yes  |    | |  The full path of the file/object to get the facts of  |
| principal  |   no  |  | |  When security is on, the authentication is performed against a kerberos server with the principal, specified by this parameter.  This applies only to C(authentication=kerberos)  |
| verify  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  For secure connections whether to verify or not the server certificate.  |
| authentication  |   no  |  none  | <ul> <li>none</li>  <li>kerberos</li>  <li>token</li> </ul> |  {u'The authentication type to use': u'if C(local), the user issuing the requests will be the current user.'}  if C(kerberos), the C(principal) and C(keytab) or C(password) will be used to kinit.  if C(token), the C(token) will be used to authenticate the user.  |
| value  |   no  |    | |  The value to set the named name/key to, it automatically sets the C(state) to 'set'  |
| state  |   no  |  get  | <ul> <li>read</li>  <li>present</li>  <li>all</li>  <li>keys</li>  <li>absent</li> </ul> |  defines which state you want to do. C(read) retrieves the current value for a C(key) (default) C(present) sets C(name) to C(value), default if value is set C(all) dumps all data C(keys) retrieves all keys C(absent) deletes the key  |
| truststore  |   no  |  | |  For secure connections the server certificate file(trust store) to trust.  |
| user  |   no  |  | |  Identity of the user running the query, (applies only to C(authentication=local)). When security is off the authenticated user is the username specified in the user.name query parameter, specified by this parameter. Defaults to the current user (as determined by I(whoami)).  |
| timeout  |   no  |  | |  Connection timeouts, forwarded to the request handler. This determines how long to wait for the server to send data before giving up.  |
| nameservices  |   yes  |  | |  A json list of nameservices to connect to, each nameservice is a dict having a list of namenodes urls and the associated mount points.  You can create the spec in yml then use the to_json filter.  |
| password  |   no  |  | |  The kerberos password used to authenticate the principle, this is only valid with C(authentication=kerberos).  |
| root  |   no  |  | |  Root path, this will be prefixed to all HDFS paths passed. If the root is relative, the path will be assumed relative to the user home directory.  |
| token  |   no  |  | |  When security is on you can use a delegation token instead of having to authenticate every time with kerberos.  |
| proxy  |   no  |  | |  User to proxy as, theorically make sense only with C(authentication=kerberos) or C(authentication=token) but works for both secure and Insecure.  |


 
#### Examples

```
# Obtain the extended attributes  of /etc/foo.conf
- xattr: name=/etc/foo.conf
# Sets the key 'foo' to value 'bar'
- xattr: path=/etc/foo.conf key=user.foo value=bar
# Removes the key 'foo'
- xattr: name=/etc/foo.conf key=user.foo state=absent

```



---


## hdfsupload
upload a list of files in parallel from the destination server to hdfs.

  * Synopsis
  * Options
  * Examples

#### Synopsis
 Upload files or directories recursively from local to remote hdfs path.
 Use parallel uploads with glob expressions to transfer a big list of files and directories.
 Modify the uploaded files attributes based on parameters.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| preserve  |   no  |  no  | |  This will cause the hdfs file/directory to have the same attributes as the source local file/directory.  {u'The attributes that are preserved are': u'owner,group,mode,modification time,access time.'}  |
| src  |   yes  |  []  | |  Local path to a file to copy to hdfs; can be absolute or relative.  If path is a directory, it is copied recursively This can also be a glob expressions that specify a list of files and directories to upload in parallel  If the path ends with * only files inside the source directory will be uploaded.  Patterns are very useful if you want to upload a huge list of files and want to make use of the parallelism offred by this module.  |
| force  |   no  |  yes  | <ul> <li>yes</li>  <li>no</li> </ul> |  the default is C(yes), which will replace the hdfs file/directory when content is different than the source.  If C(no), the file/directory will only be transferred if the destination does not exist.  |
| dest  |   yes  |  []  | |  Remote absolute hdfs path where the file should be copied to. If the destination does not exist the source will be uploaded under the basename.  |
| verify  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  For secure connections whether to verify or not the server certificate.  |
| keytab  |   no  |  | |  The keytab used to authenticate the principle, this is only valid with C(authentication=kerberos) only one credentials type can be used so this is mutually exclusive with C(password).  |
| token  |   no  |  | |  When security is on you can use a delegation token instead of having to authenticate every time with kerberos.  |
| root  |   no  |  | |  Root path, this will be prefixed to all HDFS paths passed. If the root is relative, the path will be assumed relative to the user home directory.  |
| group  |   no  |  | |  name of the group that should own the hdfs file/directory.  |
| principal  |   no  |  | |  When security is on, the authentication is performed against a kerberos server with the principal, specified by this parameter.  This applies only to C(authentication=kerberos)  |
| replication  |   no  |  | |  If set this will apply the replication value for all files uploaded.  |
| authentication  |   no  |  none  | <ul> <li>none</li>  <li>kerberos</li>  <li>token</li> </ul> |  {u'The authentication type to use': u'if C(local), the user issuing the requests will be the current user.'}  if C(kerberos), the C(principal) and C(keytab) or C(password) will be used to kinit.  if C(token), the C(token) will be used to authenticate the user.  |
| truststore  |   no  |  | |  For secure connections the server certificate file(trust store) to trust.  |
| mode  |   no  |  | |  mode the hdfs file or directory should be. This should be an octal numbers (like 644). do not leave the leading zero.  |
| timeout  |   no  |  | |  Connection timeouts, forwarded to the request handler. This determines how long to wait for the server to send data before giving up.  |
| owner  |   no  |  | |  name of the user that should own the hdfs file/directory.  |
| nameservices  |   yes  |  | |  A json list of nameservices to connect to, each nameservice is a dict having a list of namenodes urls and the associated mount points.  You can create the spec in yml then use the to_json filter.  |
| password  |   no  |  | |  The kerberos password used to authenticate the principle, this is only valid with C(authentication=kerberos).  |
| backup  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  Create a backup file including the timestamp information so you can get the original file back if you somehow clobbered it incorrectly.  |
| proxy  |   no  |  | |  User to proxy as, theorically make sense only with C(authentication=kerberos) or C(authentication=token) but works for both secure and Insecure.  |
| user  |   no  |  | |  Identity of the user running the query, (applies only to C(authentication=local)). When security is off the authenticated user is the username specified in the user.name query parameter, specified by this parameter. Defaults to the current user (as determined by I(whoami)).  |


 
#### Examples

```
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

```



---


## hdfstoken
Manage HDFS delegation tokens.

  * Synopsis
  * Options
  * Examples

#### Synopsis
 Allow the management (creation/cancelation/query/renew) of HDFS delegation tokens.
 Used with other hdfs modules provides a better alternative than kerberos for interacting with secured HDFS clusters.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| kind  |   no  |    | |  The kind of the delegation token requested.  |
| keytab  |   no  |  | |  The keytab used to authenticate the principle, this is only valid with C(authentication=kerberos) only one credentials type can be used so this is mutually exclusive with C(password).  |
| service  |   no  |    | |  The name of the service where the token is supposed to be used, e.g. ip:port of the namenode.  |
| tokenid  |   no  |  []  | |  The delegation token to perform the disired operation on, only valid with operation C(renew) or C(cancel)  |
| principal  |   no  |  | |  When security is on, the authentication is performed against a kerberos server with the principal, specified by this parameter.  This applies only to C(authentication=kerberos)  |
| verify  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  For secure connections whether to verify or not the server certificate.  |
| token  |   no  |  | |  When security is on you can use a delegation token instead of having to authenticate every time with kerberos.  |
| authentication  |   no  |  none  | <ul> <li>none</li>  <li>kerberos</li>  <li>token</li> </ul> |  {u'The authentication type to use': u'if C(local), the user issuing the requests will be the current user.'}  if C(kerberos), the C(principal) and C(keytab) or C(password) will be used to kinit.  if C(token), the C(token) will be used to authenticate the user.  |
| truststore  |   no  |  | |  For secure connections the server certificate file(trust store) to trust.  |
| user  |   no  |  | |  Identity of the user running the query, (applies only to C(authentication=local)). When security is off the authenticated user is the username specified in the user.name query parameter, specified by this parameter. Defaults to the current user (as determined by I(whoami)).  |
| timeout  |   no  |  | |  Connection timeouts, forwarded to the request handler. This determines how long to wait for the server to send data before giving up.  |
| nameservices  |   yes  |  | |  A json list of nameservices to connect to, each nameservice is a dict having a list of namenodes urls and the associated mount points.  You can create the spec in yml then use the to_json filter.  |
| operation  |   yes  |  | <ul> <li>create</li>  <li>renew</li>  <li>cancel</li>  <li>query</li> </ul> |  If C(create), a new delegation token will be created and returned to the user. This is valid only if C(authentication) is kerberos. If C(renew), the provided delegation token will be renewed and a new expiration data is returned. This is valid only if C(authentication) is kerberos. If C(cancel), the provided delegation token will be canceled. If C(query), query the list of available delegation tokens.  |
| password  |   no  |  | |  The kerberos password used to authenticate the principle, this is only valid with C(authentication=kerberos).  |
| root  |   no  |  | |  Root path, this will be prefixed to all HDFS paths passed. If the root is relative, the path will be assumed relative to the user home directory.  |
| renewer  |   no  |    | |  The username of the renewer of a delegation token.  |
| proxy  |   no  |  | |  User to proxy as, theorically make sense only with C(authentication=kerberos) or C(authentication=token) but works for both secure and Insecure.  |


 
#### Examples

```
- name: "Create a delegation token"
  hdfstoken:
    authentication: "kerberos"
    principal: "hdfs@HADOOP.LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    verify: True
    truststore: "/opt/cloudera/security/cacerts/platform-ca.crt"
    urls: "{{namenodes_urls}}"
    operation: "create" 
    renewer: "hdfs" 
  register: token
- name: "Renew delegarion token"
  hdfstoken:
    authentication: "kerberos"
    principal: "hdfs@HADOOP.LOCALDOMAIN"
    password: "{{hdfs_kerberos_password}}"
    verify: True
    truststore: "/opt/cloudera/security/cacerts/platform-ca.crt"
    urls: "{{namenodes_urls}}"
    operation: "renew"
    tokenid: "{{token.token}}"
  register: new_token
- debug: msg="{{new_token}}"
- name: "Delete delegarion token"
  hdfstoken:
    authentication: "token"
    token: "{{token.token}}"
    verify: True
    truststore: "/opt/cloudera/security/cacerts/platform-ca.crt"
    urls: "{{namenodes_urls}}"
    operation: "cancel"
    tokenid: "{{token.token}}"

```



---


## hdfsdownload
download a file or directory from hdfs.

  * Synopsis
  * Options
  * Examples

#### Synopsis
 Download files or directories recursively from local to remote hdfs path.
 Modify the downloaded files attributes based on parameters.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| preserve  |   no  |  no  | |  This will cause the local file/directory to have the same attributes as the source local file/directory. The attributes that are preserved are : owner,group,mode.  |
| src  |   yes  |  []  | |  HDFS path of the file to download, if the path is a directory the recursive option is needed.  |
| force  |   no  |  yes  | <ul> <li>yes</li>  <li>no</li> </ul> |  the default is C(yes), which will replace the local file/directory when contents are different than the source. If C(no), the file/directory will only be transferred if the destination does not exist.  |
| dest  |   yes  |  []  | |  Local path where the file should be downloaded to. If the destination does not exist the source will be uploaded under the basename.  |
| verify  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  For secure connections whether to verify or not the server certificate.  |
| keytab  |   no  |  | |  The keytab used to authenticate the principle, this is only valid with C(authentication=kerberos) only one credentials type can be used so this is mutually exclusive with C(password).  |
| token  |   no  |  | |  When security is on you can use a delegation token instead of having to authenticate every time with kerberos.  |
| root  |   no  |  | |  Root path, this will be prefixed to all HDFS paths passed. If the root is relative, the path will be assumed relative to the user home directory.  |
| group  |   no  |  | |  name of the group that should own the local downloaded file/directory.  |
| principal  |   no  |  | |  When security is on, the authentication is performed against a kerberos server with the principal, specified by this parameter.  This applies only to C(authentication=kerberos)  |
| authentication  |   no  |  none  | <ul> <li>none</li>  <li>kerberos</li>  <li>token</li> </ul> |  {u'The authentication type to use': u'if C(local), the user issuing the requests will be the current user.'}  if C(kerberos), the C(principal) and C(keytab) or C(password) will be used to kinit.  if C(token), the C(token) will be used to authenticate the user.  |
| truststore  |   no  |  | |  For secure connections the server certificate file(trust store) to trust.  |
| mode  |   no  |  | |  mode to be set on the local downloaded file or directory. This should be an octal numbers (like 0644).  |
| timeout  |   no  |  | |  Connection timeouts, forwarded to the request handler. This determines how long to wait for the server to send data before giving up.  |
| owner  |   no  |  | |  name of the user that should own the local downloaded file/directory.  |
| nameservices  |   yes  |  | |  A json list of nameservices to connect to, each nameservice is a dict having a list of namenodes urls and the associated mount points.  You can create the spec in yml then use the to_json filter.  |
| password  |   no  |  | |  The kerberos password used to authenticate the principle, this is only valid with C(authentication=kerberos).  |
| backup  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  Create a backup file including the timestamp information so you can get the original file back if you somehow clobbered it incorrectly.  |
| proxy  |   no  |  | |  User to proxy as, theorically make sense only with C(authentication=kerberos) or C(authentication=token) but works for both secure and Insecure.  |
| user  |   no  |  | |  Identity of the user running the query, (applies only to C(authentication=local)). When security is off the authenticated user is the username specified in the user.name query parameter, specified by this parameter. Defaults to the current user (as determined by I(whoami)).  |


 
#### Examples

```
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

```



---


## hdfscopy
copy hdfs files or directorys.

  * Synopsis
  * Options
  * Examples

#### Synopsis
 Copy hdfs files or directories recursively.
 Modify the copied files attributes based on parameters.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| preserve  |   no  |  no  | |  This will cause the destination file/directory to have the same attributes as the source file/directory. The attributes that are preserved are : owner,group,mode,replication. mutually exclusive with C(owner),C(group),C(mode) and C(replication)  |
| src  |   yes  |  []  | |  source path of the file to copy, if the path is a directory the C(recursive) option is needed.  |
| force  |   no  |  yes  | <ul> <li>yes</li>  <li>no</li> </ul> |  the default is C(yes), which will replace the destination file/directory when contents are different than the source. If C(no), the file/directory will only be transferred if the destination does not exist.  |
| dest  |   yes  |  []  | |  Destination path where the file should be copied to. If the destination does not exist the source will be copied under the basename.  |
| verify  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  For secure connections whether to verify or not the server certificate.  |
| keytab  |   no  |  | |  The keytab used to authenticate the principle, this is only valid with C(authentication=kerberos) only one credentials type can be used so this is mutually exclusive with C(password).  |
| token  |   no  |  | |  When security is on you can use a delegation token instead of having to authenticate every time with kerberos.  |
| root  |   no  |  | |  Root path, this will be prefixed to all HDFS paths passed. If the root is relative, the path will be assumed relative to the user home directory.  |
| group  |   no  |  | |  name of the group that should own the copied file/directory, mutually exclusive with C(preserve).  |
| principal  |   no  |  | |  When security is on, the authentication is performed against a kerberos server with the principal, specified by this parameter.  This applies only to C(authentication=kerberos)  |
| replication  |   no  |  | |  If set this will apply the replication value for all copied files, mutually exclusive with C(preserve).  |
| authentication  |   no  |  none  | <ul> <li>none</li>  <li>kerberos</li>  <li>token</li> </ul> |  {u'The authentication type to use': u'if C(local), the user issuing the requests will be the current user.'}  if C(kerberos), the C(principal) and C(keytab) or C(password) will be used to kinit.  if C(token), the C(token) will be used to authenticate the user.  |
| truststore  |   no  |  | |  For secure connections the server certificate file(trust store) to trust.  |
| mode  |   no  |  | |  mode to be set on the copied file or directory. This should be an octal numbers (like 0644), mutually exclusive with C(preserve).  |
| timeout  |   no  |  | |  Connection timeouts, forwarded to the request handler. This determines how long to wait for the server to send data before giving up.  |
| owner  |   no  |  | |  name of the user that should own the copied file/directory, mutually exclusive with C(preserve).  |
| nameservices  |   yes  |  | |  A json list of nameservices to connect to, each nameservice is a dict having a list of namenodes urls and the associated mount points.  You can create the spec in yml then use the to_json filter.  |
| password  |   no  |  | |  The kerberos password used to authenticate the principle, this is only valid with C(authentication=kerberos).  |
| backup  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  Create a backup file including the timestamp information so you can get the original file back if you somehow clobbered it incorrectly.  |
| proxy  |   no  |  | |  User to proxy as, theorically make sense only with C(authentication=kerberos) or C(authentication=token) but works for both secure and Insecure.  |
| user  |   no  |  | |  Identity of the user running the query, (applies only to C(authentication=local)). When security is off the authenticated user is the username specified in the user.name query parameter, specified by this parameter. Defaults to the current user (as determined by I(whoami)).  |


 
#### Examples

```
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

```



---


## hdfsacl
Sets and retrieves file ACL information on hdfs.

  * Synopsis
  * Options
  * Examples

#### Synopsis
 Sets and retrieves file ACL information on hdfs.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| keytab  |   no  |  | |  The keytab used to authenticate the principle, this is only valid with C(authentication=kerberos) only one credentials type can be used so this is mutually exclusive with C(password).  |
| recursive  |   no  |  False  | <ul> <li>yes</li>  <li>no</li> </ul> |  Recursively sets the specified ACL. Incompatible with C(state=query).  |
| principal  |   no  |  | |  When security is on, the authentication is performed against a kerberos server with the principal, specified by this parameter.  This applies only to C(authentication=kerberos)  |
| verify  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  For secure connections whether to verify or not the server certificate.  |
| token  |   no  |  | |  When security is on you can use a delegation token instead of having to authenticate every time with kerberos.  |
| authentication  |   no  |  none  | <ul> <li>none</li>  <li>kerberos</li>  <li>token</li> </ul> |  {u'The authentication type to use': u'if C(local), the user issuing the requests will be the current user.'}  if C(kerberos), the C(principal) and C(keytab) or C(password) will be used to kinit.  if C(token), the C(token) will be used to authenticate the user.  |
| state  |   no  |  query  | <ul> <li>query</li>  <li>present</li>  <li>absent</li> </ul> |  defines whether the ACL should be present or not.  The C(query) state gets the current acl without changing it, for use in register operations.  if state is query, entries need to be null  if state is absent, then we remove acls, entries can be null to say remove everything. otherwise if provided the entity need to be provided and permissions need to be null in all acl entries  if state is present, then we add/overwrite acls. You can use overwrite to replace existing acls but you must include entries for user, group, and others for compatibility with permission bits.  |
| truststore  |   no  |  | |  For secure connections the server certificate file(trust store) to trust.  |
| user  |   no  |  | |  Identity of the user running the query, (applies only to C(authentication=local)). When security is off the authenticated user is the username specified in the user.name query parameter, specified by this parameter. Defaults to the current user (as determined by I(whoami)).  |
| timeout  |   no  |  | |  Connection timeouts, forwarded to the request handler. This determines how long to wait for the server to send data before giving up.  |
| entries  |   no  |  | |  Defines a list of acl entries, An ACL entry have an optional default field to specify, if it is a default acl or not, a type (user, group, mask, or other), an optional name called entity (referring to a specific user or group) and a set of permissions (any combination of read, write and execute). A single acl entry is a string having three/or four identifiers separated by a colon default, type, entity, permissions.  |
| nameservices  |   yes  |  | |  A json list of nameservices to connect to, each nameservice is a dict having a list of namenodes urls and the associated mount points.  You can create the spec in yml then use the to_json filter.  |
| path  |   yes  |  | |  The full path of the file or object.  |
| password  |   no  |  | |  The kerberos password used to authenticate the principle, this is only valid with C(authentication=kerberos).  |
| root  |   no  |  | |  Root path, this will be prefixed to all HDFS paths passed. If the root is relative, the path will be assumed relative to the user home directory.  |
| overwrite  |   no  |  False  | <ul> <li>yes</li>  <li>no</li> </ul> |  If used acls will be completely replaced. Fully replaces ACL of files and directories, discarding all existing entries.  Note that default acls are not overwritten by the overwrite parameter, you can change default acls either delelting all acls or by using the scope default in acl entries with state absent or prensent to modify/delete individual default acls.  |
| proxy  |   no  |  | |  User to proxy as, theorically make sense only with C(authentication=kerberos) or C(authentication=token) but works for both secure and Insecure.  |


 
#### Examples

```
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

```


#### Notes

- The "acl" module requires that hdfs acls are enabled on your cluster using dfs.namenode.acls.enabled.

- Note when using this module do not use the folded block scalar ">" after the module name like "hdfsacl >" because the list parameters will be interpreted as string argument.


---


---
Created by Network to Code, LLC
For:
2015
