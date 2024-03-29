import urllib.error
import urllib.request
from copy import deepcopy
from datetime import datetime
from os import environ
from unittest import TestCase
from unittest.mock import patch

import yaml
from DataServices.sample_tracking_services import MonocleSampleTracking
from DataSources.institution_data import InstitutionData
from DataSources.pipeline_status import PipelineStatus
from DataSources.sample_metadata import MonocleClient, SampleMetadata
from DataSources.sequencing_status import MLWH_Client, SequencingStatus

INSTITUTION_KEY = "GenWel"
PUBLIC_NAME = "SCN9A"


class MonocleSampleTrackingTest(TestCase):

    test_config = "dash/tests/mock_data/data_sources.yml"
    test_config_bad = "dash/tests/mock_data/data_sources_bad.yml"
    with open(test_config, "r") as file:
        data_sources = yaml.load(file, Loader=yaml.FullLoader)
    mock_url_path = data_sources["data_download"]["url_path"]
    mock_web_dir = data_sources["data_download"]["web_dir"]

    inst_key_batch_date_pairs = [
        {"institution key": "FakOne", "batch date": "2020-04-29"},
        {"institution key": "FakTwo", "batch date": "2021-05-02"},
        {"institution key": "FakOne", "batch date": "1892-01-30"},
    ]

    mock_project_id = "juno"
    mock_monocle_data_dir = "dash/tests/mock_data/s3"

    # this is the path to the actual data directory, i.e. the target of the data download symlinks
    mock_inst_view_dir = "dash/tests/mock_data/monocle_juno_institution_view"

    mock_unwanted_lanes_file = "dash/tests/mock_data/unwanted-lanes.txt"

    # this has mock values for the environment variables set by docker-compose
    mock_environment = {"JUNO_DATA": mock_monocle_data_dir, "UNWANTED_LANES_FILE": mock_unwanted_lanes_file}

    # this is the mock date for the instantiation of MonocleSampleTracking; it must match the latest month used in `expected_progress_data`
    # (because get_progeress() always returns date values up to "now")
    mock_data_updated = datetime(2021, 5, 15)

    # mock values for patching queries in DataSources modules
    mock_institution_data = [
        {"key": "FakOne", "name": "Fake institution One"},
        {"key": "FakTwo", "name": "Fake institution Two"},
    ]
    mock_samples = [
        {
            "sanger_sample_id": "fake_sample_id_1",
            "submitting_institution": "FakOne",
            "public_name": f"{PUBLIC_NAME}_1",
        },
        {
            "sanger_sample_id": "fake_sample_id_2",
            "submitting_institution": "FakOne",
            "public_name": f"{PUBLIC_NAME}_2",
        },
        {
            "sanger_sample_id": "fake_sample_id_3",
            "submitting_institution": "FakTwo",
            "public_name": f"{PUBLIC_NAME}_3",
        },
        {
            "sanger_sample_id": "fake_sample_id_4",
            "submitting_institution": "FakTwo",
            "public_name": f"{PUBLIC_NAME}_4",
        },
    ]
    mock_seq_data = {
        "_ERROR": None,
        "fake_sample_id_1": {
            "mock data": "anything",
            "creation_datetime": "2020-04-29T11:03:35Z",
            "lanes": [
                {
                    "id": "fake_lane_id_1",
                    "qc_lib": 1,
                    "qc_seq": 1,
                    "qc_success": 1,
                    "qc_status_text": "Success",
                    "run_status": "qc complete",
                    "qc_started": 1,
                    "qc_complete_datetime": "any string will do",
                },
                {
                    "id": "fake_lane_id_2",
                    "qc_lib": 1,
                    "qc_seq": 1,
                    "qc_success": 1,
                    "qc_status_text": "Success",
                    "run_status": "qc complete",
                    "qc_started": 1,
                    "qc_complete_datetime": "any string will do",
                },
                {
                    "id": "fake_lane_id_3",
                    "qc_lib": 1,
                    "qc_seq": 0,
                    "qc_success": 0,
                    "qc_status_text": "Sequencing QC failed",
                    "run_status": "qc complete",
                    "qc_started": 1,
                    "qc_complete_datetime": "any string will do",
                },
            ],
        },
        "fake_sample_id_2": {
            "mock data": "anything",
            "creation_datetime": "2020-11-16T16:43:04Z",
            "lanes": [
                {
                    "id": "fake_lane_id_4",
                    "qc_lib": 1,
                    "qc_seq": 1,
                    "qc_success": 1,
                    "qc_status_text": "Success",
                    "run_status": "qc complete",
                    "qc_started": 1,
                    "qc_complete_datetime": "any string will do",
                }
            ],
        },
        "fake_sample_id_3": {
            "mock data": "anything",
            "creation_datetime": "2021-05-02T10:31:49Z",
            "lanes": [
                {
                    "id": "fake_lane_id_5",
                    "qc_lib": 1,
                    "qc_seq": 1,
                    "qc_success": 1,
                    "qc_status_text": "Success",
                    "run_status": "qc complete",
                    "qc_started": 1,
                    "qc_complete_datetime": "any string will do",
                }
            ],
        },
        "fake_sample_id_4": {
            "mock data": "anything",
            "creation_datetime": "2021-05-02T14:07:23Z",
            "lanes": [
                {
                    "id": "fake_lane_id_6",
                    "qc_lib": 1,
                    "qc_seq": 1,
                    "qc_success": 1,
                    "qc_status_text": "Success",
                    "run_status": "qc complete",
                    "qc_started": 1,
                    "qc_complete_datetime": "any string will do",
                }
            ],
        },
    }

    # data we expect MonocleSampleTracking methods to return, given patched queries with the value above
    # the latest month included here must match the date provided by `mock_data_updated`
    expected_progress_data = {
        "date": [
            "Sep 2019",
            "Oct 2019",
            "Nov 2019",
            "Dec 2019",
            "Jan 2020",
            "Feb 2020",
            "Mar 2020",
            "Apr 2020",
            "May 2020",
            "Jun 2020",
            "Jul 2020",
            "Aug 2020",
            "Sep 2020",
            "Oct 2020",
            "Nov 2020",
            "Dec 2020",
            "Jan 2021",
            "Feb 2021",
            "Mar 2021",
            "Apr 2021",
            "May 2021",
        ],
        "samples received": [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 8],
        "samples sequenced": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }

    expected_dropout_data = {
        "FakOne": {"_ERROR": "Server Error: Records cannot be collected at this time. Please try again later."},
        "FakTwo": {"_ERROR": "Server Error: Records cannot be collected at this time. Please try again later."},
    }

    expected_sample_data = {
        "FakOne": [
            {"sanger_sample_id": "fake_sample_id_1", "public_name": f"{PUBLIC_NAME}_1"},
            {"sanger_sample_id": "fake_sample_id_2", "public_name": f"{PUBLIC_NAME}_2"},
        ],
        "FakTwo": [
            {"sanger_sample_id": "fake_sample_id_3", "public_name": f"{PUBLIC_NAME}_3"},
            {"sanger_sample_id": "fake_sample_id_4", "public_name": f"{PUBLIC_NAME}_4"},
        ],
    }
    # expected sequencing data are same as mock sequencing data except unwanted lane(s) are removed
    expected_seq_data = mock_seq_data
    expected_seq_data["fake_sample_id_1"]["lanes"] = [
        {
            "id": "fake_lane_id_2",
            "qc_lib": 1,
            "qc_seq": 1,
            "qc_success": 1,
            "qc_status_text": "Success",
            "run_status": "qc complete",
            "qc_started": 1,
            "qc_complete_datetime": "any string will do",
        },
    ]
    expected_seq_status = {"FakOne": expected_seq_data, "FakTwo": expected_seq_data}
    expected_batches = {
        "FakOne": {
            "_ERROR": None,
            "expected": 2,
            "received": 4,
            "deliveries": [
                {"name": "Batch 1", "date": "2020-04-29", "number": 1},
                {"name": "Batch 2", "date": "2020-11-16", "number": 1},
                {"name": "Batch 3", "date": "2021-05-02", "number": 2},
            ],
        },
        "FakTwo": {
            "_ERROR": None,
            "expected": 2,
            "received": 4,
            "deliveries": [
                {"name": "Batch 1", "date": "2020-04-29", "number": 1},
                {"name": "Batch 2", "date": "2020-11-16", "number": 1},
                {"name": "Batch 3", "date": "2021-05-02", "number": 2},
            ],
        },
    }
    expected_seq_summary = {
        "FakOne": {
            "_ERROR": None,
            "samples_received": 4,
            "samples_completed": 4,
            "samples_successful": 4,
            "lanes_completed": 4,
            "lanes_successful": 4,
            "lanes_failed": 0,
            "fail_messages": [],
        },
        "FakTwo": {
            "_ERROR": None,
            "samples_received": 4,
            "samples_completed": 4,
            "samples_successful": 4,
            "lanes_completed": 4,
            "lanes_successful": 4,
            "lanes_failed": 0,
            "fail_messages": [],
        },
    }
    expected_pipeline_summary = {
        "FakOne": {"_ERROR": None, "running": 4, "completed": 0, "success": 0, "failed": 0, "fail_messages": []},
        "FakTwo": {"_ERROR": None, "running": 4, "completed": 0, "success": 0, "failed": 0, "fail_messages": []},
    }

    # create MonocleSampleTracking object outside setUp() to avoid creating multipe instances
    # this means we use cached data rather than making multiple patched queries to SampleMetadata etc.
    monocle_sample_tracking = MonocleSampleTracking(set_up=False)

    @patch.dict(environ, mock_environment, clear=True)
    def setUp(self):
        self.monocle_sample_tracking.institution_ldap_data = InstitutionData(set_up=False)
        self.monocle_sample_tracking.institution_ldap_data.set_up(self.test_config)
        self.monocle_sample_tracking.current_project = self.mock_project_id
        # mock sample_metadata
        self.monocle_sample_tracking.sample_metadata = SampleMetadata(set_up=False)
        self.monocle_sample_tracking.sample_metadata.monocle_client = MonocleClient(set_up=False)
        self.monocle_sample_tracking.sample_metadata.monocle_client.set_up(self.test_config)
        self.monocle_sample_tracking.updated = self.mock_data_updated
        # mock sequencing_status
        self.monocle_sample_tracking.sequencing_status_source = SequencingStatus(set_up=False)
        self.monocle_sample_tracking.sequencing_status_source.mlwh_client = MLWH_Client(set_up=False)
        self.monocle_sample_tracking.sequencing_status_source.mlwh_client.set_up(self.test_config)
        # mock pipeline_status
        self.monocle_sample_tracking.pipeline_status = PipelineStatus(self.mock_project_id, config=self.test_config)
        # load mock data
        self.get_mock_data()

    @patch.object(InstitutionData, "get_all_institutions_regardless_of_user_membership")
    @patch.object(SampleMetadata, "get_samples")
    @patch.object(SequencingStatus, "get_multiple_samples")
    def get_mock_data(self, mock_seq_samples_query, mock_db_sample_query, mock_institutions_query):
        mock_institutions_query.return_value = self.mock_institution_data
        self.monocle_sample_tracking.sequencing_status_data = None
        mock_db_sample_query.return_value = self.mock_samples
        # sequencing status data are modified (unwanted lanes removed) so
        # use a copy of the mock data for the return value here:
        mock_seq_samples_query.return_value = deepcopy(self.mock_seq_data)
        self.monocle_sample_tracking.get_institutions()
        self.monocle_sample_tracking.get_samples()
        self.monocle_sample_tracking.get_sequencing_status()

    def test_init(self):
        self.assertIsInstance(self.monocle_sample_tracking, MonocleSampleTracking)

    def test_get_progress(self):
        progress_data = self.monocle_sample_tracking.get_progress()

        self.assertEqual(self.expected_progress_data, progress_data)

    def test_get_institutions(self):
        expected_institutions = {
            "FakOne": {"name": "Fake institution One"},
            "FakTwo": {"name": "Fake institution Two"},
        }

        actual_institutions = self.monocle_sample_tracking.get_institutions()

        self.assertEqual(expected_institutions, actual_institutions)

    def test_get_institutions_returns_cached_response(self):
        expected = "some data"
        self.monocle_sample_tracking.institutions_data = expected

        actual_institutions = self.monocle_sample_tracking.get_institutions()

        self.assertEqual(expected, actual_institutions)
        # Teardown: clear cache.
        self.monocle_sample_tracking.institutions_data = None

    def test_get_institutions_returns_institutions_from_user_membership(self):
        self.monocle_sample_tracking.institutions_data = None
        expected_institution_key = "CenParEng"
        expected_institution_name = "Center of Paradise Engineering"
        user_record = {"memberOf": [{"inst_id": expected_institution_key, "inst_name": expected_institution_name}]}
        self.monocle_sample_tracking.user_record = user_record

        actual_institutions = self.monocle_sample_tracking.get_institutions()

        self.assertEqual({expected_institution_key: {"name": expected_institution_name}}, actual_institutions)
        # Teardown: clear cache.
        self.monocle_sample_tracking.user_record = None
        self.monocle_sample_tracking.institutions_data = None

    def test_get_samples(self):
        sample_data = self.monocle_sample_tracking.get_samples()
        self.assertEqual(self.expected_sample_data, sample_data)

    @patch.object(SampleMetadata, "get_samples")
    def test_get_samples_does_not_crash_on_unauthorised_user_institution(self, mock_db_sample_query):
        mem_samples = self.monocle_sample_tracking.samples_data
        self.monocle_sample_tracking.samples_data = None
        mock_db_sample_query.return_value = [
            dict(self.mock_samples[0]),
            {
                "sanger_sample_id": "fake_sample_id_2",
                "submitting_institution": "SECRET_INSTITUTION",
                "public_name": f"{PUBLIC_NAME}_2",
            },
        ]

        try:
            self.monocle_sample_tracking.get_samples()
        except KeyError:
            self.fail("`get_samples` should not fail on institutions that aren't in user institutions")
        finally:
            self.monocle_sample_tracking.samples_data = mem_samples

    @patch.dict(environ, mock_environment, clear=True)
    def test_get_sequencing_status(self):
        seq_status_data = self.monocle_sample_tracking.get_sequencing_status()

        self.assertEqual(self.expected_seq_status, seq_status_data)

    @patch.dict(environ, mock_environment, clear=True)
    @patch.object(SequencingStatus, "get_multiple_samples")
    def test_get_sequencing_status_droppout(self, get_multiple_samples_mock):
        get_multiple_samples_mock.side_effect = urllib.error.HTTPError(
            "/nowhere", "404", "page could not be found", "yes", "no"
        )
        self.monocle_sample_tracking.sequencing_status_data = None

        httpdropout = self.monocle_sample_tracking.get_sequencing_status()

        self.assertEqual(self.expected_dropout_data, httpdropout)

    def test_get_batches(self):
        batches_data = self.monocle_sample_tracking.get_batches()

        self.assertEqual(self.expected_batches, batches_data)

    @patch.dict(environ, mock_environment, clear=True)
    @patch.object(SequencingStatus, "get_multiple_samples")
    def test_get_batches_dropouts(self, get_multiple_samples_mock):
        get_multiple_samples_mock.side_effect = urllib.error.HTTPError(
            "/nowhere", "404", "page could not be found", "yes", "no"
        )
        self.monocle_sample_tracking.sequencing_status_data = None
        self.monocle_sample_tracking.get_sequencing_status()

        batches_data = self.monocle_sample_tracking.get_batches()

        self.assertEqual(self.expected_dropout_data, batches_data)

    @patch.dict(environ, mock_environment, clear=True)
    def test_sequencing_status_summary(self):
        seq_status_summary = self.monocle_sample_tracking.sequencing_status_summary()

        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.expected_seq_summary, seq_status_summary))
        self.assertEqual(self.expected_seq_summary, seq_status_summary)

    @patch.dict(environ, mock_environment, clear=True)
    def test_sequencing_status_summary_dropout(self):
        self.monocle_sample_tracking.sequencing_status_data = self.expected_dropout_data

        seq_status_summary = self.monocle_sample_tracking.sequencing_status_summary()

        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.expected_seq_summary, seq_status_summary))
        self.assertEqual(self.expected_dropout_data, seq_status_summary)

    @patch.dict(environ, mock_environment, clear=True)
    def test_pipeline_status_summary(self):
        pipeline_summary = self.monocle_sample_tracking.pipeline_status_summary()
        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.expected_pipeline_summary, pipeline_summary))

        self.assertEqual(self.expected_pipeline_summary, pipeline_summary)

    @patch.dict(environ, mock_environment, clear=True)
    def test_pipeline_status_summary_dropout(self):
        self.monocle_sample_tracking.sequencing_status_data = self.expected_dropout_data

        pipeline_summary = self.monocle_sample_tracking.pipeline_status_summary()

        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.expected_pipeline_summary, pipeline_summary))
        self.assertEqual(self.expected_dropout_data, pipeline_summary)

    def test_project_information_rejects_if_no_project_given(self):
        self.monocle_sample_tracking.current_project = None

        with self.assertRaisesRegex(ValueError, "The current project is not set"):
            self.monocle_sample_tracking.project_information()

    @patch.object(SampleMetadata, "get_project_information")
    def test_project_information(self, get_project_information_mock):
        expected_project_information = "some project info"
        get_project_information_mock.return_value = expected_project_information
        self.monocle_sample_tracking.current_project = "juno"

        actual_project_information = self.monocle_sample_tracking.project_information()
        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.expected_pipeline_summary, pipeline_summary))

        self.assertEqual(expected_project_information, actual_project_information)
