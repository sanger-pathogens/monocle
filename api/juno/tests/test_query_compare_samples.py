from juno.tests.base import AuthenticatableGraphQLTestCase
from juno.api.models import Sample, Institution, User, Affiliation


class SamplesQueryTestCase(AuthenticatableGraphQLTestCase):
    PASSWORD = "bobsicles"

    def setUp(self):
        # put an institution in the db
        self.institution = Institution.objects.create(
            name="Wellcome Sanger Institute",
            country="United Kingdom",
            latitude=52.083333,
            longitude=0.183333,
        )

        # put user in the db
        self.user = User.objects.create(
            email="bob@bob.com", first_name="Bob", last_name="Bobbity",
        )
        self.user.set_password(self.PASSWORD)
        self.user.save()

        # associate the user with the institution
        Affiliation.objects.create(
            user=self.user, institution=self.institution
        )

        # put a sample in the db, submitted by the institution
        self.sample = Sample.objects.create(
            sample_id="5903STDY8059170",
            lane_id="31663_7#113",
            public_name="CUHK_GBS177WT_16",
            serotype="Ia",
            host_status="carriage",
            submitting_institution=self.institution,
        )

        # login (institutions is an auth restricted resource)
        response = self.login(self.user.email, self.PASSWORD)
        (payload, token, refresh_expires_in) = self.validate_login_successful(
            response
        )

    def make_and_validate_compare_samples_query(self, samples):
        # call api
        response = self.post(
            """
            query CompareSamples($samples: [SampleInput!]!){
                compareSamples(samples: $samples) {
                    added {
                        sampleId
                    }
                    removed {
                        sampleId
                    }
                    changed {
                        sampleId
                    }
                    same {
                        sampleId
                    }
                    missingInstitutions
                }
            }
            """,
            op_name="CompareSamples",
            variables={"samples": samples},
        )

        data = self.validate_successful(response)
        compare_samples = self.validate_field(data, "compareSamples",)

        # return for further checks
        return compare_samples

    def test_removed(self):
        # prepare
        samples = []

        # act
        compare_samples = self.make_and_validate_compare_samples_query(samples)

        # assert
        self.validate_field(compare_samples, "added", expected_value=[])
        self.validate_field(
            compare_samples,
            "removed",
            expected_value=[{"sampleId": "5903STDY8059170"}],
        )
        self.validate_field(compare_samples, "changed", expected_value=[])
        self.validate_field(compare_samples, "same", expected_value=[])
        self.validate_field(
            compare_samples, "missingInstitutions", expected_value=[],
        )

    def test_same(self):
        # prepare
        samples = [
            {
                "sampleId": "5903STDY8059170",
                "laneId": "31663_7#113",
                "publicName": "CUHK_GBS177WT_16",
                "serotype": "IA",
                "hostStatus": "CARRIAGE",
                "submittingInstitution": "Wellcome Sanger Institute",
            }
        ]

        # act
        compare_samples = self.make_and_validate_compare_samples_query(samples)

        # assert
        self.validate_field(compare_samples, "added", expected_value=[])
        self.validate_field(
            compare_samples, "removed", expected_value=[],
        )
        self.validate_field(compare_samples, "changed", expected_value=[])
        self.validate_field(
            compare_samples,
            "same",
            expected_value=[{"sampleId": "5903STDY8059170"}],
        )
        self.validate_field(
            compare_samples, "missingInstitutions", expected_value=[],
        )

    def test_sample_with_no_lane_id_same(self):
        # Remove the db lane_id
        self.sample.lane_id = None
        self.sample.save()

        # prepare
        samples = [
            {
                "sampleId": "5903STDY8059170",
                "laneId": "",
                "publicName": "CUHK_GBS177WT_16",
                "serotype": "IA",
                "hostStatus": "CARRIAGE",
                "submittingInstitution": "Wellcome Sanger Institute",
            }
        ]

        # act
        compare_samples = self.make_and_validate_compare_samples_query(samples)

        # assert
        self.validate_field(compare_samples, "added", expected_value=[])
        self.validate_field(
            compare_samples, "removed", expected_value=[],
        )
        self.validate_field(compare_samples, "changed", expected_value=[])
        self.validate_field(
            compare_samples,
            "same",
            expected_value=[{"sampleId": "5903STDY8059170"}],
        )
        self.validate_field(
            compare_samples, "missingInstitutions", expected_value=[],
        )

    def test_changed(self):
        # prepare
        samples = [
            {
                "sampleId": "5903STDY8059170",
                "laneId": "31663_7#113",
                "publicName": "CUHK_GBS177WT_16",
                "serotype": "IB",
                "hostStatus": "CARRIAGE",
                "submittingInstitution": "Wellcome Sanger Institute",
            }
        ]

        # act
        compare_samples = self.make_and_validate_compare_samples_query(samples)

        # assert
        self.validate_field(compare_samples, "added", expected_value=[])
        self.validate_field(
            compare_samples, "removed", expected_value=[],
        )
        self.validate_field(
            compare_samples,
            "changed",
            expected_value=[{"sampleId": "5903STDY8059170"}],
        )
        self.validate_field(
            compare_samples, "same", expected_value=[],
        )
        self.validate_field(
            compare_samples, "missingInstitutions", expected_value=[],
        )

    def test_sample_with_no_lane_id_changed(self):
        # Remove the db lane_id
        self.sample.lane_id = None
        self.sample.save()

        # prepare
        samples = [
            {
                "sampleId": "5903STDY8059170",
                "laneId": "31663_7#113",
                "publicName": "CUHK_GBS177WT_16",
                "serotype": "IB",
                "hostStatus": "CARRIAGE",
                "submittingInstitution": "Wellcome Sanger Institute",
            }
        ]

        # act
        compare_samples = self.make_and_validate_compare_samples_query(samples)

        # assert
        self.validate_field(compare_samples, "added", expected_value=[])
        self.validate_field(
            compare_samples, "removed", expected_value=[],
        )
        self.validate_field(
            compare_samples,
            "changed",
            expected_value=[{"sampleId": "5903STDY8059170"}],
        )
        self.validate_field(
            compare_samples, "same", expected_value=[],
        )
        self.validate_field(
            compare_samples, "missingInstitutions", expected_value=[],
        )

    def test_added(self):
        # prepare
        samples = [
            {
                "sampleId": "5903STDY8059170",
                "laneId": "31663_7#113",
                "publicName": "CUHK_GBS177WT_16",
                "serotype": "IA",
                "hostStatus": "CARRIAGE",
                "submittingInstitution": "Wellcome Sanger Institute",
            },
            {
                "sampleId": "5903STDY8059171",
                "laneId": "31663_7#115",
                "publicName": "CUHK_GBS177WT_17",
                "serotype": "IB",
                "hostStatus": "CARRIAGE",
                "submittingInstitution": "Wellcome Sanger Institute",
            }
        ]

        # act
        compare_samples = self.make_and_validate_compare_samples_query(samples)

        # assert
        self.validate_field(
            compare_samples,
            "added",
            expected_value=[{"sampleId": "5903STDY8059171"}],
        )
        self.validate_field(
            compare_samples, "removed", expected_value=[],
        )
        self.validate_field(
            compare_samples, "changed", expected_value=[],
        )
        self.validate_field(
            compare_samples,
            "same",
            expected_value=[{"sampleId": "5903STDY8059170"}],
        )
        self.validate_field(
            compare_samples, "missingInstitutions", expected_value=[],
        )

    def test_sample_with_no_lane_id_added(self):
        # prepare
        samples = [
            {
                "sampleId": "5903STDY8059170",
                "laneId": "31663_7#113",
                "publicName": "CUHK_GBS177WT_16",
                "serotype": "IA",
                "hostStatus": "CARRIAGE",
                "submittingInstitution": "Wellcome Sanger Institute",
            },
            {
                "sampleId": "5903STDY8059171",
                "laneId": "",
                "publicName": "CUHK_GBS177WT_17",
                "serotype": "IB",
                "hostStatus": "CARRIAGE",
                "submittingInstitution": "Wellcome Sanger Institute",
            }
        ]

        # act
        compare_samples = self.make_and_validate_compare_samples_query(samples)

        # assert
        self.validate_field(
            compare_samples,
            "added",
            expected_value=[{"sampleId": "5903STDY8059171"}],
        )
        self.validate_field(
            compare_samples, "removed", expected_value=[],
        )
        self.validate_field(
            compare_samples, "changed", expected_value=[],
        )
        self.validate_field(
            compare_samples,
            "same",
            expected_value=[{"sampleId": "5903STDY8059170"}],
        )
        self.validate_field(
            compare_samples, "missingInstitutions", expected_value=[],
        )

    def test_missing_institution(self):
        # prepare
        missing_institution = "UNKNOWN INSTITUTION"
        samples = [
            {
                "sampleId": "5903STDY8059170",
                "laneId": "31663_7#113",
                "publicName": "CUHK_GBS177WT_16",
                "serotype": "IB",
                "hostStatus": "CARRIAGE",
                "submittingInstitution": missing_institution,
            }
        ]

        # act
        compare_samples = self.make_and_validate_compare_samples_query(samples)

        # assert
        self.validate_field(compare_samples, "added", expected_value=[])
        self.validate_field(
            compare_samples, "removed", expected_value=[],
        )
        self.validate_field(
            compare_samples,
            "changed",
            expected_value=[{"sampleId": "5903STDY8059170"}],
        )
        self.validate_field(
            compare_samples, "same", expected_value=[],
        )
        self.validate_field(
            compare_samples,
            "missingInstitutions",
            expected_value=[missing_institution],
        )
