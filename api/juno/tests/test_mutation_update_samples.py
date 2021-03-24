from juno.tests.base import AuthenticatableGraphQLTestCase
from juno.api.models import Sample, Institution, User, Affiliation


class UpdateSamplesMutationTestCase(AuthenticatableGraphQLTestCase):
    PASSWORD = "bobsicles"
    SUBMITTING_INSTITUTION = "Wellcome Sanger Institute"
    SAMPLE_ID_TO_USE = "5903STDY8059170"

    def setUp(self):
        # put an institution in the db
        self.institution = Institution.objects.create(
            name=self.SUBMITTING_INSTITUTION,
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

        # login (auth restricted mutation)
        response = self.login(self.user.email, self.PASSWORD)
        (payload, token, refresh_expires_in) = self.validate_login_successful(
            response
        )

    def make_and_validate_update_samples_mutation(self, samples):
        # call api
        response = self.post(
            """
            mutation UpdateSamples($samples: [SampleInput!]!){
                updateSamples(samples: $samples) {
                    committed
                    diff {
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
            }
            """,
            op_name="UpdateSamples",
            variables={"samples": samples},
        )

        data = self.validate_successful(response)
        update_samples = self.validate_field(data, "updateSamples")

        # return for further checks
        return update_samples

    def test_can_empty(self):
        # prepare
        # put a sample in the db, submitted by the institution
        Sample.objects.create(
            sample_id=self.SAMPLE_ID_TO_USE,
            lane_id="31663_7#113",
            public_name="CUHK_GBS177WT_16",
            serotype="Ia",
            host_status="carriage",
            submitting_institution=self.institution,
        )

        # act
        update_samples = self.make_and_validate_update_samples_mutation([],)

        # assert (diff)
        diff = self.validate_field(update_samples, "diff")
        self.validate_field(diff, "added", expected_value=[])
        self.validate_field(
            diff, "removed", expected_value=[{"sampleId": self.SAMPLE_ID_TO_USE}]
        )
        self.validate_field(diff, "changed", expected_value=[])
        self.validate_field(diff, "same", expected_value=[])

        # assert (db changed)
        self.validate_field(update_samples, "committed", expected_value=True)

    def test_blank_lane_id_sample_removal(self):
        # prepare
        # put a sample in the db, submitted by the institution, with no lane id
        Sample.objects.create(
            sample_id=self.SAMPLE_ID_TO_USE,
            public_name="CUHK_GBS177WT_16",
            serotype="Ia",
            host_status="carriage",
            submitting_institution=self.institution,
        )

        # act
        update_samples = self.make_and_validate_update_samples_mutation([])

        # assert (diff)
        diff = self.validate_field(update_samples, "diff")
        self.validate_field(diff, "added", expected_value=[])
        self.validate_field(
            diff, "removed", expected_value=[{"sampleId": self.SAMPLE_ID_TO_USE}]
        )
        self.validate_field(diff, "changed", expected_value=[])
        self.validate_field(diff, "same", expected_value=[])

        # assert (db changed)
        self.validate_field(update_samples, "committed", expected_value=True)

    def test_blank_lane_id_sample_update(self):
        # prepare
        # put a sample in the db, submitted by the institution
        Sample.objects.create(
            sample_id=self.SAMPLE_ID_TO_USE,
            lane_id="31663_7#113",
            public_name="CUHK_GBS177WT_16",
            serotype="Ia",
            host_status="carriage",
            submitting_institution=self.institution,
        )

        # we will change the lane id to empty [null in db]
        changed_sample_list = [
            {
                "sampleId": self.SAMPLE_ID_TO_USE,
                "laneId":  "",
                "publicName": "CUHK_GBS177WT_16",
                "serotype": "Ia",
                "hostStatus": "CARRIAGE",
                "submittingInstitution": self.SUBMITTING_INSTITUTION,
            }
        ]

        # act
        update_samples = self.make_and_validate_update_samples_mutation(changed_sample_list)

        # assert (diff)
        diff = self.validate_field(update_samples, "diff")
        self.validate_field(diff, "added", expected_value=[])
        self.validate_field(diff, "removed", expected_value=[])
        self.validate_field(diff, "changed", expected_value=[{"sampleId": self.SAMPLE_ID_TO_USE}])
        self.validate_field(diff, "same", expected_value=[])

        # assert (db changed)
        self.validate_field(update_samples, "committed", expected_value=True)

    def test_blank_lane_id_sample_add(self):
        # prepare
        # add a sample with no lane id
        sample_list = [
            {
                "sampleId": self.SAMPLE_ID_TO_USE,
                "laneId":  "",
                "publicName": "CUHK_GBS177WT_16",
                "serotype": "Ia",
                "hostStatus": "CARRIAGE",
                "submittingInstitution": self.SUBMITTING_INSTITUTION,
            }
        ]

        # act
        update_samples = self.make_and_validate_update_samples_mutation(sample_list)

        # assert (diff)
        diff = self.validate_field(update_samples, "diff")
        self.validate_field(diff, "added", expected_value=[{"sampleId": self.SAMPLE_ID_TO_USE}])
        self.validate_field(diff, "removed", expected_value=[])
        self.validate_field(diff, "changed", expected_value=[])
        self.validate_field(diff, "same", expected_value=[])

        # assert (db changed)
        self.validate_field(update_samples, "committed", expected_value=True)

    def test_no_change_to_sample(self):
        # prepare
        # put a sample in the db, submitted by the institution
        Sample.objects.create(
            sample_id=self.SAMPLE_ID_TO_USE,
            public_name="CUHK_GBS177WT_16",
            serotype="Ia",
            host_status="carriage",
            submitting_institution=self.institution,
        )

        # sample to update
        sample_list = [
            {
                "sampleId": self.SAMPLE_ID_TO_USE,
                "laneId":  "",
                "publicName": "CUHK_GBS177WT_16",
                "serotype": "Ia",
                "hostStatus": "CARRIAGE",
                "submittingInstitution": self.SUBMITTING_INSTITUTION,
            }
        ]

        # act
        update_samples = self.make_and_validate_update_samples_mutation(sample_list)

        # assert (diff)
        diff = self.validate_field(update_samples, "diff")
        self.validate_field(diff, "added", expected_value=[])
        self.validate_field(diff, "removed", expected_value=[])
        self.validate_field(diff, "changed", expected_value=[])
        self.validate_field(diff, "same", expected_value=[{"sampleId": self.SAMPLE_ID_TO_USE}])

        # assert (db changed)
        self.validate_field(update_samples, "committed", expected_value=True)

