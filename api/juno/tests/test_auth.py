from time import sleep
from datetime import timedelta
from django.test import override_settings

from juno.api.models import User
from juno.tests.base import AuthenticatableGraphQLTestCase

DELTA_MS = 1000
DELTA_S = DELTA_MS / 1000

TEST_GRAPHQL_JWT = {
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_EXPIRATION_DELTA": timedelta(milliseconds=2 * DELTA_MS),
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(milliseconds=5 * DELTA_MS),
}


@override_settings(GRAPHQL_JWT=TEST_GRAPHQL_JWT)
class AuthTestCase(AuthenticatableGraphQLTestCase):
    PASSWORD = "bobsicles"

    def setUp(self):
        # put something in the db
        self.user = User.objects.create(
            email="bob@bob.com", first_name="Bob", last_name="Bobbity",
        )
        self.user.set_password(self.PASSWORD)
        self.user.save()

    def test_refresh_token_before_expiry(self):
        # login
        response = self.login(self.user.email, self.PASSWORD)
        (payload, token, refresh_expires_in) = self.validate_login_successful(
            response
        )

        # access token added to client cookies?
        self.assertIn("JWT", self.client.cookies.keys())
        self.assertEqual(self.client.cookies["JWT"].value, token)

        # ...time passes, but the token has not expired...
        sleep(DELTA_S)

        # refresh to get a new access token:
        # clients (such as the ui) can repeatedly request a
        # new access token in this way, provided the current
        # one has not expired
        # see django-graphql-jwt: https://django-graphql-jwt.domake.io/en/latest/refresh_token.html#single-token-refresh
        response = self.refresh_token(token)
        (
            new_payload,
            new_token,
            new_refresh_expires_in,
        ) = self.validate_refresh_token_successful(response)

        # access token changed?
        self.assertNotEqual(token, new_token)

        # access token expiry changed?
        self.assertGreater(new_payload["exp"], payload["exp"])

        # (long term) refresh expiry unchanged?
        self.assertEqual(new_refresh_expires_in, refresh_expires_in)

        # new access token added to client cookies?
        self.assertIn("JWT", self.client.cookies.keys())
        self.assertEqual(self.client.cookies["JWT"].value, new_token)

    def test_refresh_token_after_expiry(self):
        # login
        response = self.login(self.user.email, self.PASSWORD)
        (payload, token, refresh_expires_in) = self.validate_login_successful(
            response
        )

        # access token added to client cookies?
        self.assertIn("JWT", self.client.cookies.keys())
        self.assertEqual(self.client.cookies["JWT"].value, token)

        # ...time passes, and the token has expired...
        sleep(
            TEST_GRAPHQL_JWT["JWT_EXPIRATION_DELTA"].total_seconds() + DELTA_S
        )

        # refresh to get a new access token fails?
        response = self.refresh_token(token)
        self.validate_refresh_token_signature_expired(response)
