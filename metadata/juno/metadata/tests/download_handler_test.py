import unittest
import json
from unittest.mock import patch, Mock
from metadata.tests.test_data import *
from metadata.api.download_handler import DownloadHandler
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition


class TestDownloadHandler(unittest.TestCase):
    """ Unit tests for the DownloadHandler class """

    def setUp(self) -> None:
        fields = {
            "column_1": {
                "title": "COLUMN_1_NAME"
            },
            "column_2": {
                "title": "COLUMN_2_NAME"
            },
            "column_3": {
                "title": "COLUMN_3_NAME"
            }
        }

        with patch('metadata.api.database.monocle_database_service.MonocleDatabaseService', autospec=True) as dao_mock:
            self.dao_mock = dao_mock
            self.test_spreadsheet_def = SpreadsheetDefinition(5, fields)
            self.under_test = DownloadHandler(self.dao_mock, self.test_spreadsheet_def)

    def test_append_to_dict(self) -> None:
        results = {}
        self.under_test._append_to_dict(results, 'column_1', 'test_value1')
        self.assertEqual(len(results), 1)
        self.assertEqual(
            results['column_1'],
            {
                'order': 1,
                'name': 'COLUMN_1_NAME',
                'value': 'test_value1'
            }
        )

        self.under_test._append_to_dict(results, 'column_2', 'test_value2')
        self.assertEqual(len(results), 2)
        self.assertEqual(
            results['column_2'],
            {
                'order': 2,
                'name': 'COLUMN_2_NAME',
                'value': 'test_value2'
            }
        )

    def test_append_to_dict_novalue(self) -> None:
        results = {}
        self.under_test._append_to_dict(results, 'column_1', None)

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results['column_1'],
            {
                'order': 1,
                'name': 'COLUMN_1_NAME',
                'value': ''
            }
        )

    def test_read_download_metadata(self) -> None:
        keys = ['key1', 'key2']
        mock_retval = [Mock(), Mock()]
        self.dao_mock.get_download_metadata.return_value = mock_retval
        metadata_list = self.under_test.read_download_metadata(keys)
        self.dao_mock.get_download_metadata.assert_called_once_with(keys)
        self.assertEqual(metadata_list, mock_retval)

    def test_create_download_response(self) -> None:
        with open('config.json') as cfg:
            data = json.load(cfg)
            sprd_def = SpreadsheetDefinition(2, data['spreadsheet_definition'])
            handler = DownloadHandler(self.dao_mock, sprd_def)
            results = handler.create_download_response([TEST_SAMPLE_1, TEST_SAMPLE_2])
            self.assertIsNotNone(results)
            self.assertEqual(len(results), 2)
            #
            # TODO Assert all field values
            #
