import pytest

from juno.graphql.models import UserModel, InstitutionModel, SampleModel

@pytest.mark.usefixtures('db', 'client')
class TestSample:
    """API schema tests."""

    def test_samples(self, db, client):
        """Query samples."""
        sample = SampleModel(
            lane_id="31663_7#113",
            sample_id="5903STDY8059170",
            public_name="CUHK_GBS177WT_16",
            submitting_institution_name="National Reference Laboratories"
        )
        
        db.session.add(sample)
        db.session.commit()

        executed = client.execute('''
        {
            samples {
                laneId
                sampleId
                submittingInstitutionName
            }
        }
        ''')

        assert len(executed['data']['samples']) == 1
        assert executed['data']['samples'][0]['laneId'] == sample.lane_id
