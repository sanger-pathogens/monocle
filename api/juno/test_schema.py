import json
from graphene_django.utils.testing import GraphQLTestCase

from juno.schema import schema


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
