import unittest
from flask import Config
from dash.api.configuration import read_ldap_config


class TestConfiguration(unittest.TestCase):
    """ Test class for the configuration module """

    def test_read_ldap_config(self):
        config = Config(None, defaults={"monocle_ldap": {"key1": "value1", "key2": "value2"}})
        result = read_ldap_config(config)
        self.assertEqual(len(result), 2)
        self.assertEqual(result['key1'], 'value1')
        self.assertEqual(result['key2'], 'value2')

    def test_read_ldap_config_with_error(self):
        config = Config(None, defaults={"some_other_key": {"key1": "value1", "key2": "value2"}})
        with self.assertRaises(KeyError):
            read_ldap_config(config)

