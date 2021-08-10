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

    TEST_TAB_WITH_VALIDATION_ERRORS = '**/validation_test_in_silico_data.tab'
    TEST_TAB_WITH_NO_ERRORS = '**/valid_in_silico_data.tab'
    TEST_TSV_WITH_VALIDATION_ERRORS = '**/validation_test_in_silico_data.tsv'
    TEST_TSV_WITH_NO_ERRORS = '**/valid_in_silico_data.tsv'
    TEST_TXT_WITH_VALIDATION_ERRORS = '**/validation_test_in_silico_data.txt'
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

    def __check_validation_errors(self, validation_errors: List[str]):
        """ Assert validation errors are correct """
        self.assertEqual(len(validation_errors), 47)

        self.assertTrue(
            '{row: 2, column: "Sample_id"}: "ZZZ;;{}{}{[[STUDY" contains illegal characters' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "cps_type"}: "@" contains illegal characters' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "ST"}: "ST=I" contains illegal characters' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "adhP"}: "abc" must be a whole positive number' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "pheS"}: "*" must be a whole positive number' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "atr"}: "0!" must be a whole positive number' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "glnA"}: "1_6" must be a whole positive number' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "sdhA"}: "2.2" must be a whole positive number' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "glcK"}: "NA" must be a whole positive number' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "tkt"}: "abc" must be a whole positive number' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "23S1"}: "[pos]" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "23S3"}: "*" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "ERMB"}: "_" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "ERMT"}: "0" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "FOSA"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "GYRA"}: "+" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "LNUB"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "LSAC"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "MEFA"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "MPHC"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "MSRA"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "MSRD"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "PARC"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "RPOBGBS-1"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "RPOBGBS-2"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "RPOBGBS-3"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "RPOBGBS-4"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "SUL2"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "TETB"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "TETL"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "TETM"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "TETO"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "TETS"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "ALP1"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "ALP23"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "ALPHA"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "HVGA"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "PI1"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "PI2A1"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "PI2A2"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "PI2B"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "RIB"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "SRR1"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "SRR2"}: "\'\'" must be pos, neg or NA' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "GYRA_variant"}: "\'\'" contains illegal characters' in validation_errors)
        self.assertTrue(
            '{row: 2, column: "PARC_variant"}: "\'\'" contains illegal characters' in validation_errors)

    def test_allowed_file_types(self):
        self.assertIsNotNone(self.under_test.allowed_file_types())
        self.assertEqual(sorted(self.under_test.allowed_file_types()), sorted(['tab','tsv','txt']))

    def test_is_valid_file_type(self):
        self.assertTrue(UploadHandler.is_valid_file_type(self.TEST_TAB_WITH_NO_ERRORS))
        self.assertTrue(UploadHandler.is_valid_file_type(self.TEST_TSV_WITH_NO_ERRORS))
        self.assertTrue(UploadHandler.is_valid_file_type(self.TEST_TXT_WITH_NO_ERRORS))
        self.assertFalse(UploadHandler.is_valid_file_type('foo'))
        self.assertFalse(UploadHandler.is_valid_file_type(None))
        self.assertFalse(UploadHandler.is_valid_file_type(''))

    def test_tab_load_with_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TAB_WITH_VALIDATION_ERRORS, recursive=True)[0])
        #self.display_errors('test_tab_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)

    def test_tab_load_with_no_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TAB_WITH_NO_ERRORS, recursive=True)[0])
        #self.display_errors('test_tab_load_with_no_validation_errors', validation_errors)
        self.assertEqual(len(validation_errors), 0)

    def test_tab_load_with_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TSV_WITH_VALIDATION_ERRORS, recursive=True)[0])
        #self.display_errors('test_tab_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)

    def test_tsv_load_with_no_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TSV_WITH_NO_ERRORS, recursive=True)[0])
        #self.display_errors('test_tsv_load_with_no_validation_errors', validation_errors)
        self.assertEqual(len(validation_errors), 0)

    def test_txt_load_with_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TXT_WITH_VALIDATION_ERRORS, recursive=True)[0])
        #self.display_errors('test_tab_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)

    def test_txt_load_with_no_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TXT_WITH_NO_ERRORS, recursive=True)[0])
        #self.display_errors('test_txt_load_with_no_validation_errors', validation_errors)
        self.assertEqual(len(validation_errors), 0)
