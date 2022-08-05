""" Module for exception classes """


class LdapDataError(Exception):
    """Exception when LDAP data method queries or responses are not valid"""

    pass


class NotAuthorisedException(Exception):
    """Thrown in the event of an authorisation issue"""

    pass
