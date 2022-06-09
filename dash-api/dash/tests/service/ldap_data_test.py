from unittest import TestCase
from unittest.mock import patch

from dash.api.exceptions import LdapDataError
from DataSources.ldap_data import LdapData
from ldap import SERVER_DOWN

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
MOCK_GID = "any_string"
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

    @patch.object(LdapData, "ldap_search")
    def test_group_search_rejects_multiple_search_results(self, mock_query):
        with self.assertRaises(LdapDataError):
            mock_query.return_value = [MOCK_LDAP_RESULT_GROUP, MOCK_LDAP_RESULT_GROUP]
            self.ldap_data.ldap_search_group_by_gid(MOCK_GID, GROUP_OBJ_CONFIG_KEY)

    @patch.object(LdapData, "ldap_search")
    def test_group_search_rejects_group_record_without_country_name_attribute(self, mock_query):
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
        with self.assertRaises(LdapDataError):
            mock_query.return_value = [mock_ldap_result_group_no_country]
            self.ldap_data.ldap_search_group_by_gid(MOCK_GID, GROUP_OBJ_CONFIG_KEY)

    @patch.object(LdapData, "ldap_search")
    def test_group_search_rejects_group_record_without_description_attribute(self, mock_query):
        MOCK_LDAP_RESULT_GROUP_NO_DESC = (
            "cn=WelSanIns,ou=groups,dc=monocle,dc=dev,dc=pam,dc=sanger,dc=ac,dc=uk",
            {"cn": [b"WelSanIns"], "gidNumber": [b"501"], "objectClass": [b"posixGroup", b"top"], "memberUid": [b"UK"]},
        )
        with self.assertRaises(LdapDataError):
            mock_query.return_value = [MOCK_LDAP_RESULT_GROUP_NO_DESC]
            self.ldap_data.ldap_search_group_by_gid(MOCK_GID, GROUP_OBJ_CONFIG_KEY)

    @patch.object(LdapData, "ldap_search")
    def test_group_search(self, mock_query):
        mock_query.return_value = [MOCK_LDAP_RESULT_GROUP]

        user_ldap_result = self.ldap_data.ldap_search_group_by_gid(MOCK_GID, GROUP_OBJ_CONFIG_KEY)

        self.assertIsInstance(user_ldap_result, tuple)

    def test_low_level_search(self):
        with self.assertRaises(TypeError):
            self.ldap_data.ldap_search("inetOrgPerson", "uid")
        with self.assertRaises(LdapDataError):
            self.ldap_data.ldap_search("inetOrgPerson", "uid", None)
        with self.assertRaises(LdapDataError):
            self.ldap_data.ldap_search("inetOrgPerson", "uid", "")
        with self.assertRaises(SERVER_DOWN):
            self.ldap_data.ldap_search("inetOrgPerson", "uid", "this_is_valid")
