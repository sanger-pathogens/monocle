from juno.tests.base import AuthenticatableGraphQLTestCase
from juno.api.models import Institution, User, Affiliation


class InstitutionsQueryTestCase(AuthenticatableGraphQLTestCase):
    def setUp(self):
        # put several institutions in the db
        self.institution_sanger = Institution.objects.create(
            name="Wellcome Sanger Institute",
            country="United Kingdom",
            latitude=52.083333,
            longitude=0.183333,
        )
        self.institution_other = Institution.objects.create(
            name="Monsters Inc",
            country="Unknown",
            latitude=34.3,
            longitude=170.6,
        )
        self.institution_another = Institution.objects.create(
            name="Skynet",
            country="United States",
            latitude=44.3,
            longitude=223.2,
        )

        # put several users in the db
        self.user_sanger = User.objects.create(
            email="jane@sanger.ac.uk", first_name="Jane", last_name="Seymour",
        )
        self.password_sanger = "janesicles"
        self.user_sanger.set_password(self.password_sanger)
        self.user_sanger.save()
        self.user_other = User.objects.create(
            email="bob@bob.com", first_name="Bob", last_name="Bobbity",
        )
        self.password_other = "bobsicles"
        self.user_other.set_password(self.password_other)
        self.user_other.save()

        # associate the users with the institutions
        Affiliation.objects.create(
            user=self.user_sanger, institution=self.institution_sanger
        )
        Affiliation.objects.create(
            user=self.user_other, institution=self.institution_other
        )

    def make_and_validate_institutions_query(self, subquery):
        # call api
        response = self.make_query("institutions", subquery)
        data = self.validate_successful(response)
        institutions = self.validate_field(data, "institutions")

        # check non-empty
        self.validate_non_empty_list(institutions)

        # return institutions
        return institutions

    def test_non_authenticated_user_cannot_view_institutions(self):
        # call api
        response = self.make_query("institutions", "name")

        # checks
        content = self.validate_unsuccessful(response)
        errors = self.validate_has_graphql_errors(content)
        self.assertTrue(
            any(
                e["message"] == self.GRAPHQL_JWT_MSG_BAD_PERMISSIONS
                for e in errors
            )
        )
        if (
            "data" in content.keys()
            and content["data"]
            and "institutions" in content["data"].keys()
        ):
            self.assertEqual(content["data"]["institutions"], None)

    def test_non_sanger_user_can_view_restricted_institutions(self):
        # login as non-sanger user
        response = self.login(self.user_other.email, self.password_other)
        self.validate_login_successful(response)

        # call api
        institutions = self.make_and_validate_institutions_query("name")

        # checks
        self.assertEqual(len(institutions), 1)
        self.validate_field(
            institutions[0],
            "name",
            expected_value=self.institution_other.name,
        )

    def test_sanger_user_can_view_all_institutions(self):
        # login as sanger user
        response = self.login(self.user_sanger.email, self.password_sanger)
        self.validate_login_successful(response)

        # call api
        institutions = self.make_and_validate_institutions_query("name")

        # checks
        self.assertEqual(len(institutions), 3)
        self.validate_field(
            institutions[0],
            "name",
            expected_value=self.institution_sanger.name,
        )
        self.validate_field(
            institutions[1],
            "name",
            expected_value=self.institution_other.name,
        )
        self.validate_field(
            institutions[2],
            "name",
            expected_value=self.institution_another.name,
        )
