from unittest import TestCase
from unittest.mock import Mock, patch

from dash.api.exceptions import LdapDataError
from DataSources.ldap_data import LdapData
from ldap import SCOPE_SUBTREE

ADDITIONAL_LDAP_CONFIG_KEYS = ["uid_attr"]
TEST_CONFIG = "dash/tests/mock_data/data_sources.yml"
BAD_CONFIG = "dash/tests/mock_data/data_sources_bad.yml"
BAD_OPENLDAP_CONFIG = "dash/tests/mock_data/openldap-bad.yaml"
# in LdapData object variable config (dict of config params), the OpenLDAP params are stored using this key:
OPENLDAP_CONFIG_KEY = "openldap"
OPENLDAP_STRING_PARAMETERS = [
    "LDAP_ORGANISATION",
    "LDAP_DOMAIN",
    "LDAP_ADMIN_PASSWORD",
    "LDAP_CONFIG_PASSWORD",
    "LDAP_READONLY_USER_USERNAME",
    "LDAP_READONLY_USER_PASSWORD",
    "MONOCLE_LDAP_BASE_DN",
    "MONOCLE_LDAP_BIND_DN",
    "MONOCLE_LDAP_BIND_PASSWORD",
]
OPENLDAP_BOOL_PARAMETERS = ["LDAP_READONLY_USER"]

GROUP_OBJ_CONFIG_KEY = "user_group_obj"
MOCK_ID = "any_string"
MOCK_LDAP_OBJECT_CLASS = "posixAccount"
MOCK_LDAP_OBJECT_ATTRIBUTE = "uid"
MOCK_LDAP_RESULT_GROUP = (
    "cn=WelSanIns,ou=groups,dc=monocle,dc=dev,dc=pam,dc=sanger,dc=ac,dc=uk",
    {
        "cn": [b"WelSanIns"],
        "description": [b"Wellcome Sanger Institute"],
        "gidNumber": [b"501"],
        "objectClass": [b"posixGroup", b"top"],
        "memberUid": [b"UK"],
    },
)
MOCK_LDAP_SEARCH_FILTER = "(some string)"
MOCK_REQUIRED_ATTRIBUTES_FOR_GROUP_SEARCH = ["cn"]


