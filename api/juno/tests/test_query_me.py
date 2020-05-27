from juno.api.models import User
from juno.tests.base import APITestCase


class MeQueryTestCase(APITestCase):
    def setUp(self):
        # put something in the db
        self.user = User.objects.create(
            email="bob@bob.com", first_name="Bob", last_name="Bobbity",
        )
        self.user.set_password("bobsicle")
        self.user.save()

    def make_me_query(self, subquery):
        # call api
        return self.query(
            """
            query {
                me {
                    %s
                }
            }
            """
            % subquery,
        )

    def test_has_field_email_when_logged_in(self):
        # auth
        self.login(self.user.email, self.user.password)

        # query
        response = self.make_me_query("email")
        data = self.validate_successful(response)
        me = self.validate_field(data, "me")
        self.validate_field(me, "email", expected_value=self.user.email)
