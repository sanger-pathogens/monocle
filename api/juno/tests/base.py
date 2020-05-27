import json
from django.test import TestCase


class GraphQLTestCase(TestCase):
    """
    Adapted from `graphene_django.utils.testing.GraphQLTestCase`
    """

    # URL to graphql endpoint
    GRAPHQL_URL = "/graphql/"

    def query(
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

    def assertResponseNoErrors(self, resp):
        """
        Assert that the call went through correctly. 200 means the syntax is ok, if there are no `errors`,
        the call was fine.
        :resp HttpResponse: Response
        """
        self.assertEqual(resp.status_code, 200)
        content = json.loads(resp.content)
        self.assertNotIn("errors", list(content.keys()))

    def assertResponseHasErrors(self, resp):
        """
        Assert that the call was failing. Take care: Even with errors, GraphQL returns status 200!
        :resp HttpResponse: Response
        """
        content = json.loads(resp.content)
        self.assertIn("errors", list(content.keys()))


class APITestCase(GraphQLTestCase):
    # common messages
    MSG_ROOT_NOT_AN_OBJECT = "API response should be a JSON object"
    MSG_NO_DATA = "API response has no root data field"
    MSG_FIELD_MISSING = "API response should contain field"
    MSG_VALUE_MISMATCH = "Value in API response differs from value in database"
    MSG_VALUE_EXPECTED_LIST = "Value in API response should be a list type"
    MSG_VALUE_EXPECTED_NONPRIMITIVE_TYPE = (
        "Value in API response should be a non-primitive type (dict)"
    )
    MSG_VALUE_EXPECTED_STRING_TYPE = "Value in API response should be a string"
    MSG_EXPECTED_NONEMPTY_LIST = "Expected non-empty list"

    def validate_successful(self, response):
        # query ok?
        self.assertResponseNoErrors(response)

        # expected content?
        content = json.loads(response.content)
        self.assertIsInstance(content, dict, msg=self.MSG_ROOT_NOT_AN_OBJECT)
        self.assertIn("data", content, msg=self.MSG_NO_DATA)

        # return data for further checks
        return content["data"]

    def validate_unsuccessful(self, response):
        # query ok?
        self.assertResponseHasErrors(response)

        # expected content?
        content = json.loads(response.content)
        self.assertIsInstance(content, dict, msg=self.MSG_ROOT_NOT_AN_OBJECT)

        # return content for further checks
        return content

    def make_and_validate_query(self, queryname, subquery):
        # make query
        response = self.query(
            """
            query {
                %s {
                    %s
                }
            }
            """
            % (queryname, subquery,),
        )

        data = self.validate_successful(response)

        # has the query?
        self.assertIn(
            queryname, data, msg=self.MSG_FIELD_MISSING,
        )
        value = data[queryname]

        # return for further checks
        return value

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

    def login(self, email, password):
        self.query(
            """
            mutation {
                tokenAuth(email:"bob@bob.com", password: "bobsicle") {
                    token
                }
            }
            """,
        )
        # TODO: return token

    def logout(self):
        self.query(
            """
            mutation {
                deleteTokenCookie {
                    deleted
                }
            }
            """,
        )
