import json
import logging
from django.test import TestCase

# Note: There's an usual bug with graphql-core which prints
#       tracebacks for errors thrown and caught in third
#       party code. This just pollutes the test output, so
#       logging level upped. It's likely to be fixed in
#       graphql-core v3, but django-graphql-jwt doesn't
#       support this yet.
# TODO: monitor this and upgrade when possible
#
# https://github.com/graphql-python/graphql-core-legacy/issues/142
logging.getLogger("graphql").setLevel(logging.CRITICAL)


class GraphQLTestCase(TestCase):
    # adapted from `graphene_django.utils.testing.GraphQLTestCase`

    # URL to graphql endpoint
    GRAPHQL_URL = "/graphql/"

    # common messages
    GRAPHQL_JWT_MSG_SIGNATURE_EXPIRED = "Signature has expired"
    GRAPHQL_JWT_MSG_REFRESH_TOKEN_EXPIRED = "Refresh token is expired"
    GRAPHQL_JWT_MSG_BAD_PERMISSIONS = (
        "You do not have permission to perform this action"
    )

    MSG_ROOT_NOT_AN_OBJECT = "API response should be a JSON object"
    MSG_NO_DATA = "API response missing an expected data field"
    MSG_NO_GQL_ERROR = "API response missing an expected error field"
    MSG_GQL_ERROR = "API response has an unexpected error field"
    MSG_FIELD_MISSING = "API response missing an expected field"
    MSG_VALUE_MISMATCH = "Value in API response differs from value in database"
    MSG_VALUE_EXPECTED_LIST = "Value in API response should be a list type"
    MSG_VALUE_EXPECTED_NONPRIMITIVE_TYPE = (
        "Value in API response should be a non-primitive type (dict)"
    )
    MSG_VALUE_EXPECTED_STRING_TYPE = "Value in API response should be a string"
    MSG_EXPECTED_NONEMPTY_LIST = "Expected non-empty list"
    MSG_EXPECTED_STATUS_200 = "Expected API response to have status code 200"

    def post(
        self,
        query,
        op_name=None,
        input_data=None,
        variables=None,
        headers=None,
    ):
        """
        Args:
            query (string)    - GraphQL query to run
            op_name (string)  - If the query is a mutation or named query, you must
                                supply the op_name.  For annon queries ("{ ... }"),
                                should be None (default).
            input_data (dict) - If provided, the $input variable in GraphQL will be set
                                to this value. If both ``input_data`` and ``variables``,
                                are provided, the ``input`` field in the ``variables``
                                dict will be overwritten with this value.
            variables (dict)  - If provided, the "variables" field in GraphQL will be
                                set to this value.
            headers (dict)    - If provided, the headers in POST request to GRAPHQL_URL
                                will be set to this value.
        Returns:
            Response object from client
        """
        body = {"query": query}
        if op_name:
            body["operationName"] = op_name
        if variables:
            body["variables"] = variables
        if input_data:
            if variables in body:
                body["variables"]["input"] = input_data
            else:
                body["variables"] = {"input": input_data}
        if headers:
            resp = self.client.post(
                self.GRAPHQL_URL,
                json.dumps(body),
                content_type="application/json",
                **headers
            )
        else:
            resp = self.client.post(
                self.GRAPHQL_URL,
                json.dumps(body),
                content_type="application/json",
            )
        return resp

    def make_query(self, queryname, subquery):
        # make query
        response = self.post(
            """
            query {
                %s {
                    %s
                }
            }
            """
            % (queryname, subquery,),
        )

        # return response for further checks
        return response

    def validate_response_has_no_errors(self, response):
        # http errors?
        self.assertEqual(
            response.status_code, 200, msg=self.MSG_EXPECTED_STATUS_200
        )

        # json body?
        content = json.loads(response.content)

        # return content for further checks
        return content

    def validate_has_no_graphql_errors(self, content):
        # GraphQL errors?
        self.assertNotIn("errors", content.keys(), msg=self.MSG_GQL_ERROR)

    def validate_has_graphql_errors(self, content):
        # GraphQL errors?
        self.assertIn("errors", content.keys(), msg=self.MSG_NO_GQL_ERROR)

        # return errors for further checks
        return content["errors"]

    def validate_successful(self, response):
        # query ok?
        content = self.validate_response_has_no_errors(response)
        self.validate_has_no_graphql_errors(content)

        # expected content?
        content = json.loads(response.content)
        self.assertIsInstance(content, dict, msg=self.MSG_ROOT_NOT_AN_OBJECT)
        self.assertIn("data", content, msg=self.MSG_NO_DATA)

        # return data for further checks
        return content["data"]

    def validate_unsuccessful(self, response):
        # query ok?
        content = self.validate_response_has_no_errors(response)
        self.validate_has_graphql_errors(content)

        # expected content?
        content = json.loads(response.content)
        self.assertIsInstance(content, dict, msg=self.MSG_ROOT_NOT_AN_OBJECT)

        # return content for further checks
        return content

    def validate_field(self, parent, fieldname, expected_value=None):
        # parent in response an object?
        self.assertIsInstance(
            parent, dict, msg=self.MSG_VALUE_EXPECTED_NONPRIMITIVE_TYPE
        )

        # parent has the field?
        self.assertIn(fieldname, parent, msg=self.MSG_FIELD_MISSING)

        # potentially check the value, but return for further checks
        value = parent[fieldname]
        if expected_value is not None:
            self.assertEqual(value, expected_value, self.MSG_VALUE_MISMATCH)

        return value

    def validate_non_empty_list(self, expected_list):
        self.assertIsInstance(
            expected_list, list, msg=self.MSG_VALUE_EXPECTED_LIST
        )
        self.assertGreater(
            len(expected_list), 0, msg=self.MSG_EXPECTED_NONEMPTY_LIST
        )


