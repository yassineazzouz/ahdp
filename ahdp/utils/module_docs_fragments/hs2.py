# (c) 2017, Yassine Azzouz <yassine.azzouz@gmail.com>

class ModuleDocFragment(object):

    # Standard files documentation fragment
    DOCUMENTATION = """
options:
  user:
    required: false
    default: null
    description:
      - LDAP user, if applicable.
  authentication:
    required: false
    default: NOSASL
    choices: [ NOSASL, PLAIN, GSSAPI, LDAP ]
    description:
      - The authentication type to use
      - NOSASL for unsecured Impala.
      - PLAIN for unsecured Hive (because Hive requires the SASL transport).
      - GSSAPI for Kerberos.
      - LDAP for Kerberos with LDAP.
  principal:
    required: false
    default: null
    description:
      - KERBEROS principal when using GSSAPI authentication.
      - This applies only to C(authentication=GSSAPI)
  kerberos_service_name:
    required: false
    default: null
    description:
      - Authenticate to a particular `impalad` or hs2 service principal.
  password:
    required: false
    default: null
    description:
      - LDAP or Kerberos password, if applicable.
  keytab:
    required: false
    default: null
    description:
      - The keytab used to authenticate the principle, this is only valid with C(authentication=GSSAPI) only one credentials type can be used so this is mutually exclusive with C(password).
  port:
    required: false
    default: 10000
    description:
      - The port number for HS2 or Impala, defaults to 10000.
      - For Impala connections set to 21050.
  host:
    required: true
    default: null
    description:
      - The hostname for HS2. For Impala, this can be any of the impala daemon.
  verify:
    required: false
    default: "no"
    choices: [ "yes", "no" ]
    description:
      - For secure connections whether to verify or not the server certificate.
  truststore:
    required: false
    default: null
    description:
      - For secure connections the server certificate file(trust store) to trust.
  timeout:
    required: false
    default: null
    description:
      - Connection timeouts, forwarded to the request handler. This determines how long to wait for the server to send data before giving up.
"""
