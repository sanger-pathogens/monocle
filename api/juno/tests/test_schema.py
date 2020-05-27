import json
from django.test import TestCase

from juno.schema import schema
from juno.api.models import Sample, Institution, User


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


class SamplesQueryTestCase(APITestCase):
    def setUp(self):
        # put something in the db
        self.institution = Institution.objects.create(
            name="Wellcome Sanger Institute",
            country="United Kingdom",
            latitude=52.083333,
            longitude=0.183333,
        )
        self.sample = Sample.objects.create(
            lane_id="31663_7#113",
            sample_id="5903STDY8059170",
            public_name="CUHK_GBS177WT_16",
            serotype="Ia",
            host_status="skin and soft-tissue infection",
            submitting_institution=self.institution,
        )

    def make_and_validate_samples_query(self, subquery):
        # call api
        samples = self.make_and_validate_query("samples", subquery)

        # check non-empty
        self.validate_non_empty_list(samples)

        # return samples
        return samples

    def test_has_field_lane_id(self):
        samples = self.make_and_validate_samples_query("laneId")
        self.validate_field(
            samples[0], "laneId", expected_value=self.sample.lane_id,
        )

    def test_has_field_sample_id(self):
        samples = self.make_and_validate_samples_query("sampleId")
        self.validate_field(
            samples[0], "sampleId", expected_value=self.sample.sample_id,
        )

    def test_has_field_public_name(self):
        samples = self.make_and_validate_samples_query("publicName")
        self.validate_field(
            samples[0], "publicName", expected_value=self.sample.public_name,
        )

    def test_has_field_serotype(self):
        samples = self.make_and_validate_samples_query("serotype")
        self.validate_field(
            samples[0], "serotype", expected_value="IA",
        )

    def test_has_field_host_status(self):
        samples = self.make_and_validate_samples_query("hostStatus")
        self.validate_field(
            samples[0],
            "hostStatus",
            expected_value="SKIN_AND_SOFT_TISSUE_INFECTION",
        )

    def test_has_field_submitting_institution(self):
        samples = self.make_and_validate_samples_query(
            """
            submittingInstitution {
                name
            }
            """,
        )
        self.validate_non_empty_list(samples)
        submitting_institution = self.validate_field(
            samples[0], "submittingInstitution"
        )
        self.validate_field(
            submitting_institution,
            "name",
            expected_value=self.institution.name,
        )


class InstitutionsQueryTestCase(APITestCase):
    def setUp(self):
        # put something in the db
        self.institution = Institution.objects.create(
            name="Wellcome Sanger Institute",
            country="United Kingdom",
            latitude=52.083333,
            longitude=0.183333,
        )

    def make_and_validate_institutions_query(self, subquery):
        # call api
        institutions = self.make_and_validate_query("institutions", subquery)

        # check non-empty
        self.validate_non_empty_list(institutions)

        # return institutions
        return institutions

    def test_has_field_name(self):
        institutions = self.make_and_validate_institutions_query("name")
        self.validate_field(
            institutions[0], "name", expected_value=self.institution.name,
        )

    def test_has_latitude(self):
        institutions = self.make_and_validate_institutions_query("latitude")
        self.validate_field(
            institutions[0],
            "latitude",
            expected_value=self.institution.latitude,
        )

    def test_has_longitude(self):
        institutions = self.make_and_validate_institutions_query("longitude")
        self.validate_field(
            institutions[0],
            "longitude",
            expected_value=self.institution.longitude,
        )

    def test_has_field_country(self):
        institutions = self.make_and_validate_institutions_query("country")
        self.validate_field(
            institutions[0],
            "country",
            expected_value=self.institution.country,
        )


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