class AuthenticatableGraphQLTestCase(GraphQLTestCase):
    def login(self, email, password):
        response = self.post(
            """
            mutation Login($email: String!, $password: String!) {
                tokenAuth(email: $email, password: $password) {
                    payload
                    token
                    refreshExpiresIn
                }
            }
            """,
            op_name="Login",
            variables={"email": email, "password": password},
        )

        return response

    def logout(self):
        response = self.post(
            """
            mutation Logout {
                deleteTokenCookie {
                    deleted
                }
            }
            """,
            op_name="Logout",
        )

        return response

    def refresh_token(self):
        response = self.post(
            """
            mutation RefreshToken {
                refreshToken {
                    payload
                    token
                    refreshExpiresIn
                }
            }
            """,
            op_name="RefreshToken",
        )

        return response

    def change_password(self, old_password, new_password):
        response = self.post(
            """
            mutation ChangePassword($old_password: String!, $new_password: String!) {
                changePassword(oldPassword: $old_password, newPassword: $new_password) {
                    committed
                }
            }
            """,
            op_name="ChangePassword",
            variables={
                "old_password": old_password,
                "new_password": new_password,
            },
        )

        return response

    def validate_login_successful(self, response):
        data = self.validate_successful(response)
        token_auth = self.validate_field(data, "tokenAuth")
        payload = self.validate_field(token_auth, "payload")
        token = self.validate_field(token_auth, "token")
        refresh_expires_in = self.validate_field(
            token_auth, "refreshExpiresIn"
        )

        return (payload, token, refresh_expires_in)

    def validate_refresh_token_successful(self, response):
        data = self.validate_successful(response)
        refresh_token = self.validate_field(data, "refreshToken")
        payload = self.validate_field(refresh_token, "payload")
        token = self.validate_field(refresh_token, "token")
        refresh_expires_in = self.validate_field(
            refresh_token, "refreshExpiresIn"
        )

        return (payload, token, refresh_expires_in)

    def validate_refresh_token_signature_expired(self, response):
        content = self.validate_unsuccessful(response)
        errors = self.validate_field(content, "errors")
        self.assertTrue(
            any(
                "message" in e.keys()
                and e["message"] == self.GRAPHQL_JWT_MSG_REFRESH_TOKEN_EXPIRED
                for e in errors
            )
        )
