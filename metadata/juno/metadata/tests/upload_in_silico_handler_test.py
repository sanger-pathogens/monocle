import unittest
from unittest.mock import patch
import json
import glob
from typing import List
from metadata.api.upload_in_silico_handler import UploadHandler
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition
from metadata.api.model.institution import Institution
from metadata.api.model.metadata import Metadata


class TestInSilicoUploadHandler(unittest.TestCase):
    """ Unit tests for the UploadHandler class """

    TEST_TXT_WITH_NO_ERRORS = '**/valid_in_silico_data.txt'
    CONFIG_FILE_PATH = 'in_silico_data_config.json'

    def display_errors(self, test_method, errors: List[str]) -> None:
        print('{} errors:'.format(test_method))
        for error in errors:
            print(str(error))

    def setUp(self) -> None:
        self.maxDiff = None
        with patch('metadata.api.database.monocle_database_service.MonocleDatabaseService', autospec=True) as dao_mock:
            self.dao_mock = dao_mock
            self.dao_mock.get_institutions.return_value = [
                Institution('Test Institution A', 'TestCountryA', 0, 0),
                Institution('Test Institution B', 'TestCountryB', 0, 0)
            ]

            # Read in the spreadsheet field definitions
            with open(self.CONFIG_FILE_PATH, 'r') as app_config_file:
                data = app_config_file.read()
                self.config = json.loads(data)
                self.test_spreadsheet_def = SpreadsheetDefinition(
                    self.config['spreadsheet_header_row_position'], self.config['spreadsheet_definition'])

            self.under_test = UploadHandler(self.dao_mock, self.test_spreadsheet_def, True)

    def test_allowed_file_types(self):
        self.assertIsNotNone(self.under_test.allowed_file_types())
        self.assertEqual(sorted(self.under_test.allowed_file_types()), sorted(['tab','tsv','txt']))
