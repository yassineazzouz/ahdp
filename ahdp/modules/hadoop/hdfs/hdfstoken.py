#!/usr/bin/python
# -*- coding: utf-8 -*-
## (c) 2016, Yassine Azzouz <yassine.azzouz@gmail.com>

DOCUMENTATION = '''
---
module: hdfstoken
short_description: Manage HDFS delegation tokens.
extends_documentation_fragment: hdfs
description:
     - Allow the management (creation/cancelation/query/renew) of HDFS delegation tokens.
     - Used with other hdfs modules provides a better alternative than kerberos for interacting with
       secured HDFS clusters.
version_added: "1.9"
requirements: [ pywhdfs ]
author: "Yassine Azzouz"
options:
  tokenid:
    description:
      - 'The delegation token to perform the disired operation on, only valid with 
         operation C(renew) or C(cancel)'
    required: false
    default: []
  operation:
    description:
      - If C(create), a new delegation token will be created and returned to the user. This is valid only if C(authentication)
          is kerberos.
        If C(renew), the provided delegation token will be renewed and a new expiration data is returned. This is valid 
          only if C(authentication) is kerberos.
        If C(cancel), the provided delegation token will be canceled.
        If C(query), query the list of available delegation tokens.
    required: true
    choices: [ create, renew, cancel, query ]
  renewer:
    required: false
    default: "None"
    description:
      - The username of the renewer of a delegation token.
  kind:
    required: false
    description:
      - The kind of the delegation token requested.
    default: "None"
  service:
    description:
      - The name of the service where the token is supposed to be used, e.g. ip:port of the namenode.
    required: false
    default: "None"
'''

EXAMPLES = '''
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
'''

import datetime as dt

# import module snippets
from ansible.module_utils.basic import AnsibleModule
from ahdp.module_utils.hdfsbase import *

def required_if():
  return [ ('operation', 'renew', ['tokenid']),('operation', 'cancel', ['tokenid']),('operation', 'create', ['renewer']),('operation', 'query', ['renewer']) ]

def invalid_if():
  return [ ('operation', 'renew', ['renewer','kind','service']),('operation', 'create', ['tokenid']),('operation', 'cancel', ['renewer','kind','service']),('operation', 'query', ['tokenid','kind','service']) ]

def main():
    argument_spec = hdfs_argument_spec()
    argument_spec.update( dict(
            tokenid       = dict(required=False, default=None, type='str', no_log=True),
            operation     = dict(required=True, choices=['create','renew','cancel','query']),
            renewer       = dict(required=False, default=None, type='str'),
            kind          = dict(required=False, default=None, type='str'),
            service       = dict(required=False, default=None, type='str'),
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
    operation  = params['operation']
    tokenid    = params['tokenid']
    renewer    = params['renewer']
    kind       = params['kind']
    service    = params['service']

    if operation == 'create':
      if hdfs.get_authentication_type() != 'kerberos':
        hdfs.hdfs_fail_json(msg='Delegation Token can be cretated only with kerberos or web authentication')

      tokenid = hdfs.hdfs_get_token(renewer=renewer,kind=kind,service=service)
      module.exit_json(token=tokenid, changed=True)
    elif operation == 'renew':
      if hdfs.get_authentication_type() != 'kerberos':
        hdfs.hdfs_fail_json(msg='Delegation Token can be renewed only with kerberos or web authentication')

      ts_epoch = hdfs.hdfs_renew_token(tokenid=tokenid)/1000
      expiration_date = dt.datetime.fromtimestamp(ts_epoch).strftime('%Y-%m-%d %H:%M:%S')
      module.exit_json(token=tokenid, expiration_date=expiration_date, changed=True)
    elif operation == 'cancel':
      hdfs.hdfs_cancel_token(tokenid=tokenid)
      module.exit_json(token=tokenid, changed=True)
    elif operation == 'query':
      hdfs.hdfs_fail_json(msg='query is not implemented yet.')
    
    hdfs.hdfs_fail_json(msg='unexpected position reached')

if __name__ == '__main__':
    main()
