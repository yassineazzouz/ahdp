ahdp
==================================

ahdp is an ansible library of modules for integration with hadoop framework, it provides a way to interact with different hadoop services in a very simple and flexible way using ansible's easy syntax. The popse of this project is to provide DevOps and platform administrators a simple way to automate their operations on large scale hadoop clusters using ansible.

Features
---------------

Currently ahdp provides modules to interact with HDFS through WEBHDFS or HTTPFS and with hive server 2 or impala using thrift.

* Ansible libraries and utilities functions for HDFS operations :
    * create directories and files
    * change directories and files attributes and ownership
    * manage acls
    * manage extra attributes
    * fetch and copy files to HDFS
    * advanced search functionalities.
    * manage hdfs snapshots
    * The HDFS modules are based on [ pywhdfs ](https://github.com/yassineazzouz/pywhdfs) project to establish WebHDFS and HTTPFS connections with hdfs service.
        - Support both secure (Kerberos,Token) and insecure clusters
        - Supports HA clusters and handle namenode failover
        - Supports HDFS federation with multiple nameservices and mount points.
    * Please refer to the [ hdfs modules documentation ](webdocs/web/hdfs-modules-docs.md) for more details about all the supported modules

* Ansible libraries and utilities functions for HIVE operations :
    * create and delete databases
    * Manage privileges on hive database objects.
    * The hive modules are based on [ impyla client ](https://github.com/cloudera/impyla) project to interact with HIVE Mmetastore:
        - Support for multiple types of authentication (Kerberos, LDAP, PLAIN, NOSASL)
        - Support for SSL
        - Works with both hive server 2 and impala daemons connections.
    * Please refer to the [ hive modules documentation ](webdocs/web/hive-modules-docs.md) for more details about all the supported modules


Installation & Configuration
---------------

The ahdp module need to be installed on both the ansible server and on client machines (for instance the gateways that you will use as targets on the playbook). Normally simple ansible modules does not need to exist on target machines, however since the hdfs and hive modules uses a custom module_utils they need to be installed also on the target machine. 

To install ahdp on the ansible host :

```
pip install ahdp
```

or

```
pip install ahdp[ansible]
```

To install ahdp on the target hosts :

```
pip install ahdp[client]
```

The client extension will also install all dependencies that need to exist on target machines:
* [ pywhdfs ](https://github.com/yassineazzouz/pywhdfs)
* [ impyla client ](https://github.com/cloudera/impyla)
* thrift_sasl
* sasl 


Make sure the following packages are also installed on the target machines :
    libffi-devel
    gcc-c++
    python-devel
    krb5-devel

Note:
To use ahdp modules you need to configure ansible to know where the modules are located, you need simply add the library configuration to your ~/.ansible.cfg or to /etc/ansible.cfg, for instance if you have python 2.7, the modules path will be  :

```
library = /usr/lib/python2.7/site-packages/ahdp/modules/
```

You can also place manually the modules in a path of your choise then set the library option to that path.

Dependencies


USAGE
-------

The best way to use ahdp is to run ansible playbooks and see it as work, there are some testcases under "test" directory, which can give a high level idea of how an ansible project should be structured around hadoop.

Below a simple playbook that creates a User home directory in hdfs and a database in hive:

```yml
- hosts: localhost
  vars:
    nameservices:
      - urls: "http://localhost:50070"
        mounts: "/"
    hs2_host: "localhost"
  tasks:
    - name: Create HDFS user home directory
      hdfsfile:
        authentication: "none"
        state: "directory"
        path: "/user/ansible"
        owner: "ansible"
        group: "supergroup"
        mode: "0700"
        nameservices: "{{nameservices | to_json}}"
    - name: Create User hive database
      hive_db:
        authentication: "NOSASL"
        user: "hive"
        host: "{{hs2_host}}"
        port: 10000
        db: "ansible"
        owner: "ansible"
        state: "present"
```

To run the playbook, simply run:

```
 ansible-playbook simple_test.yml
```

SOME GOOD PRACTICES
--------

The folowing project aim to make hadoop administration and operation easier using ansible, below some useful tips and gidelines on how to structure a hadoop project in ansible:

* Create a separate inventory group for each hadoop cluster and create separate groups for different services and roles, If you are using a cloudera distribution you can also use dynamic inventory based the [ cloudera api ] ( tools/cloudera.py ).
* Define a gateway or edge node for each cluster to use it as target in your ansible playbooks. Make sure the ahdp project and its dependencies are installed on all edge nodes, you can also configure [ pywhdfs ](https://github.com/yassineazzouz/pywhdfs) and use its cli to interact programatically with the HDFS service.
* Create separate group variables for every cluster where you can define the connection parameters, for instance below a configuration example for a standalone hadoop installation :
```
cat group_vars/local/local.yml
---
nameservices:
      - urls: "http://localhost:50070"
        mounts: "/"
hs2_host: "localhost"
impala_daemon_host: "localhost"
cloudera_manager_host: "localhost"
```
* Use ansible vault for passwords, create a separate vault file for every cluster.
```
ansible-vault view group_vars/local/local_encrypted.yml
---
hdfs_kerberos_password: "password"
hdfs_principal: "hdfs@LOCALDOMAIN"
hive_ldap_password: "password"
```
* Create ansible roles for different kind of operational tasks you perform on your platforms and use "--limit=NAME_OF_CLUSTER" to control the target cluster.

Question or Ideas ?
------------

I'd love to hear what you think about ahdp and appreciate any idea or suggestion, Pull requests are also very welcome!
