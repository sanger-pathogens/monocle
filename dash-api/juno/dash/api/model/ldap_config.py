
class LdapConfig(dict):
    """ Model class for ldap related configuration parameters """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
