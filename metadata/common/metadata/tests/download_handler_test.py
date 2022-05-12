import json
import unittest
from unittest.mock import Mock, patch

from metadata.api.download_handlers import DownloadInSilicoHandler, DownloadMetadataHandler, DownloadQCDataHandler
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition
from metadata.tests.test_data import (
    TEST_LANE_IN_SILICO_1,
    TEST_LANE_IN_SILICO_1_DICT,
    TEST_LANE_IN_SILICO_2,
    TEST_LANE_IN_SILICO_2_DICT,
    TEST_LANE_QC_DATA_1,
    TEST_LANE_QC_DATA_1_DICT,
    TEST_LANE_QC_DATA_2,
    TEST_LANE_QC_DATA_2_DICT,
    TEST_SAMPLE_1,
    TEST_SAMPLE_1_DICT,
    TEST_SAMPLE_2,
    TEST_SAMPLE_2_DICT,
)


class TestDownloadMetadataHandler(unittest.TestCase):
    """Unit tests for the DownloadMetadataHandler class"""

    CONFIG_FILE = "config.json"

    def setUp(self) -> None:
        fields = {
            "column_1": {"title": "COLUMN_1_NAME"},
            "column_2": {"title": "COLUMN_2_NAME"},
            "column_3": {"title": "COLUMN_3_NAME"},
        }

        with patch("metadata.api.database.monocle_database_service.MonocleDatabaseService", autospec=True) as dao_mock:
            self.dao_mock = dao_mock
            self.test_spreadsheet_def = SpreadsheetDefinition(5, fields)
            self.under_test = DownloadMetadataHandler(self.dao_mock, self.test_spreadsheet_def)

    def test_append_to_dict(self) -> None:
        results = {}
        self.under_test._append_to_dict(results, "column_1", "test_value1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results["column_1"], {"order": 1, "title": "COLUMN_1_NAME", "value": "test_value1"})

        self.under_test._append_to_dict(results, "column_2", "test_value2")
        self.assertEqual(len(results), 2)
        self.assertEqual(results["column_2"], {"order": 2, "title": "COLUMN_2_NAME", "value": "test_value2"})

    def test_append_to_dict_novalue(self) -> None:
        results = {}
        self.under_test._append_to_dict(results, "column_1", None)

        self.assertEqual(len(results), 1)
        self.assertEqual(results["column_1"], {"order": 1, "title": "COLUMN_1_NAME", "value": None})

    def test_append_to_dict_novalue_null_to_empty_string(self) -> None:
        results = {}

        # temporarily set replace_null_with_empty_string flag to True whilst calling _append_to_dict()
        original_value = self.under_test.replace_null_with_empty_string
        self.under_test.replace_null_with_empty_string = True
        self.under_test._append_to_dict(results, "column_1", None)
        self.under_test.replace_null_with_empty_string = original_value

        self.assertEqual(len(results), 1)
        self.assertEqual(results["column_1"], {"order": 1, "title": "COLUMN_1_NAME", "value": ""})

    def test_read_download_metadata(self) -> None:
        keys = ["key1", "key2"]
        mock_retval = [Mock(), Mock()]
        self.dao_mock.get_download_metadata.return_value = mock_retval
        metadata_list = self.under_test.read_download_metadata(keys)
        self.dao_mock.get_download_metadata.assert_called_once_with(keys)
        self.assertEqual(metadata_list, mock_retval)

    def test_create_download_response(self) -> None:
        from metadata.wsgi import application

        value_field_name = "value"
        with open(self.CONFIG_FILE) as cfg:
            data = json.load(cfg)
            sprd_def = SpreadsheetDefinition(2, data["metadata"]["spreadsheet_definition"])
            handler = DownloadMetadataHandler(self.dao_mock, sprd_def)
            handler.application = application
            handler.application.config = data
            results = handler.create_download_response([TEST_SAMPLE_1, TEST_SAMPLE_2])
            self.assertIsNotNone(results)
            self.assertEqual(len(results), 2)
            # Sample 1
            for (k, v) in TEST_SAMPLE_1_DICT.items():
                self.assertEqual(results[0][k][value_field_name], v)
            # Sample 2
            for (k, v) in TEST_SAMPLE_2_DICT.items():
                self.assertEqual(results[1][k][value_field_name], v)


class TestDownloadInSilicoHandler(unittest.TestCase):
    """Unit tests for the DownloadInSilicoHandler class"""

    CONFIG_FILE = "config.json"

    def setUp(self) -> None:
        fields = {
            "column_1": {"title": "COLUMN_1_NAME"},
            "column_2": {"title": "COLUMN_2_NAME"},
            "column_3": {"title": "COLUMN_3_NAME"},
        }

        with patch("metadata.api.database.monocle_database_service.MonocleDatabaseService", autospec=True) as dao_mock:
            self.dao_mock = dao_mock
            self.test_spreadsheet_def = SpreadsheetDefinition(5, fields)
            self.under_test = DownloadInSilicoHandler(self.dao_mock, self.test_spreadsheet_def)

    def test_append_to_dict(self) -> None:
        results = {}
        self.under_test._append_to_dict(results, "column_1", "test_value1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results["column_1"], {"order": 1, "title": "COLUMN_1_NAME", "value": "test_value1"})

        self.under_test._append_to_dict(results, "column_2", "test_value2")
        self.assertEqual(len(results), 2)
        self.assertEqual(results["column_2"], {"order": 2, "title": "COLUMN_2_NAME", "value": "test_value2"})

    def test_append_to_dict_novalue(self) -> None:
        results = {}
        self.under_test._append_to_dict(results, "column_1", None)

        self.assertEqual(len(results), 1)
        self.assertEqual(results["column_1"], {"order": 1, "title": "COLUMN_1_NAME", "value": None})

    def test_append_to_dict_novalue_null_to_empty_string(self) -> None:
        results = {}

        # temporarily set replace_null_with_empty_string flag to True whilst calling _append_to_dict()
        original_value = self.under_test.replace_null_with_empty_string
        self.under_test.replace_null_with_empty_string = True
        self.under_test._append_to_dict(results, "column_1", None)
        self.under_test.replace_null_with_empty_string = original_value

        self.assertEqual(len(results), 1)
        self.assertEqual(results["column_1"], {"order": 1, "title": "COLUMN_1_NAME", "value": ""})

    def test_read_download_in_silico_data(self) -> None:
        keys = ["key1", "key2"]
        mock_retval = [Mock(), Mock()]
        self.dao_mock.get_download_in_silico_data.return_value = mock_retval
        in_silico_data_list = self.under_test.read_download_in_silico_data(keys)
        self.dao_mock.get_download_in_silico_data.assert_called_once_with(keys)
        self.assertEqual(in_silico_data_list, mock_retval)

    def test_create_download_response(self) -> None:
        from metadata.wsgi import application

        value_field_name = "value"
        with open(self.CONFIG_FILE) as cfg:
            data = json.load(cfg)
            sprd_def = SpreadsheetDefinition(2, data["in_silico_data"]["spreadsheet_definition"])
            handler = DownloadInSilicoHandler(self.dao_mock, sprd_def)
            handler.application = application
            handler.application.config = data
            results = handler.create_download_response([TEST_LANE_IN_SILICO_1, TEST_LANE_IN_SILICO_2])
            self.assertIsNotNone(results)
            self.assertEqual(len(results), 2)
            # Sample 1
            for (k, v) in TEST_LANE_IN_SILICO_1_DICT.items():
                self.assertEqual(results[0][k][value_field_name], v)
            # Sample 2
            for (k, v) in TEST_LANE_IN_SILICO_2_DICT.items():
                self.assertEqual(results[1][k][value_field_name], v)


class TestDownloadQCHandler(unittest.TestCase):
    """Unit tests for the DownloadQCDataHandler class"""

    CONFIG_FILE = "config.json"

    def setUp(self) -> None:
        fields = {
            "column_1": {"title": "COLUMN_1_NAME"},
            "column_2": {"title": "COLUMN_2_NAME"},
            "column_3": {"title": "COLUMN_3_NAME"},
        }

        with patch("metadata.api.database.monocle_database_service.MonocleDatabaseService", autospec=True) as dao_mock:
            self.dao_mock = dao_mock
            self.test_spreadsheet_def = SpreadsheetDefinition(5, fields)
            self.under_test = DownloadQCDataHandler(self.dao_mock, self.test_spreadsheet_def)

    def test_append_to_dict(self) -> None:
        results = {}
        self.under_test._append_to_dict(results, "column_1", "test_value1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results["column_1"], {"order": 1, "title": "COLUMN_1_NAME", "value": "test_value1"})

        self.under_test._append_to_dict(results, "column_2", "test_value2")
        self.assertEqual(len(results), 2)
        self.assertEqual(results["column_2"], {"order": 2, "title": "COLUMN_2_NAME", "value": "test_value2"})

    def test_append_to_dict_novalue(self) -> None:
        results = {}
        self.under_test._append_to_dict(results, "column_1", None)

        self.assertEqual(len(results), 1)
        self.assertEqual(results["column_1"], {"order": 1, "title": "COLUMN_1_NAME", "value": None})

    def test_append_to_dict_novalue_null_to_empty_string(self) -> None:
        results = {}

        # temporarily set replace_null_with_empty_string flag to True whilst calling _append_to_dict()
        original_value = self.under_test.replace_null_with_empty_string
        self.under_test.replace_null_with_empty_string = True
        self.under_test._append_to_dict(results, "column_1", None)
        self.under_test.replace_null_with_empty_string = original_value

        self.assertEqual(len(results), 1)
        self.assertEqual(results["column_1"], {"order": 1, "title": "COLUMN_1_NAME", "value": ""})

    def test_read_download_in_silico_data(self) -> None:
        keys = ["key1", "key2"]
        mock_retval = [Mock(), Mock()]
        self.dao_mock.get_download_qc_data.return_value = mock_retval
        qc_data_list = self.under_test.read_download_qc_data(keys)
        self.dao_mock.get_download_qc_data.assert_called_once_with(keys)
        self.assertEqual(qc_data_list, mock_retval)

    def test_create_download_response(self) -> None:
        from metadata.wsgi import application

        value_field_name = "value"
        with open(self.CONFIG_FILE) as cfg:
            data = json.load(cfg)
            sprd_def = SpreadsheetDefinition(2, data["qc_data"]["spreadsheet_definition"])
            handler = DownloadQCDataHandler(self.dao_mock, sprd_def)
            handler.application = application
            handler.application.config = data
            results = handler.create_download_response([TEST_LANE_QC_DATA_1, TEST_LANE_QC_DATA_2])
            self.assertIsNotNone(results)
            self.assertEqual(len(results), 2)
            # Sample 1
            for (k, v) in TEST_LANE_QC_DATA_1_DICT.items():
                self.assertEqual(results[0][k][value_field_name], v)
            # Sample 2
            for (k, v) in TEST_LANE_QC_DATA_2_DICT.items():
                self.assertEqual(results[1][k][value_field_name], v)
