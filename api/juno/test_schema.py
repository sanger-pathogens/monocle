import json
from graphene_django.utils.testing import GraphQLTestCase

from juno.schema import schema
from juno.api.models import Sample, Institution


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
            samples[0], "hostStatus", expected_value="SKIN_AND_SOFT_TISSUE_INFECTION",
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
            name="Wellcome Sanger Institute", country="United Kingdom"
        )

    def make_and_validate_institutions_query(self, subquery):
        # call api
        institutions = self.make_and_validate_query("institutions", subquery)

        # check non-empty
        self.validate_non_empty_list(institutions)

        # return samples
        return institutions

    def test_has_field_name(self):
        institutions = self.make_and_validate_institutions_query("name")
        self.validate_field(
            institutions[0], "name", expected_value=self.institution.name,
        )

    def test_has_field_country(self):
        institutions = self.make_and_validate_institutions_query("country")
        self.validate_field(
            institutions[0],
            "country",
            expected_value=self.institution.country,
        )
