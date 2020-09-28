from juno.api.models import User, Institution, Affiliation
from juno.tests.base import AuthenticatableGraphQLTestCase


class MeQueryTestCase(AuthenticatableGraphQLTestCase):
    PASSWORD = "bobsicles"

    def setUp(self):
        # put an institution in the db
        self.institution = Institution.objects.create(
            name="Wellcome Sanger Institute",
            country="United Kingdom",
            latitude=52.083333,
            longitude=0.183333,
        )

        # put user in the db
        self.user = User.objects.create(
            email="bob@bob.com", first_name="Bob", last_name="Bobbity",
        )
        self.user.set_password(self.PASSWORD)
        self.user.save()

        # associate the user with the institution
        Affiliation.objects.create(
            user=self.user, institution=self.institution
        )

    def make_me_query(self, subquery):
        # call api
        return self.make_query("me", subquery)

    def test_has_field_email_when_logged_in(self):
        # auth
        response = self.login(self.user.email, self.PASSWORD)
        self.validate_login_successful(response)

        # query
        response = self.make_me_query("email")

        # check
        data = self.validate_successful(response)
        me = self.validate_field(data, "me")
        self.validate_field(me, "email", expected_value=self.user.email)

    def test_has_field_affiliations_name_when_logged_in(self):
        # auth
        response = self.login(self.user.email, self.PASSWORD)
        self.validate_login_successful(response)

        # query
        response = self.make_me_query(
            """
            affiliations {
                name
            }
            """,
        )

        # check
        data = self.validate_successful(response)
        me = self.validate_field(data, "me")
        affiliations = self.validate_field(me, "affiliations")
        self.assertEqual(len(affiliations), 1)
        self.validate_field(
            affiliations[0], "name", expected_value=self.institution.name,
        )

    def test_has_no_field_me_when_not_logged_in(self):
        # query
        response = self.make_me_query("email")

        # check
        content = self.validate_unsuccessful(response)
        if "data" in content.keys():
            self.assertEqual(content["data"], None)

    def test_has_no_field_me_when_logged_out(self):
        # auth
        response = self.login(self.user.email, self.PASSWORD)
        self.validate_login_successful(response)
        self.logout()

        # query
        response = self.make_me_query("email")

        # check
        content = self.validate_unsuccessful(response)
        if "data" in content.keys():
            self.assertEqual(content["data"], None)
