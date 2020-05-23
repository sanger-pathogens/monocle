import json
from graphene_django.utils.testing import GraphQLTestCase

from juno.schema import schema
from juno.api.models import Sample, Institution


class EmptyDatabaseSchemaTest(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema

    def test_query_samples(self):
        response = self.query(
            """
            query {
                samples {
                    laneId
                }
            }
            """,
        )

        # query ok?
        self.assertResponseNoErrors(response)

        # expected content?
        actual_content = json.loads(response.content)
        expected_content = {"data": {"samples": []}}
        self.assertDictEqual(
            actual_content, expected_content, msg="Unexpected data in response"
        )


class NonEmptyDatabaseSchemaTest(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    fixtures = [
        "institutions.json",
        "samples.json",
    ]  # alternatively, could generate in setUp() function

    def test_query_samples(self):
        response = self.query(
            """
            query {
                samples {
                    laneId
                }
            }
            """,
        )

        # query ok?
        self.assertResponseNoErrors(response)

        # expected content?
        actual_content = json.loads(response.content)
        self.assertIn(
            "samples",
            actual_content["data"],
            msg="Expected samples field in response",
        )
        self.assertGreater(
            len(actual_content["data"]["samples"]),
            0,
            msg="Expected data in response, got none",
        )
        self.assertIn(
            "laneId",
            actual_content["data"]["samples"][0],
            msg="Expected laneId field in each sample response",
        )


class APITestCase(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema

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

        # query ok?
        self.assertResponseNoErrors(response)

        # expected content?
        content = json.loads(response.content)
        self.assertIsInstance(content, dict, msg=self.MSG_ROOT_NOT_AN_OBJECT)
        self.assertIn("data", content, msg=self.MSG_NO_DATA)

        # has the query?
        self.assertIn(
            queryname, content["data"], msg=self.MSG_FIELD_MISSING,
        )
        value = content["data"][queryname]

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


class SamplesQueryTestCase(APITestCase):
    def setUp(self):
        # put something in the db
        self.institution = Institution.objects.create(
            name="Wellcome Sanger Institute", country="United Kingdom"
        )
        self.sample = Sample.objects.create(
            lane_id="31663_7#113",
            sample_id="5903STDY8059170",
            public_name="CUHK_GBS177WT_16",
            submitting_institution=self.institution,
        )

    def test_has_field_lane_id(self):
        query_value = self.make_and_validate_query("samples", "laneId")
        self.validate_non_empty_list(query_value)
        self.validate_field(
            query_value[0], "laneId", expected_value=self.sample.lane_id
        )

    def test_has_field_sample_id(self):
        query_value = self.make_and_validate_query("samples", "sampleId")
        self.validate_non_empty_list(query_value)
        self.validate_field(
            query_value[0], "sampleId", expected_value=self.sample.sample_id
        )

    def test_has_field_public_name(self):
        query_value = self.make_and_validate_query("samples", "publicName")
        self.validate_non_empty_list(query_value)
        self.validate_field(
            query_value[0],
            "publicName",
            expected_value=self.sample.public_name,
        )

    def test_has_field_submitting_institution(self):
        query_value = self.make_and_validate_query(
            "samples",
            """
            submittingInstitution {
                name
            }
            """,
        )
        self.validate_non_empty_list(query_value)
        submitting_institution = self.validate_field(
            query_value[0], "submittingInstitution"
        )
        self.validate_field(
            submitting_institution,
            "name",
            expected_value=self.institution.name,
        )
