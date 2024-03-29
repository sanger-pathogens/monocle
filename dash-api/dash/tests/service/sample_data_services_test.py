from copy import deepcopy
from os import environ
from pathlib import Path, PurePath
from unittest import TestCase
from unittest.mock import patch

import yaml
from DataServices.sample_data_services import (
    ZIP_COMPRESSION_FACTOR_ASSEMBLIES_ANNOTATIONS,
    DataSourceConfigError,
    MonocleSampleData,
)
from DataServices.sample_tracking_services import MonocleSampleTracking
from DataSources.institution_data import InstitutionData
from DataSources.metadata_download import MetadataDownload, MonocleDownloadClient
from DataSources.pipeline_status import PipelineStatus
from DataSources.sample_metadata import MonocleClient, SampleMetadata
from DataSources.sequencing_status import MLWH_Client, SequencingStatus
from utils.file import format_file_size

INSTITUTION_KEY = "GenWel"
PUBLIC_NAME = "SCN9A"

MOCK_DOWNLOAD_HOST = "mock.host"
MOCK_DOWNLOAD_PATH = "path/incl/mock/download/symlink"
MOCK_DOWNLOAD_URL = "https://" + MOCK_DOWNLOAD_HOST + "/" + MOCK_DOWNLOAD_PATH
EXPECTED_METADATA_PLUS_QC_AND_IN_SILICO_DATA = (
    '''"Public_Name","Sanger_Sample_ID","Something_Made_Up","Also_Made_Up","Lane_ID","QC_Thing","In_Silico_Thing","Another_In_Silico_Thing","Download_Link"\n"fake_public_name_1","fake_sample_id_1","","","fake_lane_id_1 fake_lane_id_2 fake_lane_id_3","","","","'''
    + MOCK_DOWNLOAD_URL
    + '''/fake_public_name_1"\n"fake public name 2","fake_sample_id_2","","whatevs","fake_lane_id_4","","","","'''
    + MOCK_DOWNLOAD_URL
    + """/fake%20public%20name%202"
"""
)


