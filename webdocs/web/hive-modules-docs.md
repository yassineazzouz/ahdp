# HIVE Modules

---
### Requirements

---
### Modules

  * [hive_db - add or remove hive or impala databases from a remote hive server 2 or impala host.](#hive_db)
  * [hive_privs - manage privileges on hive database objects.](#hive_privs)

---

## hive_db
Add or remove HIVE or Impala databases from a remote hive server 2 or impala host.

  * Synopsis
  * Options
  * Examples

#### Synopsis
 Add or remove Hive or impala databases from a remote host.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| comment  |   no  |  | |  A description or comment on the DB.  |
| keytab  |   no  |  | |  The keytab used to authenticate the principle, this is only valid with C(authentication=GSSAPI) only one credentials type can be used so this is mutually exclusive with C(password).  |
| kerberos_service_name  |   no  |  | |  Authenticate to a particular `impalad` or hs2 service principal.  |
| principal  |   no  |  | |  KERBEROS principal when using GSSAPI authentication.  This applies only to C(authentication=GSSAPI)  |
| verify  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  For secure connections whether to verify or not the server certificate.  |
| db  |   yes  |  | |  name of the database to add or remove  |
| authentication  |   no  |  NOSASL  | <ul> <li>NOSASL</li>  <li>PLAIN</li>  <li>GSSAPI</li>  <li>LDAP</li> </ul> |  {u'The authentication type to use': None}  NOSASL for unsecured Impala.  PLAIN for unsecured Hive (because Hive requires the SASL transport).  GSSAPI for Kerberos.  LDAP for Kerberos with LDAP.  |
| properties  |   no  |  | |  Properties to associate to the database.  |
| owner  |   no  |  | |  The USER or ROLE owner of the database.  |
| state  |   no  |  present  | <ul> <li>query</li>  <li>present</li>  <li>absent</li> </ul> |  The type of operation to perform on the database  |
| truststore  |   no  |  | |  For secure connections the server certificate file(trust store) to trust.  |
| location  |   no  |  | |  The DB location in HDFS.  |
| timeout  |   no  |  | |  Connection timeouts, forwarded to the request handler. This determines how long to wait for the server to send data before giving up.  |
| host  |   yes  |  | |  The hostname for HS2. For Impala, this can be any of the impala daemon.  |
| owner_type  |   no  |  | <ul> <li>USER</li>  <li>ROLE</li> </ul> |  The type of the owner, required with owner option.  |
| password  |   no  |  | |  LDAP or Kerberos password, if applicable.  |
| port  |   no  |  10000  | |  The port number for HS2 or Impala, defaults to 10000.  For Impala connections set to 21050.  |
| user  |   no  |  | |  LDAP user, if applicable.  |


 
#### Examples

```
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

```



---


## hive_privs
Manage privileges on HIVE database objects.

  * Synopsis
  * Options
  * Examples

#### Synopsis
 Grant or revoke privileges on HIVE database objects.
 This module support connection to a Hive server 2 or impala deamons and uses their thrift apis to perform previlege operations.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| keytab  |   no  |  | |  The keytab used to authenticate the principle, this is only valid with C(authentication=GSSAPI) only one credentials type can be used so this is mutually exclusive with C(password).  |
| kerberos_service_name  |   no  |  | |  Authenticate to a particular `impalad` or hs2 service principal.  |
| verify  |   no  |  no  | <ul> <li>yes</li>  <li>no</li> </ul> |  For secure connections whether to verify or not the server certificate.  |
| authentication  |   no  |  NOSASL  | <ul> <li>NOSASL</li>  <li>PLAIN</li>  <li>GSSAPI</li>  <li>LDAP</li> </ul> |  {u'The authentication type to use': None}  NOSASL for unsecured Impala.  PLAIN for unsecured Hive (because Hive requires the SASL transport).  GSSAPI for Kerberos.  LDAP for Kerberos with LDAP.  |
| host  |   yes  |  | |  The hostname for HS2. For Impala, this can be any of the impala daemon.  |
| objtype  |   no  |  | <ul> <li>table</li>  <li>server</li>  <li>column</li>  <li>database</li>  <li>uri</li>  <li>group</li> </ul> |  Type of the object to set privileges on.  |
| state  |   no  |  present  | <ul> <li>present</li>  <li>absent</li> </ul> |  If C(present), the specified privileges are granted, if C(absent) they are revoked.  |
| truststore  |   no  |  | |  For secure connections the server certificate file(trust store) to trust.  |
| role  |   yes  |  | |  The role name to set permissions for.  |
| user  |   no  |  | |  LDAP user, if applicable.  |
| timeout  |   no  |  | |  Connection timeouts, forwarded to the request handler. This determines how long to wait for the server to send data before giving up.  |
| privilege  |   no  |  | <ul> <li>select</li>  <li>insert</li>  <li>all</li> </ul> |  The type of previlege to grant or revoke.  |
| obj  |   yes  |  | |  The object name to target, corresponding to the type specified by C(objtype).  |
| password  |   no  |  | |  LDAP or Kerberos password, if applicable.  |
| port  |   no  |  10000  | |  The port number for HS2 or Impala, defaults to 10000.  For Impala connections set to 21050.  |
| grant_option  |   no  |  | <ul> <li>yes</li>  <li>no</li> </ul> |  Whether C(role) may grant/revoke the specified privileges/group memberships to others.  Set to C(no) to revoke GRANT OPTION, leave unspecified to make no changes.  I(grant_option) only has an effect if I(state) is C(present).  Alias: I(admin_option)  |
| principal  |   no  |  | |  KERBEROS principal when using GSSAPI authentication.  This applies only to C(authentication=GSSAPI)  |


 
#### Examples

```
# Create a role named test
- hive_privs:
   authentication: "PLAIN"
   user: "hive"
   password: "{{hive_ldap_password}}"
   host: "localhost"
   port: 10000
   role: "test"
   state: "present"

# Assign the ROLE test to the group test
- hive_privs:
   authentication: "PLAIN"
   user: "hive"
   password: "{{hive_ldap_password}}"
   host: "localhost"
   port: 10000
   role: "test"
   objtype: "group"
   obj: "test"
   state: "present"

# Grant the role test sect access on database db
- hive_privs:
   authentication: "PLAIN"
   user: "hive"
   password: "{{hive_ldap_password}}"
   host: "localhost"
   port: 10000
   role: "test"
   objtype: "database"
   obj: "db"
   privilege: "select"
   state: "present"

# grant the role test all previleges on table tb
- hive_privs:
   authentication: "PLAIN"
   user: "hive"
   password: "{{hive_ldap_password}}"
   host: "localhost"
   port: 10000
   role: "test"
   objtype: "table"
   obj: "db.tb"
   privilege: "all"
   state: "present"

# grant the role test all previleges on column id of table tb2
- hive_privs:
   authentication: "PLAIN"
   user: "hive"
   password: "{{hive_ldap_password}}"
   host: "localhost"
   port: 10000
   role: "test"
   objtype: "column"
   obj: "db.tb2.id"
   privilege: "select"
   state: "present"

# grant role test all previleges on uri
- hive_privs:
   authentication: "PLAIN"
   user: "hive"
   password: "{{hive_ldap_password}}"
   host: "localhost"
   port: 10000
   role: "test"
   objtype: "uri"
   obj: "hdfs:///hive/metastore/db/tb"
   privilege: "all"
   grant_option: True
   state: "present"

# REVOKE previleges on table tb for role test
- hive_privs:
   authentication: "PLAIN"
   user: "hive"
   password: "{{hive_ldap_password}}"
   host: "localhost"
   port: 10000
   role: "test"
   objtype: "table"
   obj: "db.tb"
   privilege: "all"
   state: "absent"

```



---


---
Created by Network to Code, LLC
For:
2015
