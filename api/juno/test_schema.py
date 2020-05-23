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


class SamplesQueryTest(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    MSG_VALUE_MISMATCH = "Value in API response differs from value in database"
    MSG_VALUE_EXPECTED_NONPRIMITIVE_TYPE = (
        "Value in API response should be an object"
    )
    MSG_VALUE_EXPECTED_STRING_TYPE = "Value in API response should be a string"
    MSG_MISSING_FIELD = "API response should contain field"

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

    def verify_field_present(self, field, subquery):
        # make query
        response = self.query(
            """
            query {
                samples {
                    %s
                }
            }
            """
            % (subquery,),
        )

        # query ok?
        self.assertResponseNoErrors(response)

        # expected content?
        actual_content = json.loads(response.content)

        # has the query?
        self.assertIn(
            "samples", actual_content["data"], msg=self.MSG_MISSING_FIELD,
        )
        self.assertEqual(
            len(actual_content["data"]["samples"]),
            1,
            msg="Expected one sample",
        )

        # has the field?
        sample = actual_content["data"]["samples"][0]
        self.assertIn(
            field, sample, msg=self.MSG_MISSING_FIELD,
        )
        value = sample[field]

        # return field value for further checks
        return value

    def test_has_field_lane_id(self):
        value = self.verify_field_present("laneId", "laneId")
        self.assertEqual(
            value, self.sample.lane_id, msg=self.MSG_VALUE_MISMATCH
        )

    def test_has_field_sample_id(self):
        value = self.verify_field_present("sampleId", "sampleId")
        self.assertEqual(
            value, self.sample.sample_id, msg=self.MSG_VALUE_MISMATCH
        )

    def test_has_field_public_name(self):
        value = self.verify_field_present("publicName", "publicName")
        self.assertEqual(
            value, self.sample.public_name, msg=self.MSG_VALUE_MISMATCH
        )

    def test_has_field_submitting_institution(self):
        value = self.verify_field_present(
            "submittingInstitution",
            """
            submittingInstitution {
                name
            }
            """,
        )
        self.assertIsInstance(
            value, dict, msg=self.MSG_VALUE_EXPECTED_NONPRIMITIVE_TYPE
        )
        self.assertIn("name", value, msg=self.MSG_MISSING_FIELD)
        self.assertEqual(
            value["name"], self.institution.name, msg=self.MSG_VALUE_MISMATCH
        )
