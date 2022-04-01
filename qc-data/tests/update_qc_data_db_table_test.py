import argparse
import json
import os
import urllib.request
from operator import itemgetter
from unittest import TestCase
from unittest.mock import patch

from bin.update_qc_data_db_table import (
    _find_files,
    _get_qc_data,
    _get_update_request_body,
    _make_request,
    data_sources_config,
    delete_qc_data_from_database,
    get_api_config,
    get_arguments,
    main,
    qc_data_file_name,
    update_database,
)

TEST_CONFIG = "tests/test_data_sources.yml"
TEST_CONFIG_BAD = "tests/test_data_sources_bad.yml"
# must mtach contents of TEST_CONFIG
TEST_API_CONFIG = {
    "base_url": "http://mock.metadata.api",
    "qc_data_upload": "/metadata/mock_upload_endpoint",
    "qc_data_delete_all": "/metadata/mock_delete_endpoint",
}
TEST_ENVIRONMENT = {"MONOCLE_PIPELINE_QC_DATA": "other/dir"}
TEST_DATA_DIR = "tests/update_qc_test_data"
# test lanes IDs must match names of subdirectories in TEST_DATA_DIR
TEST_LANE1_ID = "test_lane1"
TEST_LANE2_ID = "test_lane2"
# species, timestamps and rel abundance values must match contents of JSON files under TEST_DATA_DIR
TEST_SPECIES = "Streptococcus agalactiae"
TEST_TIMESTAMP1 = "2021-12-15 09:32:59"
TEST_TIMESTAMP2 = "2021-12-21 00:00:00"
TEST_REL_ABUN_SA1 = "97.65"
TEST_REL_ABUN_SA2 = "92.38"
TEST_TIMESTAMP1_EARLY = "2021-07-23 11:45:00"
TEST_REL_ABUN_SA1_EARLY = "37.52"
TEST_UPLOAD = [{"lane_id": TEST_LANE1_ID, "rel_abun_sa": float(TEST_REL_ABUN_SA1)}]
# Note this includes two values for TEST_SPECIES; the one with the latest timestamp should be returned,
# the other ignored.  The other species should be ignored.
TEST_LANE1_DATA = {
    "lane_id": TEST_LANE1_ID,
    "qc_data": {
        "rel_abundance": [
            {"species": TEST_SPECIES, "value": TEST_REL_ABUN_SA1_EARLY, "timestamp": TEST_TIMESTAMP1_EARLY},
            {"species": TEST_SPECIES, "value": TEST_REL_ABUN_SA1, "timestamp": TEST_TIMESTAMP1},
            {"species": "A species we're not interested in", "value": "12.34", "timestamp": "2021-11-03 17:51:10"},
        ]
    },
}
TEST_LANE1_DATA_BLANK = {
    "lane_id": TEST_LANE1_ID,
    "qc_data": {"rel_abundance": [{"species": TEST_SPECIES, "value": "", "timestamp": TEST_TIMESTAMP1}]},
}
TEST_LANE1_DATA_INVALID = {
    "lane_id": TEST_LANE1_ID,
    "qc_data": {"rel_abundance": [{"species": TEST_SPECIES, "value": "not a number", "timestamp": TEST_TIMESTAMP1}]},
}
TEST_LANE2_DATA = {
    "lane_id": TEST_LANE2_ID,
    "qc_data": {"rel_abundance": [{"species": TEST_SPECIES, "value": TEST_REL_ABUN_SA2, "timestamp": TEST_TIMESTAMP2}]},
}

# EXPECTED... vars are the return values we should get when the test succeeds
EXPECTED_LANE1_DATA = {
    "lane_id": TEST_LANE1_ID,
    "qc_data": {"rel_abundance": [{"species": TEST_SPECIES, "value": TEST_REL_ABUN_SA1, "timestamp": TEST_TIMESTAMP1}]},
}
EXPECTED_LANE2_DATA = {
    "lane_id": TEST_LANE2_ID,
    "qc_data": {"rel_abundance": [{"species": TEST_SPECIES, "value": TEST_REL_ABUN_SA2, "timestamp": TEST_TIMESTAMP2}]},
}
EXPECTED_REQUEST_BODY = [
    {"lane_id": TEST_LANE1_ID, "rel_abun_sa": float(TEST_REL_ABUN_SA1)},
    {"lane_id": TEST_LANE2_ID, "rel_abun_sa": float(TEST_REL_ABUN_SA2)},
]
EXPECTED_REQUEST_BODY_LANE1_BLANK = [
    {"lane_id": TEST_LANE1_ID},
    {"lane_id": TEST_LANE2_ID, "rel_abun_sa": float(TEST_REL_ABUN_SA2)},
]
EXPECTED_FILES = [
    os.path.join(TEST_DATA_DIR, TEST_LANE1_ID, qc_data_file_name),
    os.path.join(TEST_DATA_DIR, TEST_LANE2_ID, qc_data_file_name),
]


