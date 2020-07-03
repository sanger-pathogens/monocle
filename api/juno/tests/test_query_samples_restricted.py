from juno.tests.base import AuthenticatableGraphQLTestCase
from juno.api.models import Sample, Institution, User, Affiliation


class SamplesQueryTestCase(AuthenticatableGraphQLTestCase):
    def setUp(self):
        # put several institutions in the db
        self.institution_sanger = Institution.objects.create(
            name="Wellcome Sanger Institute",
            country="United Kingdom",
            latitude=52.083333,
            longitude=0.183333,
        )
        self.institution_other = Institution.objects.create(
            name="Monsters Inc",
            country="Unknown",
            latitude=34.3,
            longitude=170.6,
        )
        self.institution_another = Institution.objects.create(
            name="Skynet",
            country="United States",
            latitude=44.3,
            longitude=223.2,
        )

        # put several users in the db
        self.user_sanger = User.objects.create(
            email="jane@sanger.ac.uk", first_name="Jane", last_name="Seymour",
        )
        self.password_sanger = "janesicles"
        self.user_sanger.set_password(self.password_sanger)
        self.user_sanger.save()
        self.user_other = User.objects.create(
            email="bob@bob.com", first_name="Bob", last_name="Bobbity",
        )
        self.password_other = "bobsicles"
        self.user_other.set_password(self.password_other)
        self.user_other.save()

        # associate the users with the institutions
        Affiliation.objects.create(
            user=self.user_sanger, institution=self.institution_sanger
        )
        Affiliation.objects.create(
            user=self.user_other, institution=self.institution_other
        )

        # put a sample in the db per institution
        self.sample_other = Sample.objects.create(
            lane_id="31663_7#113",
            sample_id="5903STDY8059170",
            public_name="CUHK_GBS177WT_16",
            serotype="Ia",
            host_status="skin and soft-tissue infection",
            submitting_institution=self.institution_other,
        )
        self.sample_another = Sample.objects.create(
            lane_id="31663_7#114",
            sample_id="5903STDY8059171",
            public_name="CUHK_GBS177WT_17",
            serotype="Ib",
            host_status="skin and soft-tissue infection",
            submitting_institution=self.institution_another,
        )

    def make_and_validate_samples_query(self, subquery):
        # call api
        response = self.make_query("samples", subquery)
        data = self.validate_successful(response)
        samples = self.validate_field(data, "samples")

        # check non-empty
        self.validate_non_empty_list(samples)

        # return samples
        return samples

    def test_non_authenticated_user_cannot_view_samples(self):
        # call api
        response = self.make_query("samples", "laneId")

        # checks
        content = self.validate_unsuccessful(response)
        errors = self.validate_has_graphql_errors(content)
        self.assertTrue(
            any(
                e["message"] == self.GRAPHQL_JWT_MSG_BAD_PERMISSIONS
                for e in errors
            )
        )
        if "data" in content.keys() and "samples" in content["data"].keys():
            self.assertEqual(content["data"]["samples"], None)

    def test_non_sanger_user_can_view_restricted_samples(self):
        # login as non-sanger user
        response = self.login(self.user_other.email, self.password_other)
        self.validate_login_successful(response)

        # call api
        samples = self.make_and_validate_samples_query("laneId")

        # checks
        self.assertEqual(len(samples), 1)
        self.validate_field(
            samples[0], "laneId", expected_value=self.sample_other.lane_id,
        )

    def test_sanger_user_can_view_all_samples(self):
        # login as sanger user
        response = self.login(self.user_sanger.email, self.password_sanger)
        self.validate_login_successful(response)

        # call api
        samples = self.make_and_validate_samples_query("laneId")

        # checks
        self.assertEqual(len(samples), 2)
        self.validate_field(
            samples[0], "laneId", expected_value=self.sample_other.lane_id,
        )
        self.validate_field(
            samples[1], "laneId", expected_value=self.sample_another.lane_id,
        )