class LdapDataTest(TestCase):
    def setUp(self):
        self.ldap_data = LdapData(ADDITIONAL_LDAP_CONFIG_KEYS, set_up=False)
        self.ldap_data.set_up(TEST_CONFIG)

    def test_has_expected_ldap_config(self):
        base_ldap_config_keys = ["openldap_config", "ldap_url"]
        ldap_config_keys = base_ldap_config_keys + ADDITIONAL_LDAP_CONFIG_KEYS
        for ldap_config_key in ldap_config_keys:
            actual_ldap_config_attribute = self.ldap_data.config[ldap_config_key]
            self.assertIsInstance(actual_ldap_config_attribute, str)

        for openldap_string_parameter in OPENLDAP_STRING_PARAMETERS:
            actual_openldap_param_value = self.ldap_data.config[OPENLDAP_CONFIG_KEY][openldap_string_parameter]
            self.assertIsInstance(actual_openldap_param_value, str)

        for openldap_bool_parameter in OPENLDAP_BOOL_PARAMETERS:
            actual_openldap_param_value = self.ldap_data.config[OPENLDAP_CONFIG_KEY][openldap_bool_parameter]
            self.assertIsInstance(actual_openldap_param_value, bool)

    def test_rejects_bad_config(self):
        with self.assertRaises(KeyError):
            doomed = LdapData(ADDITIONAL_LDAP_CONFIG_KEYS, set_up=False)
            doomed.set_up(BAD_CONFIG)

    def test_rejects_missing_config(self):
        with self.assertRaises(FileNotFoundError):
            doomed = LdapData(ADDITIONAL_LDAP_CONFIG_KEYS, set_up=False)
            doomed.set_up("no_such_config.yml")

    def test_rejects_bad_ldap_config(self):
        with self.assertRaises(KeyError):
            doomed = LdapData(ADDITIONAL_LDAP_CONFIG_KEYS, set_up=False)
            doomed.read_openldap_config(BAD_OPENLDAP_CONFIG)

    def test_rejects_missing_ldap_config(self):
        with self.assertRaises(FileNotFoundError):
            doomed = LdapData(ADDITIONAL_LDAP_CONFIG_KEYS, set_up=False)
            doomed.read_openldap_config("no_such.yaml")

    @patch.object(LdapData, "ldap_search_by_attribute_value")
    def test_group_search_rejects_empty_required_attributes(self, mock_query):
        with self.assertRaises(ValueError):
            self.ldap_data.ldap_search_group_by_gid(MOCK_ID, GROUP_OBJ_CONFIG_KEY, None)
        with self.assertRaises(ValueError):
            self.ldap_data.ldap_search_group_by_gid(MOCK_ID, GROUP_OBJ_CONFIG_KEY, [])

    @patch.object(LdapData, "ldap_search_by_attribute_value")
    def test_group_search_rejects_multiple_search_results(self, mock_query):
        with self.assertRaises(LdapDataError):
            mock_query.return_value = [MOCK_LDAP_RESULT_GROUP, MOCK_LDAP_RESULT_GROUP]
            self.ldap_data.ldap_search_group_by_gid(
                MOCK_ID, GROUP_OBJ_CONFIG_KEY, MOCK_REQUIRED_ATTRIBUTES_FOR_GROUP_SEARCH
            )

    @patch.object(LdapData, "ldap_search_by_attribute_value")
    def test_group_search_rejects_group_record_without_required_attribute(self, mock_query):
        mock_ldap_result_group_no_country = (
            "cn=WelSanIns,ou=groups,dc=monocle,dc=dev,dc=pam,dc=sanger,dc=ac,dc=uk",
            {
                "cn": [b"WelSanIns"],
                "description": [b"Wellcome Sanger Institute"],
                "gidNumber": [b"501"],
                "objectClass": [b"posixGroup", b"top"],
                "memberUid": [],
            },
        )
        mock_query.return_value = [mock_ldap_result_group_no_country]

        with self.assertRaises(LdapDataError):
            self.ldap_data.ldap_search_group_by_gid(MOCK_ID, GROUP_OBJ_CONFIG_KEY, ["country"])

    @patch.object(LdapData, "ldap_search_by_attribute_value")
    def test_group_search(self, mock_query):
        mock_query.return_value = [MOCK_LDAP_RESULT_GROUP]

        user_ldap_result = self.ldap_data.ldap_search_group_by_gid(
            MOCK_ID, GROUP_OBJ_CONFIG_KEY, MOCK_REQUIRED_ATTRIBUTES_FOR_GROUP_SEARCH
        )

        self.assertIsInstance(user_ldap_result, tuple)

    def test_ldap_search_by_attribute_value_rejects_on_empty_value(self):
        with self.assertRaises(LdapDataError):
            self.ldap_data.ldap_search_by_attribute_value(MOCK_LDAP_OBJECT_CLASS, MOCK_LDAP_OBJECT_ATTRIBUTE, None)
        with self.assertRaises(LdapDataError):
            self.ldap_data.ldap_search_by_attribute_value(MOCK_LDAP_OBJECT_CLASS, MOCK_LDAP_OBJECT_ATTRIBUTE, "")

    @patch.object(LdapData, "ldap_search")
    def test_ldap_search_by_attribute_value_call_ldap_search_with_expected_search_filter(self, mock_ldap_search):
        self.ldap_data.ldap_search_by_attribute_value(MOCK_LDAP_OBJECT_CLASS, MOCK_LDAP_OBJECT_ATTRIBUTE, MOCK_ID)

        mock_ldap_search.assert_called_once_with(
            f"(&(objectClass={MOCK_LDAP_OBJECT_CLASS})({MOCK_LDAP_OBJECT_ATTRIBUTE}={MOCK_ID}))"
        )

    @patch.object(LdapData, "ldap_search")
    def test_ldap_search_by_attribute_value_returns_result_from_ldap_search(self, mock_ldap_search):
        expected_result = 42
        mock_ldap_search.return_value = expected_result

        actual_result = self.ldap_data.ldap_search_by_attribute_value(
            MOCK_LDAP_OBJECT_CLASS, MOCK_LDAP_OBJECT_ATTRIBUTE, MOCK_ID
        )

        self.assertEqual(expected_result, actual_result)

    @patch.object(LdapData, "connection")
    def test_ldap_search_raises_on_connection_exception(self, mock_connection):
        mock_connection.side_effect = ConnectionError()

        with self.assertRaises(LdapDataError):
            self.ldap_data.ldap_search(MOCK_LDAP_SEARCH_FILTER)

    @patch.object(LdapData, "connection")
    def test_ldap_search_raises_on_library_exception(self, mock_connection):
        mock_ldap_object = Mock()
        mock_ldap_object.search_s.side_effect = ValueError()
        mock_connection.return_value = mock_ldap_object

        with self.assertRaises(LdapDataError):
            self.ldap_data.ldap_search(MOCK_LDAP_SEARCH_FILTER)

    @patch.object(LdapData, "connection")
    def test_ldap_search_calls_ldap_library_search_method_with_expected_search_filter(self, mock_connection):
        mock_ldap_object = Mock()
        mock_connection.return_value = mock_ldap_object

        self.ldap_data.ldap_search(MOCK_LDAP_SEARCH_FILTER)

        mock_ldap_object.search_s.assert_called_once_with(
            self.ldap_data.config["openldap"]["MONOCLE_LDAP_BASE_DN"], SCOPE_SUBTREE, MOCK_LDAP_SEARCH_FILTER
        )

    @patch.object(LdapData, "connection")
    def test_ldap_search_returns_result_from_ldap_library_search_method(self, mock_connection):
        mock_ldap_object = Mock()
        expected_result = 42
        mock_ldap_object.search_s.return_value = expected_result
        mock_connection.return_value = mock_ldap_object

        actual_result = self.ldap_data.ldap_search(MOCK_LDAP_SEARCH_FILTER)

        self.assertEqual(expected_result, actual_result)