class UpdateQCDataDBTable(TestCase):
    def test_get_api_config(self):
        config = get_api_config(TEST_CONFIG)
        for expected_key in TEST_API_CONFIG:
            self.assertIn(expected_key, config)
            self.assertEqual(config.get(expected_key), TEST_API_CONFIG.get(expected_key))

    def test_get_api_config_reject_bad_config(self):
        with self.assertRaises(KeyError):
            get_api_config(TEST_CONFIG_BAD)

    @patch("urllib.request.Request")
    @patch("urllib.request.urlopen")
    def test_make_request_GET(self, mock_urlopen, mock_request):
        mock_request_url = TEST_API_CONFIG["base_url"] + TEST_API_CONFIG["qc_data_delete_all"]
        mock_urlopen.return_value = urllib.request.Request(mock_request_url)
        response = _make_request(mock_request_url)
        mock_request.assert_called_with(mock_request_url, data=None, headers={})

    @patch("urllib.request.Request")
    @patch("urllib.request.urlopen")
    def test_make_request_POST(self, mock_urlopen, mock_request):
        mock_request_url = TEST_API_CONFIG["base_url"] + TEST_API_CONFIG["qc_data_delete_all"]
        mock_urlopen.return_value = urllib.request.Request(mock_request_url)
        response = _make_request(mock_request_url, post_data=TEST_UPLOAD)
        mock_request.assert_called_with(
            mock_request_url,
            data=str(json.dumps(TEST_UPLOAD)).encode("utf-8"),
            headers={"Content-type": "application/json;charset=utf-8"},
        )

    def test_find_files(self):
        files_found = _find_files(qc_data_file_name, TEST_DATA_DIR)
        # order of arrays doesn't matter
        self.assertEqual(sorted(files_found), sorted(EXPECTED_FILES))

    @patch("bin.update_qc_data_db_table._find_files")
    def test_get_qc_data(self, mock_find_files):
        mock_find_files.return_value = EXPECTED_FILES
        qc_data = _get_qc_data(TEST_DATA_DIR)
        expected = [EXPECTED_LANE2_DATA, EXPECTED_LANE1_DATA]
        # order of arrays doesn't matter
        self.assertEqual(sorted(qc_data, key=itemgetter("lane_id")), sorted(expected, key=itemgetter("lane_id")))

    @patch("bin.update_qc_data_db_table._get_qc_data")
    def test_get_update_request_body(self, mock_get_qc_data):
        mock_get_qc_data.return_value = [TEST_LANE1_DATA, TEST_LANE2_DATA]
        request_body = _get_update_request_body(TEST_DATA_DIR)
        self.assertEqual(request_body, EXPECTED_REQUEST_BODY)

    @patch("bin.update_qc_data_db_table._get_qc_data")
    def test_get_update_request_body_lane_with_missing_rel_abun(self, mock_get_qc_data):
        mock_get_qc_data.return_value = [TEST_LANE1_DATA_BLANK, EXPECTED_LANE2_DATA]
        request_body = _get_update_request_body(TEST_DATA_DIR)
        self.assertEqual(request_body, EXPECTED_REQUEST_BODY_LANE1_BLANK)

    @patch("bin.update_qc_data_db_table._get_qc_data")
    def test_get_update_request_body_lane_with_invalid_rel_abun(self, mock_get_qc_data):
        mock_get_qc_data.return_value = [TEST_LANE1_DATA_INVALID, EXPECTED_LANE2_DATA]
        with self.assertRaises(ValueError):
            _get_update_request_body(TEST_DATA_DIR)

    @patch("bin.update_qc_data_db_table._get_update_request_body")
    @patch("bin.update_qc_data_db_table._make_request")
    def test_update_database(self, mock_make_request, mock_get_update_request_body):
        mock_get_update_request_body.return_value = TEST_UPLOAD
        update_database(TEST_DATA_DIR, TEST_API_CONFIG)
        mock_make_request.assert_called_once_with(
            TEST_API_CONFIG["base_url"] + TEST_API_CONFIG["qc_data_upload"], post_data=TEST_UPLOAD
        )

    @patch("bin.update_qc_data_db_table._make_request")
    def test_delete_qc_data_from_database(self, mock_make_request):
        delete_qc_data_from_database(TEST_API_CONFIG)
        mock_make_request.assert_called_once_with(TEST_API_CONFIG["base_url"] + TEST_API_CONFIG["qc_data_delete_all"])

    def test_get_arguments(self):
        actual = get_arguments().parse_args(["--pipeline_qc_dir", "qc_data_root_directory", "--log_level", "INFO"])
        self.assertEqual(actual, argparse.Namespace(pipeline_qc_dir="qc_data_root_directory", log_level="INFO"))

    def test_get_arguments_short(self):
        actual = get_arguments().parse_args(["-D", "qc_data_root_directory", "-L", "DEBUG"])
        self.assertEqual(actual, argparse.Namespace(pipeline_qc_dir="qc_data_root_directory", log_level="DEBUG"))

    @patch.dict(os.environ, TEST_ENVIRONMENT, clear=True)
    def test_get_arguments_using_environ(self):
        actual = get_arguments().parse_args(["--log_level", "ERROR"])
        self.assertEqual(actual, argparse.Namespace(pipeline_qc_dir="other/dir", log_level="ERROR"))

    def test_get_arguments_default(self):
        actual = get_arguments().parse_args([])
        self.assertEqual(actual, argparse.Namespace(pipeline_qc_dir="/app/monocle_pipeline_qc", log_level="WARNING"))

    @patch("bin.update_qc_data_db_table.get_arguments")
    @patch("bin.update_qc_data_db_table.get_api_config")
    @patch("bin.update_qc_data_db_table.delete_qc_data_from_database")
    @patch("bin.update_qc_data_db_table.update_database")
    def test_main(
        self, mock_update_database, mock_delete_qc_data_from_database, mock_get_api_config, mock_get_arguments
    ):

        args = mock_get_arguments.return_value.parse_args()
        args.pipeline_qc_dir = TEST_DATA_DIR
        args.log_level = "WARNING"
        mock_get_api_config.return_value = TEST_API_CONFIG

        main()

        mock_get_api_config.assert_called_once()
        mock_delete_qc_data_from_database.assert_called_once_with(TEST_API_CONFIG)
        mock_update_database.assert_called_once_with(TEST_DATA_DIR, TEST_API_CONFIG)
