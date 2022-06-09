import logging
from unittest import TestCase
from unittest.mock import call, patch

from dash.api.exceptions import LdapDataError
from DataSources.user_data import UserAuthentication, UserData

logging.basicConfig(format="%(asctime)-15s %(levelname)s:  %(message)s", level="CRITICAL")


class MonocleUserAuthenticationTest(TestCase):
    def setUp(self):
        self.userauth = UserAuthentication()

    def test_get_auth_token_ascii(self):
        mock_username = "test_user"
        mock_password = "test_password"
        expected_token = "dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ="
        actual_token = self.userauth.get_auth_token(mock_username, mock_password, encoding="ascii")
        self.assertEqual(expected_token, actual_token)

    def test_get_auth_token_utf8(self):
        mock_username = "test_user"
        mock_password = "test_p\xc3ssword"
        expected_token = "dGVzdF91c2VyOnRlc3RfcMODc3N3b3Jk"
        actual_token = self.userauth.get_auth_token(mock_username, mock_password)
        self.assertEqual(expected_token, actual_token)

    def test_get_username_from_token_ascii(self):
        mock_token = "dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ="
        expected_username = "test_user"
        actual_username = self.userauth.get_username_from_token(mock_token, encoding="ascii")
        self.assertEqual(expected_username, actual_username)

    def test_get_username_from_token_utf8(self):
        mock_token = "dGVzdF91c2VyOnRlc3RfcMODc3N3b3Jk"
        expected_username = "test_user"
        actual_username = self.userauth.get_username_from_token(mock_token)
        self.assertEqual(expected_username, actual_username)


