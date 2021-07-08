import unittest
import os
import ldap
from unittest.mock import patch
from dash.api.model.ldap_config import LdapConfig
from dash.api.user.ldap_user_service import LdapUserService


class TestLdapUserService(unittest.TestCase):
    """ Test class for the LdapUserService module """

    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    def setUp(self) -> None:
        self.TEST_CONFIG = {
            "openldap_config": self.THIS_DIR + '/../test_data/openldap-test.yaml',
            "ldap_url": "ldap://myldap:3000",
            "users_obj": "inetOrgPerson",
            "groups_obj": "posixGroup",
            "username_attr": "uid",
            "uid_attr": "uidNumber",
            "membership_attr": "o",
            "gid_attr": "gidNumber",
            "inst_id_attr": "cn",
            "inst_name_attr": "description"
        }
        self.test_params = LdapConfig(self.TEST_CONFIG)
        self.under_test = LdapUserService()

    def test_set_up(self):
        self.under_test.set_up(self.test_params)

    def test_set_up_with_missing_config(self):
        del self.TEST_CONFIG['users_obj']
        del self.TEST_CONFIG['ldap_url']
        self.under_test.set_up(self.test_params)

    @patch.object(ldap, 'initialize')
    def test_connect(self, ldap_init_mock):
        ldap_init_mock.return_value = ldap.ldapobject.SimpleLDAPObject('')
        # TODO finish this test

    def test_disconnect(self):
        # Check no errors...
        self.under_test.disconnect()

