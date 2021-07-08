import unittest
from flask import Config
from dash.api.dependencies import ApiModule
from dash.api.configuration import LDAP_CONFIG_KEY
from dash.api.user.ldap_user_service import LdapUserService


class TestApiModule(unittest.TestCase):
    """ Test class for the dependencies module """

    def setUp(self):
        self.under_test = ApiModule()

    def test_user_service(self):
        config = Config(None, defaults={LDAP_CONFIG_KEY: ""})
        service = self.under_test.user_service(config)
        self.assertIsInstance(service, LdapUserService)
