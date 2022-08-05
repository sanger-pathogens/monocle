from unittest import TestCase
from unittest.mock import patch

from DataSources.institution_data import InstitutionData
from DataSources.ldap_data import LdapDataError

LDAP_INSTITUTIONS_SEARCH_RESULT = [
    ("dn1", {"cn": [b"CenQuaRes"], "description": [b"Center for Qualia Research"], "memberUid": [b"US", b"AU"]}),
    ("dn2", {"cn": [b"WelSanIns"], "description": [b"Wellcome Sanger Institute"], "memberUid": [b"UK"]}),
]
TEST_CONFIG = "dash/tests/mock_data/data_sources.yml"


class InstitutionDataTest(TestCase):
    def setUp(self):
        self.institution_data = InstitutionData(set_up=False)
        self.institution_data.set_up(TEST_CONFIG)

    def test_has_expected_additional_required_config_params(self):
        InstitutionData(set_up=False)

        self.assertEqual(
            [
                "institution_group_obj",
                "inst_id_attr",
                "inst_name_attr",
            ],
            self.institution_data.required_config_params[-3:],
        )

    @patch.object(InstitutionData, "ldap_search")
    def test_get_institutions_rejects_on_missing_institution_key(self, mock_ldap_search):
        mock_ldap_search.return_value = [
            ("dn1", {"description": [b"Center for Qualia Research"], "memberUid": [b"US"]})
        ]

        with self.assertRaisesRegex(LdapDataError, "Retrieving institution LDAP data: "):
            self.institution_data.get_all_institutions_regardless_of_user_membership()

    @patch.object(InstitutionData, "ldap_search")
    def test_get_institutions_rejects_on_missing_institution_name(self, mock_ldap_search):
        mock_ldap_search.return_value = [("dn1", {"cn": [b"FakIns"], "memberUid": [b"US"]})]

        with self.assertRaisesRegex(LdapDataError, "Retrieving institution LDAP data: "):
            self.institution_data.get_all_institutions_regardless_of_user_membership()

    @patch.object(InstitutionData, "ldap_search")
    def test_get_institutions_succeeds_with_missing_institution_country(self, mock_ldap_search):
        institution_ldap_data = {"cn": [b"CenQuaRes"], "description": [b"Center for Qualia Research"]}
        mock_ldap_search.return_value = [("dn1", institution_ldap_data)]

        actual_institutions = self.institution_data.get_all_institutions_regardless_of_user_membership()

        self.assertEqual(
            [
                {
                    "key": institution_ldap_data["cn"][0].decode("utf-8"),
                    "name": institution_ldap_data["description"][0].decode("utf-8"),
                }
            ],
            actual_institutions,
        )

    @patch.object(InstitutionData, "ldap_search")
    def test_get_institutions(self, mock_ldap_search):
        mock_ldap_search.return_value = LDAP_INSTITUTIONS_SEARCH_RESULT

        actual_institutions = self.institution_data.get_all_institutions_regardless_of_user_membership()

        self.assertEqual(
            [
                {
                    "key": institution_ldap_tuple[1]["cn"][0].decode("utf-8"),
                    "name": institution_ldap_tuple[1]["description"][0].decode("utf-8"),
                    "countries": list(
                        map(lambda country: country.decode("utf-8"), institution_ldap_tuple[1]["memberUid"])
                    ),
                }
                for institution_ldap_tuple in LDAP_INSTITUTIONS_SEARCH_RESULT
            ],
            actual_institutions,
        )

    @patch.object(InstitutionData, "ldap_search")
    def test_get_institution_keys_rejects_on_none_institutions(self, mock_ldap_search):
        mock_ldap_search.return_value = None

        with self.assertRaises(LdapDataError):
            self.institution_data.get_all_institution_keys_regardless_of_user_membership()

    @patch.object(InstitutionData, "ldap_search")
    def test_get_institution_keys_rejects_on_empty_institution_list(self, mock_ldap_search):
        mock_ldap_search.return_value = None

        with self.assertRaises(LdapDataError):
            self.institution_data.get_all_institution_keys_regardless_of_user_membership()

    @patch.object(InstitutionData, "ldap_search")
    def test_get_institution_keys(self, mock_ldap_search):
        mock_ldap_search.return_value = LDAP_INSTITUTIONS_SEARCH_RESULT

        actual_institution_keys = self.institution_data.get_all_institution_keys_regardless_of_user_membership()

        self.assertEqual(
            [
                institution_ldap_tuple[1]["cn"][0].decode("utf-8")
                for institution_ldap_tuple in LDAP_INSTITUTIONS_SEARCH_RESULT
            ],
            actual_institution_keys,
        )

    @patch.object(InstitutionData, "ldap_search")
    def test_get_institution_names_rejects_on_none_institutions(self, mock_ldap_search):
        mock_ldap_search.return_value = None

        with self.assertRaises(LdapDataError):
            self.institution_data.get_all_institution_names_regardless_of_user_membership()

    @patch.object(InstitutionData, "ldap_search")
    def test_get_institution_names_rejects_on_empty_institution_list(self, mock_ldap_search):
        mock_ldap_search.return_value = None

        with self.assertRaises(LdapDataError):
            self.institution_data.get_all_institution_names_regardless_of_user_membership()

    @patch.object(InstitutionData, "ldap_search")
    def test_get_institution_names(self, mock_ldap_search):
        mock_ldap_search.return_value = LDAP_INSTITUTIONS_SEARCH_RESULT

        actual_institution_names = self.institution_data.get_all_institution_names_regardless_of_user_membership()

        self.assertEqual(
            [
                institution_ldap_tuple[1]["description"][0].decode("utf-8")
                for institution_ldap_tuple in LDAP_INSTITUTIONS_SEARCH_RESULT
            ],
            actual_institution_names,
        )
