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
    "JWT_LONG_RUNNING_REFRESH_TOKEN": True,
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

    def test_refresh_token_before_access_expiry(self):
        # login
        response = self.login(self.user.email, self.PASSWORD)
        (payload, token, refresh_expires_in) = self.validate_login_successful(
            response
        )

        # access token added to client cookies?
        self.assertIn("JWT", self.client.cookies.keys())
        self.assertEqual(self.client.cookies["JWT"].value, token)

        # ...time passes, but the access token has not expired...
        sleep(DELTA_S)

        # refresh to get a new access token:
        # clients (such as the ui) can repeatedly request a
        # new access token in this way, provided the current
        # refresh token has not expired
        # see django-graphql-jwt: https://django-graphql-jwt.domake.io/en/latest/refresh_token.html#single-token-refresh
        response = self.refresh_token()
        (
            new_payload,
            new_token,
            new_refresh_expires_in,
        ) = self.validate_refresh_token_successful(response)

        # access token changed?
        self.assertNotEqual(token, new_token)

        # access token expiry changed?
        self.assertGreater(new_payload["exp"], payload["exp"])

        # (long term) refresh expiry?
        self.assertGreaterEqual(new_refresh_expires_in, refresh_expires_in)

        # new access token added to client cookies?
        self.assertIn("JWT", self.client.cookies.keys())
        self.assertEqual(self.client.cookies["JWT"].value, new_token)

    def test_refresh_token_after_access_expiry(self):
        # login
        response = self.login(self.user.email, self.PASSWORD)
        (payload, token, refresh_expires_in) = self.validate_login_successful(
            response
        )

        # access token added to client cookies?
        self.assertIn("JWT", self.client.cookies.keys())
        self.assertEqual(self.client.cookies["JWT"].value, token)

        # ...time passes, and the access token has expired...
        # ...but the refresh token has not expired...
        sleep(
            TEST_GRAPHQL_JWT["JWT_EXPIRATION_DELTA"].total_seconds() + DELTA_S
        )

        # refresh to get a new access token fails?
        response = self.refresh_token()
        (
            new_payload,
            new_token,
            new_refresh_expires_in,
        ) = self.validate_refresh_token_successful(response)

        # access token changed?
        self.assertNotEqual(token, new_token)

        # access token expiry changed?
        self.assertGreater(new_payload["exp"], payload["exp"])

        # (long term) refresh expiry?
        self.assertGreaterEqual(new_refresh_expires_in, refresh_expires_in)

        # new access token added to client cookies?
        self.assertIn("JWT", self.client.cookies.keys())
        self.assertEqual(self.client.cookies["JWT"].value, new_token)

    def test_refresh_token_after_refresh_expiry(self):
        # login
        response = self.login(self.user.email, self.PASSWORD)
        (payload, token, refresh_expires_in) = self.validate_login_successful(
            response
        )

        # access token added to client cookies?
        self.assertIn("JWT", self.client.cookies.keys())
        self.assertEqual(self.client.cookies["JWT"].value, token)

        # ...time passes, and the access token has expired...
        # ...and the refresh token has also expired...
        sleep(
            TEST_GRAPHQL_JWT["JWT_REFRESH_EXPIRATION_DELTA"].total_seconds()
            + DELTA_S
        )

        # refresh to get a new access token fails?
        response = self.refresh_token()
        self.validate_refresh_token_signature_expired(response)

    def test_new_password_succeeds_after_changing_password(self):
        # login
        response = self.login(self.user.email, self.PASSWORD)
        self.validate_login_successful(response)

        # change password
        new_password = "YOSEMITE"
        response = self.change_password(self.PASSWORD, new_password)

        # login again with new password
        response = self.login(self.user.email, new_password)
        self.validate_login_successful(response)

    def test_old_password_fails_after_changing_password(self):
        # login
        response = self.login(self.user.email, self.PASSWORD)
        self.validate_login_successful(response)

        # change password
        new_password = "YOSEMITE"
        response = self.change_password(self.PASSWORD, new_password)

        # attempt login again with old password
        response = self.login(self.user.email, self.PASSWORD)
        self.validate_unsuccessful(response)