class MonocleUserDataTest(TestCase):

    test_config = "dash/tests/mock_data/data_sources.yml"
    expected_config_keys = [
        "openldap_config",
        "ldap_url",
        "users_obj",
        "user_group_obj",
        "country_names_attr",
        "username_attr",
        "uid_attr",
        "membership_attr",
        "project_attr",
        "gid_attr",
        "inst_id_attr",
        "inst_name_attr",
        "employee_type_attr",
    ]

    mock_ldap_result_user = (
        "cn=mock_user_sanger_ac_uk,ou=users,dc=monocle,dc=pam,dc=sanger,dc=ac,dc=uk",
        {
            "cn": [b"mock_user_sanger_ac_uk"],
            "gidNumber": [b"501"],
            "homeDirectory": [b"/home/users/tmock_user_sanger_ac_uk"],
            "mail": [b"mock_user@sanger.ac.uk"],
            "o": [b"501", b"502"],
            "objectClass": [b"inetOrgPerson", b"posixAccount", b"top"],
            "sn": [b"mock_user_sanger_ac_uk"],
            "uid": [b"mock_user"],
            "uidNumber": [b"1000"],
            "businessCategory": [b"juno"],
            "employeeType": [b"admin"],
        },
    )
    mock_ldap_result_user_no_businessCategory = (
        "cn=mock_user_sanger_ac_uk,ou=users,dc=monocle,dc=pam,dc=sanger,dc=ac,dc=uk",
        {
            "cn": [b"mock_user_sanger_ac_uk"],
            "gidNumber": [b"501"],
            "homeDirectory": [b"/home/users/tmock_user_sanger_ac_uk"],
            "mail": [b"mock_user@sanger.ac.uk"],
            "o": [b"501", b"502"],
            "objectClass": [b"inetOrgPerson", b"posixAccount", b"top"],
            "sn": [b"mock_user_sanger_ac_uk"],
            "uid": [b"mock_user_no_projects"],
            "uidNumber": [b"1000"],
            "employeeType": [b"admin"],
        },
    )
    mock_ldap_result_user_empty_businessCategory = (
        "cn=mock_user_sanger_ac_uk,ou=users,dc=monocle,dc=pam,dc=sanger,dc=ac,dc=uk",
        {
            "cn": [b"mock_user_sanger_ac_uk"],
            "gidNumber": [b"501"],
            "homeDirectory": [b"/home/users/tmock_user_sanger_ac_uk"],
            "mail": [b"mock_user@sanger.ac.uk"],
            "o": [b"501", b"502"],
            "objectClass": [b"inetOrgPerson", b"posixAccount", b"top"],
            "sn": [b"mock_user_sanger_ac_uk"],
            "uid": [b"mock_user_empty_projects"],
            "uidNumber": [b"1000"],
            "businessCategory": [],
            "employeeType": [b"admin"],
        },
    )
    mock_ldap_result_user_no_type = (
        "cn=mock_user_sanger_ac_uk,ou=users,dc=monocle,dc=pam,dc=sanger,dc=ac,dc=uk",
        {
            "cn": [b"mock_user_sanger_ac_uk"],
            "gidNumber": [b"501"],
            "homeDirectory": [b"/home/users/tmock_user_sanger_ac_uk"],
            "mail": [b"mock_user@sanger.ac.uk"],
            "o": [b"501", b"502"],
            "objectClass": [b"inetOrgPerson", b"posixAccount", b"top"],
            "sn": [b"mock_user_sanger_ac_uk"],
            "uid": [b"mock_user_no_type"],
            "uidNumber": [b"1000"],
            "businessCategory": [b"juno"],
        },
    )
    mock_ldap_result_user_no_o = (
        "cn=mock_user_sanger_ac_uk,ou=users,dc=monocle,dc=pam,dc=sanger,dc=ac,dc=uk",
        {
            "cn": [b"mock_user_sanger_ac_uk"],
            "gidNumber": [b"501"],
            "homeDirectory": [b"/home/users/tmock_user_sanger_ac_uk"],
            "mail": [b"mock_user@sanger.ac.uk"],
            "objectClass": [b"inetOrgPerson", b"posixAccount", b"top"],
            "sn": [b"mock_user_sanger_ac_uk"],
            "uid": [b"mock_user_no_o"],
            "uidNumber": [b"1000"],
            "businessCategory": [b"juno"],
        },
    )
    mock_ldap_result_user_empty_o = (
        "cn=mock_user_sanger_ac_uk,ou=users,dc=monocle,dc=pam,dc=sanger,dc=ac,dc=uk",
        {
            "cn": [b"mock_user_sanger_ac_uk"],
            "gidNumber": [b"501"],
            "homeDirectory": [b"/home/users/tmock_user_sanger_ac_uk"],
            "mail": [b"mock_user@sanger.ac.uk"],
            "o": [],
            "objectClass": [b"inetOrgPerson", b"posixAccount", b"top"],
            "sn": [b"mock_user_sanger_ac_uk"],
            "uid": [b"mock_user_empty_o"],
            "uidNumber": [b"1000"],
            "businessCategory": [b"juno"],
        },
    )
    mock_ldap_result_group = (
        "cn=WelSanIns,ou=groups,dc=monocle,dc=dev,dc=pam,dc=sanger,dc=ac,dc=uk",
        {
            "cn": [b"WelSanIns"],
            "description": [b"Wellcome Sanger Institute"],
            "gidNumber": [b"501"],
            "objectClass": [b"posixGroup", b"top"],
            "memberUid": [b"UK"],
        },
    )

    def setUp(self):
        self.user_data = UserData(set_up=False)
        self.user_data.set_up(self.test_config)

    def test_init(self):
        for expected_config_key in self.expected_config_keys:
            expected_config_value = self.user_data.config[expected_config_key]
            self.assertIsInstance(expected_config_value, str)

    @patch.object(UserData, "ldap_search")
    def test_user_search(self, mock_query):
        # reject multiple search results
        with self.assertRaises(LdapDataError):
            mock_query.return_value = [self.mock_ldap_result_user, self.mock_ldap_result_user]
            user_ldap_result = self.user_data.ldap_search_user_by_username("any_valid_string")
        # reject user record not group record
        with self.assertRaises(LdapDataError):
            mock_query.return_value = [self.mock_ldap_result_group]
            user_ldap_result = self.user_data.ldap_search_user_by_username("any_valid_string")
        # reject user record without required attributes
        with self.assertRaises(LdapDataError):
            mock_query.return_value = [self.mock_ldap_result_user_no_businessCategory]
            user_ldap_result = self.user_data.ldap_search_user_by_username("any_valid_string")
        with self.assertRaises(LdapDataError):
            mock_query.return_value = [self.mock_ldap_result_user_no_o]
            user_ldap_result = self.user_data.ldap_search_user_by_username("any_valid_string")
        # TODO this method needs more validation
        mock_query.return_value = [self.mock_ldap_result_user]
        user_ldap_result = self.user_data.ldap_search_user_by_username("any_valid_string")
        self.assertIsInstance(user_ldap_result, tuple)

    @patch.object(UserData, "ldap_search_group_by_gid")
    @patch.object(UserData, "ldap_search_user_by_username")
    def test_get_user_details(self, mock_user_query, mock_group_query):
        # reject search that finds no user (should never happen: search should only be done after authentication)
        with self.assertRaises(LdapDataError):
            mock_user_query.return_value = None
            mock_group_query.return_value = self.mock_ldap_result_group
            user_details = self.user_data.get_user_details("mock_does_not_exist")
        # reject user record with uid attribute that doesn't match search term
        with self.assertRaises(LdapDataError):
            mock_user_query.return_value = self.mock_ldap_result_user
            mock_group_query.return_value = self.mock_ldap_result_group
            user_details = self.user_data.get_user_details("some_other_user")
        # reject user record with empty project attribute
        with self.assertRaises(LdapDataError):
            mock_user_query.return_value = self.mock_ldap_result_user_empty_businessCategory
            mock_group_query.return_value = self.mock_ldap_result_group
            user_details = self.user_data.get_user_details("mock_user_empty_projects")
        # reject user record with empty membership attribute
        with self.assertRaises(LdapDataError):
            mock_user_query.return_value = self.mock_ldap_result_user_empty_o
            mock_group_query.return_value = self.mock_ldap_result_group
            user_details = self.user_data.get_user_details("mock_user_empty_o")
        # reject user record with membership of non-existent group
        with self.assertRaises(LdapDataError):
            mock_user_query.return_value = self.mock_ldap_result_user
            mock_group_query.return_value = None
            user_details = self.user_data.get_user_details("mock_user")
        # now test a working search, to check data returned are correct
        mock_user_query.return_value = self.mock_ldap_result_user
        mock_group_query.return_value = self.mock_ldap_result_group
        user_details = self.user_data.get_user_details("mock_user")
        # data structure
        self.assertIsInstance(user_details, dict)
        self.assertIsInstance(user_details["username"], str)
        self.assertIsInstance(user_details["type"], str)
        self.assertIsInstance(user_details["memberOf"], list)
        self.assertIsInstance(user_details["memberOf"][0], dict)
        self.assertIsInstance(user_details["memberOf"][0]["inst_id"], str)
        self.assertIsInstance(user_details["memberOf"][0]["inst_name"], str)
        self.assertIsInstance(user_details["memberOf"][0]["country_names"], list)
        # data values
        self.assertEqual("mock_user", user_details["username"])
        self.assertEqual("admin", user_details["type"])
        self.assertEqual("WelSanIns", user_details["memberOf"][0]["inst_id"])
        self.assertEqual("Wellcome Sanger Institute", user_details["memberOf"][0]["inst_name"])
        self.assertEqual(["UK"], user_details["memberOf"][0]["country_names"])

    @patch.object(UserData, "ldap_search_group_by_gid")
    @patch.object(UserData, "ldap_search_user_by_username")
    def test_get_user_details_calls_group_search_with_expected_args(self, mock_user_query, mock_group_query):
        mock_user_query.return_value = self.mock_ldap_result_user
        mock_group_query.return_value = self.mock_ldap_result_group

        self.user_data.get_user_details("mock_user")

        expected_group_object_config_key = "user_group_obj"
        expected_group_search_calls = [
            call(org_gid_bytes.decode("UTF-8"), expected_group_object_config_key)
            for org_gid_bytes in self.mock_ldap_result_user[1]["o"]
        ]
        mock_group_query.assert_has_calls(expected_group_search_calls)

    @patch.object(UserData, "ldap_search_group_by_gid")
    @patch.object(UserData, "ldap_search_user_by_username")
    def test_get_user_details_no_employee_type(self, mock_user_query, mock_group_query):
        mock_user_query.return_value = self.mock_ldap_result_user_no_type
        mock_group_query.return_value = self.mock_ldap_result_group
        user_details = self.user_data.get_user_details("mock_user_no_type")
        self.assertEqual("mock_user_no_type", user_details["username"])
        with self.assertRaises(KeyError):
            user_details["type"]
