import json
from django.test import TestCase


class GraphQLTestCase(TestCase):
    # adapted from `graphene_django.utils.testing.GraphQLTestCase`

    # URL to graphql endpoint
    GRAPHQL_URL = "/graphql/"

    # common messages
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
                    token
                }
            }
            """,
            op_name="Login",
            variables={"email": email, "password": password},
        )

        data = self.validate_successful(response)
        token_auth = self.validate_field(data, "tokenAuth")
        token = self.validate_field(token_auth, "token")

        return token

    def logout(self):
        self.post(
            """
            mutation Logout {
                deleteTokenCookie {
                    deleted
                }
            }
            """,
        )