class MonocleSampleDataTest(TestCase):

    test_config = "dash/tests/mock_data/data_sources.yml"
    test_config_bad = "dash/tests/mock_data/data_sources_bad.yml"
    with open(test_config, "r") as file:
        data_sources = yaml.load(file, Loader=yaml.FullLoader)
    mock_url_path = data_sources["data_download"]["url_path"]
    mock_web_dir = data_sources["data_download"]["web_dir"]

    mock_institution_data = [
        {"key": "FakOne", "name": "Fake institution One"},
        {"key": "FakTwo", "name": "Fake institution Two"},
    ]

    inst_key_batch_date_pairs = [
        {"institution key": "FakOne", "batch date": "2020-04-29"},
        {"institution key": "FakTwo", "batch date": "2021-05-02"},
        {"institution key": "FakOne", "batch date": "1892-01-30"},
    ]

    mock_project_id = "juno"

    mock_monocle_data_dir = "dash/tests/mock_data/s3"

    # this is the path to the actual data directory, i.e. the target of the data download symlinks
    mock_inst_view_dir = "dash/tests/mock_data/monocle_juno_institution_view"

    mock_unwanted_lanes_file = "dash/tests/mock_data/unwanted-lanes-empty.txt"

    # this is the route used to download data
    mock_download_route = "/data_route_via_nginx"

    # maximum nuumber of samples per ZIP archive
    mock_download_max_samples_per_zip = 100
    mock_download_max_samples_per_zip_with_reads = 10

    # this has mock values for the environment variables set by docker-compose
    mock_environment = {
        "JUNO_DATA": mock_monocle_data_dir,
        "JUNO_DATA_INSTITUTION_VIEW": mock_inst_view_dir,
        "UNWANTED_LANES_FILE": mock_unwanted_lanes_file,
    }

    # mock values for patching queries in DataSources modules
    mock_institution_keys = ["FakOne", "FakTwo"]
    mock_bad_institution_key = "this institution key does not exist"
    mock_sample_id_list = ["fake_sample_id_1", "fake_sample_id_2", "fake_sample_id_3", "fake_sample_id_4"]
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
    mock_seq_status = {
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

    mock_filtered_samples = [
        {
            "creation_datetime": "2020-04-29T11:03:35Z",
            "lanes": ["fake_lane_id_1", "fake_lane_id_2", "fake_lane_id_3"],
            "sanger_sample_id": "fake_sample_id_1",
            "inst_key": "FakOne",
            "public_name": "SCN9A_1",
        },
        {
            "creation_datetime": "2021-05-02T10:31:49Z",
            "lanes": ["fake_lane_id_5"],
            "sanger_sample_id": "fake_sample_id_3",
            "inst_key": "FakTwo",
            "public_name": "SCN9A_3",
        },
        {
            "creation_datetime": "2021-05-02T14:07:23Z",
            "lanes": ["fake_lane_id_6"],
            "sanger_sample_id": "fake_sample_id_4",
            "inst_key": "FakTwo",
            "public_name": "SCN9A_4",
        },
    ]

    mock_samples2 = [
        {
            "sanger_sample_id": "fake_sample_id_1",
            "submitting_institution": "FakOne",
            "public_name": f"{PUBLIC_NAME}_1",
        },
        {
            "sanger_sample_id": "fake_sample_id_2",
            "submitting_institution": "FakTwo",
            "public_name": f"{PUBLIC_NAME}_2",
        },
    ]

    mock_seq_status2 = {
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
            "creation_datetime": "2021-05-02T16:43:04Z",
            "lanes": [
                {
                    "id": "fake_lane_id_4",
                    "qc_lib": 1,
                    "qc_seq": 0,
                    "qc_success": 0,
                    "qc_status_text": "Sequencing QC failed",
                    "run_status": "qc complete",
                    "qc_started": 1,
                    "qc_complete_datetime": "any string will do",
                }
            ],
        },
    }

    mock_filtered_samples2 = [
        {
            "creation_datetime": "2020-04-29T11:03:35Z",
            "lanes": ["fake_lane_id_1", "fake_lane_id_2", "fake_lane_id_3"],
            "sanger_sample_id": "fake_sample_id_1",
            "inst_key": "FakOne",
            "public_name": "SCN9A_1",
        }
    ]

    mock_samples3 = mock_samples2

    mock_seq_status3 = {
        "_ERROR": None,
        "fake_sample_id_1": mock_seq_status2["fake_sample_id_1"],
        "fake_sample_id_2": {
            "mock data": "anything",
            "creation_datetime": "2021-05-02T16:43:04Z",
            "lanes": [
                {
                    "id": "fake_lane_id_4",
                    "qc_lib": 0,
                    "qc_seq": 0,
                    "qc_success": 0,
                    "qc_status_text": "Sequencing QC failed",
                    "run_status": "anything other than complete",
                    "qc_started": 0,
                    "qc_complete_datetime": "any string will do",
                }
            ],
        },
    }

    mock_filtered_samples3 = mock_filtered_samples2

    mock_metadata = [
        {
            "sanger_sample_id": {"order": 1, "title": "Sanger_Sample_ID", "value": "fake_sample_id_1"},
            "some_other_column": {"order": 2, "title": "Something_Made_Up", "value": ""},
            # note use of `None`, which should end up in CSV as ""
            "another_fake_column": {"order": 3, "title": "Also_Made_Up", "value": None},
            "lane_id": {"order": 4, "title": "Lane_ID", "value": "fake_lane_id_1"},
            "public_name": {"order": 5, "title": "Public_Name", "value": "fake_public_name_1"},
        },
        {
            "sanger_sample_id": {"order": 1, "title": "Sanger_Sample_ID", "value": "fake_sample_id_2"},
            "some_other_column": {"order": 2, "title": "Something_Made_Up", "value": ""},
            "another_fake_column": {"order": 3, "title": "Also_Made_Up", "value": "whatevs"},
            "lane_id": {"order": 4, "title": "Lane_ID", "value": "fake_lane_id_2"},
            "public_name": {"order": 5, "title": "Public_Name", "value": "fake public name 2"},
        },
    ]
    mock_in_silico_data = [
        {
            "lane_id": {"order": 1, "title": "Sample_id", "value": "fake_lane_id_3"},
            "some_in_silico_thing": {"order": 2, "title": "In_Silico_Thing", "value": "pos"},
            "another_in_silico_thing": {"order": 3, "title": "Another_In_Silico_Thing", "value": "neg"},
        }
    ]
    mock_qc_data = [
        {
            "lane_id": {"order": 1, "title": "lane_id", "value": "fake_lane_id_3"},
            "some_qc_thing": {"order": 2, "title": "QC_Thing", "value": "42"},
        }
    ]
    # the return value when no in silico data are available
    in_silico_data_available_not_available = []
    # the return value when no QC data are available
    qc_data_available_not_available = []
    # these contain a bad lane ID, so it should be ignored and *not* merged into the metadata download
    mock_in_silico_data_bad_lane_id = [
        {
            "lane_id": {"order": 1, "title": "Sample_id", "value": "this_is_a_bad_id"},
            "some_in_silico_thing": {"order": 2, "title": "In_Silico_Thing", "value": "pos"},
            "another_in_silico_thing": {"order": 3, "title": "Another_In_Silico_Thing", "value": "neg"},
        },
        {
            "lane_id": {"order": 1, "title": "Sample_id", "value": "fake_lane_id_2"},
            "some_in_silico_thing": {"order": 2, "title": "In_Silico_Thing", "value": "pos"},
            "another_in_silico_thing": {"order": 3, "title": "Another_In_Silico_Thing", "value": "neg"},
        },
    ]
    mock_qc_data_bad_lane_id = [
        {
            "lane_id": {"order": 1, "title": "lane_id", "value": "this_is_a_bad_id"},
            "some_qc_thing": {"order": 2, "title": "QC_Thing", "value": "42"},
        },
        {
            "lane_id": {"order": 1, "title": "lane_id", "value": "fake_lane_id_2"},
            "some_qc_thing": {"order": 2, "title": "QC_Thing", "value": "42"},
        },
    ]

    # `total rows` and `last row` reflect the 3 rows that exist in mock_filtered_samples
    mock_combined_metadata = {
        "samples": [
            {"metadata": mock_metadata[0]},
            {
                "metadata": mock_metadata[1],
            },
        ],
        "total rows": 3,
        "last row": 3,
    }
    mock_combined_metadata_plus_in_silico = {
        "samples": [
            {"metadata": mock_metadata[0], "in silico": mock_in_silico_data[0]},
            {
                "metadata": mock_metadata[1],
            },
        ],
        "total rows": 3,
        "last row": 3,
    }
    mock_combined_metadata_plus_in_silico_qc = {
        "samples": [
            {"metadata": mock_metadata[0], "in silico": mock_in_silico_data[0], "qc data": mock_qc_data[0]},
            {
                "metadata": mock_metadata[1],
            },
        ],
        "total rows": 3,
        "last row": 3,
    }
    mock_combined_metadata_filtered = {
        "samples": [
            {"metadata": {"public_name": mock_metadata[0]["public_name"]}},
            {"metadata": {"public_name": mock_metadata[1]["public_name"]}},
        ],
        "total rows": 3,
        "last row": 3,
    }
    mock_combined_metadata_in_silico_filtered = {
        "samples": [
            {
                "metadata": {"public_name": mock_metadata[0]["public_name"]},
                "in silico": {"some_in_silico_thing": mock_in_silico_data[0]["some_in_silico_thing"]},
            },
            {"metadata": {"public_name": mock_metadata[1]["public_name"]}},
        ],
        "total rows": 3,
        "last row": 3,
    }

    # these are invalid because the lane ID appears twice:  pandas merge should catch this in validation
    mock_invalid_metadata = [mock_metadata[0], mock_metadata[1], mock_metadata[0]]
    mock_invalid_in_silico_data = [mock_in_silico_data[0], mock_in_silico_data[0]]
    mock_invalid_qc_data = [mock_qc_data[0], mock_qc_data[0]]

    mock_metadata2 = [
        {
            "sanger_sample_id": {"order": 1, "title": "Sanger_Sample_ID", "value": "fake_sample_id_1"},
            "field1": {"order": 1, "title": "Something_Made_Up", "value": "a"},
            "field2": {"order": 2, "title": "Something_Else", "value": "d"},
        },
        {
            "sanger_sample_id": {"order": 1, "title": "Sanger_Sample_ID", "value": "fake_sample_id_2"},
            "field1": {"order": 1, "title": "Something_Made_Up", "value": "b"},
            "field2": {"order": 2, "title": "Something_Else", "value": "e"},
        },
    ]
    mock_in_silico_data2 = [
        {
            "lane_id": {"order": 1, "title": "Sample_id", "value": "fake_lane_id_3"},
            "field3": {"order": 2, "title": "In_Silico_Thing", "value": "f"},
        },
        {
            "lane_id": {"order": 1, "title": "Sample_id", "value": "fake_lane_id_4"},
            "field3": {"order": 2, "title": "In_Silico_Thing", "value": "g"},
        },
        {
            "lane_id": {"order": 1, "title": "Sample_id", "value": "fake_lane_id_5"},
            "field3": {"order": 2, "title": "In_Silico_Thing", "value": "h"},
        },
    ]

    mock_metadata_with_submitting_institutions = [
        {
            "sanger_sample_id": {"order": 1, "title": "Sanger_Sample_ID", "value": "fake_sample_id_1"},
            "submitting_institution": {
                "order": 1,
                "title": "Submitting_Institution",
                "value": mock_institution_keys[0],
            },
        },
        {
            "sanger_sample_id": {"order": 1, "title": "Sanger_Sample_ID", "value": "fake_sample_id_2"},
            "submitting_institution": {
                "order": 1,
                "title": "Submitting_Institution",
                "value": mock_institution_keys[1],
            },
        },
    ]

    expected_metadata_download = {
        "success": True,
        "filename": "FakOne_sequencing_successful.csv",
        "content": EXPECTED_METADATA_PLUS_QC_AND_IN_SILICO_DATA,
    }

    expected_metadata_download_not_found = {
        "success": False,
        "error": "not found",
        "message": "No matching samples were found.",
    }

    expected_metadata_download_reject_missing = {
        "success": False,
        "error": "request",
        "message": 'institution "{}" passed, but should be one of "{}"'.format(
            mock_bad_institution_key, '", "'.join(mock_institution_keys)
        ),
    }

    expected_metadata_download_error_response = {"success": False, "error": "internal"}

    # create MonocleSampleData object outside setUp() to avoid creating multipe instances
    # this means we use cached data rather than making multiple patched queries to SampleMetadata etc.
    monocle_sample_tracking = MonocleSampleTracking(set_up=False)
    monocle_data = MonocleSampleData(
        data_source_config=test_config,
        MonocleSampleTracking_ref=monocle_sample_tracking,
    )

    @patch.dict(environ, mock_environment, clear=True)
    def setUp(self):
        # mock sample_metadata
        self.monocle_sample_tracking.institution_ldap_data = InstitutionData(set_up=False)
        self.monocle_sample_tracking.sample_metadata = SampleMetadata(set_up=False)
        self.monocle_sample_tracking.sample_metadata.monocle_client = MonocleClient(set_up=False)
        self.monocle_sample_tracking.sample_metadata.monocle_client.set_up(self.test_config)
        # mock sequencing_status
        self.monocle_sample_tracking.sequencing_status_source = SequencingStatus(set_up=False)
        self.monocle_sample_tracking.sequencing_status_source.mlwh_client = MLWH_Client(set_up=False)
        self.monocle_sample_tracking.sequencing_status_source.mlwh_client.set_up(self.test_config)
        # mock metadata_download
        self.monocle_data.current_project = self.mock_project_id
        self.monocle_data.metadata_download_source = MetadataDownload(set_up=False)
        self.monocle_data.metadata_download_source._institutions = {}
        self.monocle_data.metadata_download_source.download_client = MonocleDownloadClient(set_up=False)
        self.monocle_data.metadata_download_source.download_client.set_up(self.test_config)
        # load mock data
        self.get_mock_data()

    def test_init(self):
        self.assertIsInstance(self.monocle_sample_tracking, MonocleSampleTracking)
        self.assertIsInstance(self.monocle_data, MonocleSampleData)
        self.assertIsInstance(self.monocle_data.sample_tracking, MonocleSampleTracking)

    def test_init_reject_missing_config(self):
        with self.assertRaises(DataSourceConfigError):
            MonocleSampleData(
                data_source_config="no/such/file",
                MonocleSampleTracking_ref=self.monocle_sample_tracking,
            )

    @patch.object(InstitutionData, "get_all_institutions_regardless_of_user_membership")
    @patch.object(SampleMetadata, "get_samples")
    @patch.object(SequencingStatus, "get_multiple_samples")
    def get_mock_data(self, mock_seq_samples_query, mock_db_sample_query, mock_institutions_query):
        self.monocle_sample_tracking.sequencing_status_data = None
        mock_institutions_query.return_value = self.mock_institution_data
        mock_db_sample_query.return_value = self.mock_samples
        mock_seq_samples_query.return_value = self.mock_seq_status
        self.monocle_sample_tracking.get_institutions()
        self.monocle_sample_tracking.get_samples()
        self.monocle_sample_tracking.get_sequencing_status()

    # this can be called to load alternative data set
    @patch.object(SampleMetadata, "get_samples")
    @patch.object(SequencingStatus, "get_multiple_samples")
    @patch.dict(environ, mock_environment, clear=True)
    def get_mock_data2(self, mock_seq_samples_query, mock_db_sample_query):
        self.monocle_sample_tracking.sequencing_status_data = None
        self.monocle_sample_tracking.pipeline_status = PipelineStatus(self.mock_project_id, config=self.test_config)
        mock_db_sample_query.return_value = self.mock_samples2
        mock_seq_samples_query.return_value = self.mock_seq_status2
        self.monocle_sample_tracking.get_institutions()
        self.monocle_sample_tracking.get_samples()
        self.monocle_sample_tracking.get_sequencing_status()

    # this can be called to load a 3rd data set
    @patch.object(SampleMetadata, "get_samples")
    @patch.object(SequencingStatus, "get_multiple_samples")
    def get_mock_data3(self, mock_seq_samples_query, mock_db_sample_query):
        self.monocle_sample_tracking.sequencing_status_data = None
        mock_db_sample_query.return_value = self.mock_samples3
        mock_seq_samples_query.return_value = self.mock_seq_status3
        self.monocle_sample_tracking.get_institutions()
        self.monocle_sample_tracking.get_samples()
        self.monocle_sample_tracking.get_sequencing_status()

    @patch.object(Path, "exists", return_value=True)
    @patch.object(MonocleSampleData, "_get_file_size")
    @patch.object(SampleMetadata, "get_samples")
    @patch.dict(environ, mock_environment, clear=True)
    def test_get_bulk_download_info(self, get_sample_metadata_mock, get_file_size_mock, _path_exists_mock):
        get_sample_metadata_mock.return_value = self.mock_samples
        file_size = 420024
        get_file_size_mock.return_value = file_size

        bulk_download_info = self.monocle_data.get_bulk_download_info(
            {"batches": self.inst_key_batch_date_pairs}, assemblies=True, annotations=False
        )

        expected_num_samples = len(self.inst_key_batch_date_pairs)
        num_lanes = 5
        expected_byte_size = file_size * num_lanes
        self.assertEqual(
            {
                "num_samples": expected_num_samples,
                "size": format_file_size(expected_byte_size),
                "size_zipped": format_file_size(expected_byte_size / ZIP_COMPRESSION_FACTOR_ASSEMBLIES_ANNOTATIONS),
                "size_per_zip_options": [
                    {"max_samples_per_zip": expected_num_samples, "size_per_zip": format_file_size(expected_byte_size)}
                ],
                "num_samples_restricted_to": None,
            },
            bulk_download_info,
        )

    @patch.object(Path, "exists", return_value=True)
    @patch.object(MonocleSampleData, "_get_file_size")
    @patch.object(MonocleSampleData, "get_bulk_download_max_samples_per_download")
    @patch.object(SampleMetadata, "get_samples")
    @patch.dict(environ, mock_environment, clear=True)
    def test_get_bulk_download_info_restricted_num_samples(
        self, get_sample_metadata_mock, get_max_samples_mock, get_file_size_mock, _path_exists_mock
    ):
        get_sample_metadata_mock.return_value = self.mock_samples
        file_size = 420024
        get_file_size_mock.return_value = file_size
        # just for this test, reduce to less than the number of mock samples MAXIMUM_NUM_SAMPLES_IN_BULK_DOWNLOAD to 1
        # (but this assumes there are at least 2 mock samples, so check this first!)
        if len(self.mock_samples) < 2:
            raise RuntimeError("Test {} requires that at least 2 mock samples are provided".format(__class__.__name__))
        get_max_samples_mock.return_value = 1

        bulk_download_info = self.monocle_data.get_bulk_download_info(
            {"batches": self.inst_key_batch_date_pairs}, assemblies=True, annotations=False
        )

        expected_num_samples = self.monocle_data.get_bulk_download_max_samples_per_download()
        num_lanes = 3
        expected_byte_size = file_size * num_lanes
        self.assertEqual(
            {
                "num_samples": expected_num_samples,
                "size": format_file_size(expected_byte_size),
                "size_zipped": format_file_size(expected_byte_size / ZIP_COMPRESSION_FACTOR_ASSEMBLIES_ANNOTATIONS),
                "size_per_zip_options": [
                    {"max_samples_per_zip": expected_num_samples, "size_per_zip": format_file_size(expected_byte_size)}
                ],
                "num_samples_restricted_to": self.monocle_data.get_bulk_download_max_samples_per_download(),
            },
            bulk_download_info,
        )

    @patch.object(Path, "exists", return_value=True)
    @patch.object(MonocleSampleData, "_get_file_size")
    @patch.object(SampleMetadata, "get_samples")
    @patch.dict(environ, mock_environment, clear=True)
    def test_get_bulk_download_info_with_reads(self, get_sample_metadata_mock, get_file_size_mock, _path_exists_mock):
        get_sample_metadata_mock.return_value = self.mock_samples
        file_size = 420024
        get_file_size_mock.return_value = file_size

        bulk_download_info = self.monocle_data.get_bulk_download_info(
            {"batches": self.inst_key_batch_date_pairs}, assemblies=True, annotations=False, reads=True
        )

        expected_num_samples = len(self.inst_key_batch_date_pairs)
        num_lanes = 5 * expected_num_samples
        expected_byte_size = file_size * num_lanes
        self.assertEqual(
            {
                "num_samples": expected_num_samples,
                "size": format_file_size(expected_byte_size),
                "size_zipped": format_file_size(expected_byte_size / ZIP_COMPRESSION_FACTOR_ASSEMBLIES_ANNOTATIONS),
                "size_per_zip_options": [
                    {"max_samples_per_zip": expected_num_samples, "size_per_zip": format_file_size(expected_byte_size)}
                ],
                "num_samples_restricted_to": None,
            },
            bulk_download_info,
        )

    @patch.object(MonocleDownloadClient, "metadata")
    def test_get_metadata(self, mock_metadata_fetch):
        """
        sample_data_services.MonocleSampleData.get_metadata should return sample metadata in expected format,
        without in silico or QC data when `include_in_silico=False` and `include_qc_data=False`is passed; and
        should default to the same if `include_in_silico` and `include_qc_data` are not defined
        """
        mock_metadata_fetch.return_value = self.mock_metadata
        filtered_samples_metadata = self.monocle_data.get_metadata(
            {"batches": self.inst_key_batch_date_pairs}, include_in_silico=False, include_qc_data=False
        )
        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata, filtered_samples_metadata))
        self.assertEqual(self.mock_combined_metadata, filtered_samples_metadata)
        filtered_samples_metadata = self.monocle_data.get_metadata({"batches": self.inst_key_batch_date_pairs})
        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata, filtered_samples_metadata))
        self.assertEqual(self.mock_combined_metadata, filtered_samples_metadata)

    @patch.object(MonocleDownloadClient, "in_silico_data")
    @patch.object(MonocleDownloadClient, "metadata")
    def test_get_metadata_plus_in_silico(self, mock_metadata_fetch, mock_in_silico_data_fetch):
        """
        sample_data_services.MonocleSampleData.get_metadata should return sample metadata in expected format,
        with added in silico data when `include_in_silico=True` is passed
        """
        mock_metadata_fetch.return_value = self.mock_metadata
        mock_in_silico_data_fetch.return_value = self.mock_in_silico_data
        filtered_samples_metadata = self.monocle_data.get_metadata(
            {"batches": self.inst_key_batch_date_pairs}, include_in_silico=True
        )
        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata_plus_in_silico, filtered_samples_metadata))
        self.assertEqual(self.mock_combined_metadata_plus_in_silico, filtered_samples_metadata)

    @patch.object(MonocleDownloadClient, "qc_data")
    @patch.object(MonocleDownloadClient, "in_silico_data")
    @patch.object(MonocleDownloadClient, "metadata")
    def test_get_metadata_plus_in_silico_and_qc_data(
        self, mock_metadata_fetch, mock_in_silico_data_fetch, mock_qc_data_fetch
    ):
        """
        sample_data_services.MonocleSampleData.get_metadata should return sample metadata in expected format,
        with added in silico and QC data when `include_in_silico=True` and `include_qc_data=True` are passed
        """
        mock_metadata_fetch.return_value = self.mock_metadata
        mock_in_silico_data_fetch.return_value = self.mock_in_silico_data
        mock_qc_data_fetch.return_value = self.mock_qc_data
        filtered_samples_metadata = self.monocle_data.get_metadata(
            {"batches": self.inst_key_batch_date_pairs}, include_in_silico=True, include_qc_data=True
        )
        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata_plus_in_silico_qc, filtered_samples_metadata))
        self.assertEqual(self.mock_combined_metadata_plus_in_silico_qc, filtered_samples_metadata)

    @patch.object(MonocleDownloadClient, "metadata")
    def test_get_metadata_filtered_columns(self, mock_metadata_fetch):
        """
        sample_data_services.MonocleSampleData.get_metadata should filter the response to include
        only the requested columns
        """
        mock_metadata_fetch.return_value = deepcopy(self.mock_metadata)  # work on a copy, as metadata will be modified
        filtered_samples_metadata = self.monocle_data.get_metadata(
            {"batches": self.inst_key_batch_date_pairs}, metadata_columns=["public_name"]
        )
        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata_filtered, filtered_samples_metadata))
        self.assertEqual(self.mock_combined_metadata_filtered, filtered_samples_metadata)

    @patch.object(MonocleSampleData, "get_filtered_samples")
    def test_get_metadata_no_matching_samples(self, mock_get_filtered_samples):
        """
        sample_data_services.MonocleSampleData.get_metadata should gracefully handle a case of the filters
        matching zero samples, by just returning an empty response
        """
        mock_get_filtered_samples.return_value = []
        filtered_samples_metadata = self.monocle_data.get_metadata({"batches": self.inst_key_batch_date_pairs})
        self.assertIsNone(filtered_samples_metadata)
        filtered_samples_metadata_plus_in_silico_and_qc = self.monocle_data.get_metadata(
            {"batches": self.inst_key_batch_date_pairs}, include_in_silico=True, include_qc_data=True
        )
        self.assertIsNone(filtered_samples_metadata_plus_in_silico_and_qc)

    @patch.object(MonocleDownloadClient, "in_silico_data")
    @patch.object(MonocleDownloadClient, "metadata")
    def test_get_metadata_start_row_out_of_range_ok(self, mock_metadata_fetch, mock_in_silico_data_fetch):
        """
        sample_data_services.MonocleSampleData.get_metadata should gracefully handle a start_row parameter that
        "points" to a row beyond the total number of rows, by just returning an empty response
        """
        mock_metadata_fetch.return_value = self.mock_metadata
        mock_in_silico_data_fetch.return_value = self.mock_in_silico_data
        filtered_samples_metadata = self.monocle_data.get_metadata(
            {"batches": self.inst_key_batch_date_pairs}, start_row=9999, num_rows=1
        )
        self.assertIsNone(filtered_samples_metadata)
        filtered_samples_metadata_plus_in_silico = self.monocle_data.get_metadata(
            {"batches": self.inst_key_batch_date_pairs}, include_in_silico=True, start_row=9999, num_rows=1
        )
        self.assertIsNone(filtered_samples_metadata_plus_in_silico)

    @patch.object(MonocleDownloadClient, "metadata")
    def test_get_metadata_num_rows_out_of_range_ok(self, mock_metadata_fetch):
        """
        sample_data_services.MonocleSampleData.get_metadata should gracefully handle num_rows parameter that
        "points" to a row beyond the total number of rows, by just returning all available rows
        """
        mock_metadata_fetch.return_value = self.mock_metadata
        filtered_samples_metadata = self.monocle_data.get_metadata(
            {"batches": self.inst_key_batch_date_pairs}, start_row=1, num_rows=9999
        )
        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata, filtered_samples_metadata))
        self.assertEqual(self.mock_combined_metadata, filtered_samples_metadata)

    def test_get_metadata_pagination_reject_missing_num_rows(self):
        """
        sample_data_services.MonocleSampleData.get_metadata should raise AssertionError if only
        one pagination param start_row is passwd with a num_rows param
        (note if start_row is not defined, num_rows is simply ignored)
        """
        with self.assertRaises(AssertionError):
            self.monocle_data.get_metadata(
                {"batches": self.inst_key_batch_date_pairs}, metadata_columns=["public_name"], start_row=2
            )

    @patch.object(MonocleDownloadClient, "in_silico_data")
    @patch.object(MonocleDownloadClient, "metadata")
    def test_get_metadata_plus_in_silico_filtered_columns(self, mock_metadata_fetch, mock_in_silico_data_fetch):
        mock_metadata_fetch.return_value = deepcopy(self.mock_metadata)  # work on a copy, as metadata will be modified
        mock_in_silico_data_fetch.return_value = deepcopy(
            self.mock_in_silico_data
        )  # work on a copy, as metadata will be modified
        filtered_samples_metadata = self.monocle_data.get_metadata(
            {"batches": self.inst_key_batch_date_pairs},
            metadata_columns=["public_name"],
            in_silico_columns=["some_in_silico_thing"],
            include_in_silico=True,
        )
        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata_in_silico_filtered, filtered_samples_metadata))
        self.assertEqual(self.mock_combined_metadata_in_silico_filtered, filtered_samples_metadata)

    @patch.object(SampleMetadata, "get_samples")
    def test_get_filtered_samples(self, get_sample_metadata_mock):
        get_sample_metadata_mock.return_value = self.mock_samples

        actual_samples = self.monocle_data.get_filtered_samples({"batches": self.inst_key_batch_date_pairs})

        expected_samples = self.mock_filtered_samples
        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(expected_samples, actual_samples))
        self.assertEqual(expected_samples, actual_samples)

    def test_get_filtered_samples_accepts_empty_list(self):
        samples = self.monocle_data.get_filtered_samples({"batches": []})

        self.assertEqual([], samples)

    @patch.object(SampleMetadata, "get_samples")
    def test_get_filtered_samples_ignores_institution_keys_that_are_not_in_seq_status_data(
        self, get_sample_metadata_mock
    ):
        get_sample_metadata_mock.return_value = self.mock_samples
        inst_key_batch_date_pairs = deepcopy(self.inst_key_batch_date_pairs)
        inst_key_batch_date_pairs.append({"institution key": "nonExistentInst", "batch date": "2021-01-27"})

        actual_samples = self.monocle_data.get_filtered_samples({"batches": inst_key_batch_date_pairs})

        expected_samples = self.mock_filtered_samples
        self.assertEqual(expected_samples, actual_samples)

    @patch.dict(environ, mock_environment, clear=True)
    @patch.object(SampleMetadata, "get_samples")
    def test_get_filtered_samples_with_sequencing_success_filter(self, get_sample_metadata_mock):
        self.get_mock_data2()

        # mock_samples2 contains a successful and a failed lane for fake_sample_id_1; fake_sample_id_2 has only a failed lane
        get_sample_metadata_mock.return_value = self.mock_samples2

        # should return fake_sample_id_1 as it has one successful lane
        actual_samples = self.monocle_data.get_filtered_samples(
            {"batches": self.inst_key_batch_date_pairs, "sequencing": {"success": True}}
        )

        expected_samples = self.mock_filtered_samples2
        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(expected_samples, actual_samples))
        self.assertEqual(expected_samples, actual_samples)
        self.get_mock_data()

    @patch.dict(environ, mock_environment, clear=True)
    @patch.object(SampleMetadata, "get_samples")
    def test_get_filtered_samples_with_sequencing_complete_filter(self, get_sample_metadata_mock):
        self.get_mock_data3()

        # mock_samples3 contains a complete and incomplete lane for fake_sample_id_1; fake_sample_id_2 has only an incomplete lane
        get_sample_metadata_mock.return_value = self.mock_samples3

        # should return fake_sample_id_1 as it has one complete lane
        actual_samples = self.monocle_data.get_filtered_samples(
            {"batches": self.inst_key_batch_date_pairs, "sequencing": {"complete": True}}
        )

        expected_samples = self.mock_filtered_samples3
        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(expected_samples, actual_samples))
        self.assertEqual(expected_samples, actual_samples)
        self.get_mock_data()

    @patch.dict(environ, mock_environment, clear=True)
    @patch.object(SampleMetadata, "get_samples")
    @patch.object(PipelineStatus, "lane_status")
    def test_get_filtered_samples_with_pipeline_success_filter(self, lane_status_mock, get_sample_metadata_mock):
        self.get_mock_data2()
        get_sample_metadata_mock.return_value = self.mock_samples2
        # assigning list to side_effect returns next value each time mocked function is called
        # N.B.  the code only checks each sample's lanes until it finds one that succeeded.
        #       The mock data have 3 lanes for fake_sample_id_1, but after the second lane is
        #       checked and found to be successful, no more lanes for fake_sample_id_1 should
        #       be checked.  => even though we have mocked 4 lanes, only 3 calls are expected
        lane_status_mock.side_effect = [
            {"SUCCESS": False, "FAILED": True},  # fake_sample_id_1: first lane failed
            {"SUCCESS": True, "FAILED": False},  # fake_sample_id_1: second lane succeeded
            {"SUCCESS": False, "FAILED": True},  # fake_sample_id_2: lane failed
        ]

        # should return fake_sample_id_1 as it has one successful lane
        actual_samples = self.monocle_data.get_filtered_samples(
            {"batches": self.inst_key_batch_date_pairs, "pipeline": {"success": True}}
        )

        expected_samples = self.mock_filtered_samples2
        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(expected_samples, actual_samples))
        self.assertEqual(expected_samples, actual_samples)
        self.get_mock_data()

    @patch.dict(environ, mock_environment, clear=True)
    @patch.object(SampleMetadata, "get_samples")
    @patch.object(PipelineStatus, "lane_status")
    def test_get_filtered_samples_with_pipeline_complete_filter(self, lane_status_mock, get_sample_metadata_mock):
        self.get_mock_data2()
        get_sample_metadata_mock.return_value = self.mock_samples2
        # assigning list to side_effect returns next value each time mocked function is called
        # N.B.  the code only checks each sample's lanes until it finds one that completed.
        #       The mock data have 3 lanes for fake_sample_id_1, but after the first lane is
        #       checked and found to be complete, no more lanes for fake_sample_id_1 should
        #       be checked.  => even though we have mocked 4 lanes, only 2 calls are expected
        lane_status_mock.side_effect = [
            {"SUCCESS": False, "FAILED": True},  # fake_sample_id_1: first lane failed => complete
            {"SUCCESS": False, "FAILED": False},  # fake_sample_id_2: no status available => incomplete
        ]

        # should return fake_sample_id_1 as it has one complete lane
        actual_samples = self.monocle_data.get_filtered_samples(
            {"batches": self.inst_key_batch_date_pairs, "pipeline": {"complete": True}}
        )

        expected_samples = self.mock_filtered_samples2
        # logging.critical("\n***** EXPECTED:\n{}\nGOT:\n{}".format(expected_samples, actual_samples))
        self.assertEqual(expected_samples, actual_samples)
        self.get_mock_data()

    @patch.object(Path, "exists", return_value=True)
    @patch.dict(environ, mock_environment, clear=True)
    def test_get_public_name_to_lane_files_dict(self, _path_exists_mock):
        samples = self.mock_seq_status.values()
        for sample in samples:
            if not sample:
                continue
            sample["inst_key"] = INSTITUTION_KEY
            sample["public_name"] = PUBLIC_NAME

        public_name_to_lane_files = self.monocle_data.get_public_name_to_lane_files_dict(
            samples, assemblies=True, annotations=False
        )

        expected_lane_files = [
            PurePath(self.mock_inst_view_dir, INSTITUTION_KEY, PUBLIC_NAME, f"{lane}.contigs_spades.fa")
            for sample in samples
            if sample
            for lane in sample["lanes"]
        ]
        expected = {PUBLIC_NAME: expected_lane_files}
        self.assertEqual(expected, public_name_to_lane_files)

    @patch.object(Path, "exists", return_value=False)
    @patch.dict(environ, mock_environment, clear=True)
    def test_get_public_name_to_lane_files_dict_ignores_non_existent_files(self, _path_exists_mock):
        samples = self.mock_seq_status.values()
        for sample in samples:
            if not sample:
                continue
            sample["inst_key"] = INSTITUTION_KEY
            sample["public_name"] = PUBLIC_NAME

        public_name_to_lane_files = self.monocle_data.get_public_name_to_lane_files_dict(
            samples, assemblies=True, annotations=False
        )

        self.assertEqual({}, public_name_to_lane_files)

    def test_get_public_name_to_lane_files_dict_rejects_if_data_institution_view_env_var_is_not_set(self):
        samples = list(self.mock_seq_status.values())

        with self.assertRaises(DataSourceConfigError):
            self.monocle_data.get_public_name_to_lane_files_dict(samples, assemblies=True, annotations=False)

    @patch.dict(environ, mock_environment, clear=True)
    def test_get_zip_download_location(self):
        download_location = self.monocle_data.get_bulk_download_location()

        self.assertEqual(PurePath(self.mock_inst_view_dir, "downloads"), download_location)

    @patch.dict(environ, mock_environment, clear=True)
    def test_get_zip_download_location_raises_if_data_inst_view_is_not_in_environ(self):
        del environ["JUNO_DATA_INSTITUTION_VIEW"]

        with self.assertRaises(DataSourceConfigError):
            self.monocle_data.get_bulk_download_location()

    def test_get_zip_download_location_raises_if_data_config_is_corrupt(self):
        monocle_data_with_bad_config = MonocleSampleData(
            MonocleSampleTracking_ref=self.monocle_sample_tracking, set_up=False
        )
        monocle_data_with_bad_config.current_project = self.mock_project_id
        monocle_data_with_bad_config.data_source_config_name = self.test_config_bad

        with self.assertRaises(DataSourceConfigError):
            monocle_data_with_bad_config.get_bulk_download_location()

    def test_get_bulk_download_route(self):
        download_route = self.monocle_data.get_bulk_download_route()
        self.assertEqual(self.mock_download_route, download_route)

    def test_get_bulk_download_route_reject_bad_config(self):
        monocle_data_with_bad_config = MonocleSampleData(
            MonocleSampleTracking_ref=self.monocle_sample_tracking, set_up=False
        )
        monocle_data_with_bad_config.data_source_config_name = self.test_config_bad
        with self.assertRaises(DataSourceConfigError):
            monocle_data_with_bad_config.get_bulk_download_route()

    def test_get_bulk_download_max_samples_per_zip(self):
        download_max_samples_per_zip = self.monocle_data.get_bulk_download_max_samples_per_zip()
        self.assertEqual(self.mock_download_max_samples_per_zip, download_max_samples_per_zip)

    def test_get_bulk_download_max_samples_per_zip_excluding_reads(self):
        download_max_samples_per_zip = self.monocle_data.get_bulk_download_max_samples_per_zip(including_reads=False)
        self.assertEqual(self.mock_download_max_samples_per_zip, download_max_samples_per_zip)

    def test_get_bulk_download_max_samples_per_zip_including_reads(self):
        download_max_samples_per_zip = self.monocle_data.get_bulk_download_max_samples_per_zip(including_reads=True)
        self.assertEqual(self.mock_download_max_samples_per_zip_with_reads, download_max_samples_per_zip)

    def test_get_bulk_download_max_samples_per_zip_reject_bad_config(self):
        monocle_data_with_bad_config = MonocleSampleData(
            MonocleSampleTracking_ref=self.monocle_sample_tracking, set_up=False
        )
        monocle_data_with_bad_config.data_source_config_name = self.test_config_bad
        with self.assertRaises(DataSourceConfigError):
            monocle_data_with_bad_config.get_bulk_download_max_samples_per_zip()

    @patch.object(MonocleSampleData, "make_download_symlink")
    @patch.object(MonocleDownloadClient, "qc_data")
    @patch.object(MonocleDownloadClient, "in_silico_data")
    @patch.object(MonocleDownloadClient, "metadata")
    def test_get_metadata_for_download(
        self, mock_metadata_fetch, mock_in_silico_data_fetch, mock_qc_data_fetch, mock_make_symlink
    ):
        mock_metadata_fetch.return_value = self.mock_metadata
        mock_in_silico_data_fetch.return_value = self.mock_in_silico_data
        mock_qc_data_fetch.return_value = self.mock_qc_data
        mock_make_symlink.return_value = MOCK_DOWNLOAD_PATH

        metadata_download = self.monocle_data.get_metadata_for_download(
            MOCK_DOWNLOAD_HOST, self.mock_institution_keys[0], "sequencing", "successful"
        )

        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.expected_metadata_download, metadata_download))
        self.assertEqual(self.expected_metadata_download, metadata_download)

    @patch.object(MonocleSampleData, "make_download_symlink")
    @patch.object(MonocleSampleData, "_metadata_as_csv")
    def test_get_metadata_for_download_not_found_ok(self, mock_metadata_as_csv, mock_make_symlink):
        mock_metadata_as_csv.return_value = None
        mock_make_symlink.return_value = MOCK_DOWNLOAD_PATH

        metadata_download = self.monocle_data.get_metadata_for_download(
            MOCK_DOWNLOAD_HOST, self.mock_institution_keys[0], "sequencing", "successful"
        )

        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.expected_metadata_download_not_found, metadata_download))
        self.assertEqual(self.expected_metadata_download_not_found, metadata_download)

    @patch.object(MonocleDownloadClient, "qc_data")
    @patch.object(MonocleDownloadClient, "in_silico_data")
    @patch.object(MonocleDownloadClient, "metadata")
    def test_get_metadata_for_download_reject_missing_institution(
        self, mock_metadata_fetch, mock_in_silico_data_fetch, mock_qc_data_fetch
    ):
        mock_metadata_fetch.return_value = self.mock_metadata
        mock_in_silico_data_fetch.return_value = self.mock_in_silico_data
        mock_qc_data_fetch.return_value = self.mock_qc_data

        metadata_download = self.monocle_data.get_metadata_for_download(
            MOCK_DOWNLOAD_HOST, self.mock_bad_institution_key, "sequencing", "successful"
        )

        self.assertEqual(self.expected_metadata_download_reject_missing, metadata_download)

    @patch.object(MonocleSampleData, "make_download_symlink")
    @patch.object(MonocleDownloadClient, "qc_data")
    @patch.object(MonocleDownloadClient, "in_silico_data")
    @patch.object(MonocleDownloadClient, "metadata")
    def test_get_metadata_for_download_error_response(
        self, mock_metadata_fetch, mock_in_silico_data_fetch, mock_qc_data_fetch, mock_make_symlink
    ):
        mock_metadata_fetch.return_value = self.mock_metadata
        mock_in_silico_data_fetch.return_value = self.mock_in_silico_data
        mock_qc_data_fetch.return_value = self.mock_qc_data
        mock_make_symlink.return_value = None

        metadata_download = self.monocle_data.get_metadata_for_download(
            MOCK_DOWNLOAD_HOST, self.mock_institution_keys[0], "sequencing", "successful"
        )

        self.assertEqual(self.expected_metadata_download_error_response, metadata_download)

    # get_csv_download() mostly covered by get_metadata_for_download() tests above
    # this checks param validation
    def test_get_csv_download_reject_invalid_download_params(self):
        # missing download_links `hostname` key
        with self.assertRaises(KeyError):
            self.monocle_data.get_csv_download(
                "any_name.csv",
                {"mock filter name": "mock filter value"},
                download_links={"institution": "any institution"},
            )

    @patch.dict(environ, mock_environment, clear=True)
    def test_make_download_symlink(self):
        test_inst_key = self.mock_institution_keys[0]
        self._symlink_test_setup(test_inst_key)

        symlink_url_path = self.monocle_data.make_download_symlink(test_inst_key)

        symlink_disk_path = symlink_url_path.replace(self.mock_url_path, self.mock_web_dir, 1)

        # test the symlink is actually a symlink, and that it points at the intended target
        self.assertTrue(Path(symlink_disk_path).is_symlink())
        self.assertEqual(Path(self.mock_inst_view_dir, test_inst_key).absolute(), Path(symlink_disk_path).resolve())
        self._symlink_test_teardown()

    @patch.dict(environ, mock_environment, clear=True)
    def test_make_download_symlink_cross_institution(self):
        cross_institution_dir = "downloads"
        self._symlink_test_setup(cross_institution_dir)

        symlink_url_path = self.monocle_data.make_download_symlink(cross_institution=True)

        symlink_disk_path = symlink_url_path.replace(self.mock_url_path, self.mock_web_dir, 1)
        # test the symlink is actually a symlink, and that it points at the intended target
        self.assertTrue(Path(symlink_disk_path).is_symlink())
        self.assertEqual(
            Path(self.mock_inst_view_dir, cross_institution_dir).absolute(), Path(symlink_disk_path).resolve()
        )
        self._symlink_test_teardown()

    def _symlink_test_setup(self, mock_inst_key):
        Path(self.mock_inst_view_dir, mock_inst_key).mkdir(parents=True, exist_ok=True)
        Path(self.mock_web_dir).mkdir(parents=True, exist_ok=True)

    def _symlink_test_teardown(self):
        self._rm_minus_r(Path(self.mock_inst_view_dir))
        self._rm_minus_r(Path(self.mock_web_dir))

    def _rm_minus_r(self, this_path: Path):
        for child in this_path.iterdir():
            if child.is_file() or child.is_symlink():
                child.unlink()
            else:
                self._rm_minus_r(child)
        this_path.rmdir()
