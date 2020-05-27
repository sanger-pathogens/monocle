from juno.tests.base import APITestCase
from juno.api.models import Sample, Institution


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
