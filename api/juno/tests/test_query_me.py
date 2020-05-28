from juno.api.models import User
from juno.tests.base import AuthenticatableGraphQLTestCase


class MeQueryTestCase(AuthenticatableGraphQLTestCase):
    PASSWORD = "bobsicles"

    def setUp(self):
        # put something in the db
        self.user = User.objects.create(
            email="bob@bob.com", first_name="Bob", last_name="Bobbity",
        )
        self.user.set_password(self.PASSWORD)
        self.user.save()

    def make_me_query(self, subquery):
        # call api
        return self.make_query("me", subquery)

    def test_has_field_email_when_logged_in(self):
        # auth
        self.login(self.user.email, self.PASSWORD)

        # query
        response = self.make_me_query("email")

        # check
        data = self.validate_successful(response)
        me = self.validate_field(data, "me")
        self.validate_field(me, "email", expected_value=self.user.email)

    def test_has_no_field_email_when_not_logged_in(self):
        # query
        response = self.make_me_query("email")

        # check
        content = self.validate_unsuccessful(response)
        if "data" in content.keys() and "me" in content["data"].keys():
            self.assertEqual(content["data"]["me"], None)

    def test_has_no_field_email_when_logged_out(self):
        # auth
        self.login(self.user.email, self.PASSWORD)
        self.logout()

        # query
        response = self.make_me_query("email")

        # check
        content = self.validate_unsuccessful(response)
        if "data" in content.keys() and "me" in content["data"].keys():
            self.assertEqual(content["data"]["me"], None)
