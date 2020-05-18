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
