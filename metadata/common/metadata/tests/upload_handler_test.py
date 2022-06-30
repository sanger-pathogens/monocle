import glob
import json
import unittest
from typing import List
from unittest.mock import patch

from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition
from metadata.api.upload_handlers import UploadInSilicoHandler, UploadMetadataHandler
from metadata.tests.test_data import (
    EXPECTED_VALIDATION_ERRORS,
    EXPECTED_VALIDATION_ERRORS2,
    TEST_UPLOAD_SAMPLE_1,
    TEST_UPLOAD_SAMPLE_2,
    TEST_UPLOAD_SAMPLE_3,
    TEST_UPLOAD_SAMPLE_4,
    TEST_UPLOAD_SAMPLE_5,
)

RESPONSE_STRING_INSTITUTIONS = b'{"institutions": {"TesInsA": {"inst_name": "Test Institution A", "country_names": ["TestCountryA", "TestCountryB"]}}}'


class TestUploadHandler(unittest.TestCase):
    """Unit tests for the UploadHandler class"""

    TEST_CSV_SPREADSHEET_WITH_VALIDATION_ERRORS = "**/validation_test_spreadsheet.csv"
    TEST_CSV_SPREADSHEET_WITH_NO_ERRORS = "**/valid_spreadsheet.csv"
    TEST_TSV_SPREADSHEET_WITH_VALIDATION_ERRORS = "**/validation_test_spreadsheet.tsv"
    TEST_TSV_SPREADSHEET_WITH_NO_ERRORS = "**/valid_spreadsheet.tsv"
    TEST_TXT_SPREADSHEET_WITH_VALIDATION_ERRORS = "**/validation_test_spreadsheet.txt"
    TEST_TXT_SPREADSHEET_WITH_NO_ERRORS = "**/valid_spreadsheet.txt"
    TEST_NO_EXTENSION_WITH_VALIDATION_ERRORS = "**/validation_test_spreadsheet"
    TEST_NO_EXTENSION_SPREADSHEET_WITH_NO_ERRORS = "**/valid_spreadsheet"
    CONFIG_FILE_PATH = "config.json"

    def display_errors(self, test_method, errors: List[str]) -> None:
        print("{} errors:".format(test_method))
        for error in errors:
            print(str(error))

    def setUp(self) -> None:
        from metadata.wsgi import application

        self.maxDiff = None
        with patch("metadata.api.database.monocle_database_service.MonocleDatabaseService", autospec=True) as dao_mock:
            self.dao_mock = dao_mock

        # Read in the spreadsheet field definitions
        with open(self.CONFIG_FILE_PATH, "r") as app_config_file:
            data = app_config_file.read()
        self.config = json.loads(data)
        self.test_spreadsheet_def = SpreadsheetDefinition(
            self.config["metadata"]["spreadsheet_header_row_position"],
            self.config["metadata"]["spreadsheet_definition"],
        )

        self.under_test = UploadMetadataHandler(self.dao_mock, self.test_spreadsheet_def, True)
        self.under_test.application = application
        self.under_test.application.config = self.config

    def __check_validation_errors(self, validation_errors: List[str]):
        """Assert validation errors are correct"""
        self.assertEqual(len(validation_errors), 65)

        for expected in EXPECTED_VALIDATION_ERRORS:
            self.assertIn(expected, validation_errors)

    def test_allowed_file_types(self):
        self.assertIsNotNone(self.under_test.allowed_file_types())
        self.assertEqual(sorted(self.under_test.allowed_file_types()), sorted(["tab", "tsv", "txt"]))

    def test_is_valid_file_type(self):
        # check that file names are checked when file extension check is enabled
        previous_check_file_extension_value = self.under_test.check_file_extension
        self.under_test.check_file_extension = False
        self.assertTrue(self.under_test.is_valid_file_type(self.TEST_CSV_SPREADSHEET_WITH_NO_ERRORS))
        self.assertTrue(self.under_test.is_valid_file_type("foo"))
        self.assertTrue(self.under_test.is_valid_file_type(None))
        self.assertTrue(self.under_test.is_valid_file_type(""))
        self.under_test.check_file_extension = previous_check_file_extension_value

    def test_file_type_check_disabled_ok(self):
        # check that files without extensions are accepted if the file extention check is disabled
        previous_check_file_extension_value = self.under_test.check_file_extension
        self.under_test.check_file_extension = False
        self.assertTrue(self.under_test.is_valid_file_type(self.TEST_NO_EXTENSION_SPREADSHEET_WITH_NO_ERRORS))
        self.under_test.check_file_extension = previous_check_file_extension_value

    @patch("metadata.lib.upload_handler.urlopen")
    def test_csv_load_with_validation_errors(self, urlopen_mock) -> None:
        urlopen_mock.return_value.__enter__.return_value.read.return_value = RESPONSE_STRING_INSTITUTIONS
        previous_check_file_extension_value = self.under_test.check_file_extension
        previous_file_delimiter = self.under_test.file_delimiter
        self.under_test.check_file_extension = False
        self.under_test.file_delimiter = ","

        validation_errors = self.under_test.load(
            glob.glob(self.TEST_CSV_SPREADSHEET_WITH_VALIDATION_ERRORS, recursive=True)[0]
        )
        self.under_test.check_file_extension = previous_check_file_extension_value
        self.under_test.file_delimiter = previous_file_delimiter

        # self.display_errors('test_csv_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)

    @patch("metadata.lib.upload_handler.urlopen")
    def test_tsv_load_with_validation_errors(self, urlopen_mock) -> None:
        urlopen_mock.return_value.__enter__.return_value.read.return_value = RESPONSE_STRING_INSTITUTIONS

        validation_errors = self.under_test.load(
            glob.glob(self.TEST_TSV_SPREADSHEET_WITH_VALIDATION_ERRORS, recursive=True)[0]
        )

        # self.display_errors('test_tsv_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)

    @patch("metadata.lib.upload_handler.urlopen")
    def test_txt_load_with_validation_errors(self, urlopen_mock) -> None:
        urlopen_mock.return_value.__enter__.return_value.read.return_value = RESPONSE_STRING_INSTITUTIONS

        validation_errors = self.under_test.load(
            glob.glob(self.TEST_TXT_SPREADSHEET_WITH_VALIDATION_ERRORS, recursive=True)[0]
        )

        # self.display_errors('test_txt_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)

    @patch("metadata.lib.upload_handler.urlopen")
    def test_no_extension_load_with_validation_errors(self, urlopen_mock) -> None:
        urlopen_mock.return_value.__enter__.return_value.read.return_value = RESPONSE_STRING_INSTITUTIONS
        previous_check_file_extension_value = self.under_test.check_file_extension
        previous_file_delimiter = self.under_test.file_delimiter
        self.under_test.check_file_extension = False
        self.under_test.file_delimiter = ","

        validation_errors = self.under_test.load(
            glob.glob(self.TEST_NO_EXTENSION_WITH_VALIDATION_ERRORS, recursive=True)[0]
        )
        self.under_test.check_file_extension = previous_check_file_extension_value
        self.under_test.file_delimiter = previous_file_delimiter

        # self.display_errors('test_no_extension_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)

    @patch("metadata.lib.upload_handler.urlopen")
    def test_csv_load_with_no_validation_errors(self, urlopen_mock) -> None:
        urlopen_mock.return_value.__enter__.return_value.read.return_value = RESPONSE_STRING_INSTITUTIONS
        previous_check_file_extension_value = self.under_test.check_file_extension
        previous_file_delimiter = self.under_test.file_delimiter
        self.under_test.check_file_extension = False
        self.under_test.file_delimiter = ","

        validation_errors = self.under_test.load(
            glob.glob(self.TEST_NO_EXTENSION_SPREADSHEET_WITH_NO_ERRORS, recursive=True)[0]
        )
        self.under_test.check_file_extension = previous_check_file_extension_value
        self.under_test.file_delimiter = previous_file_delimiter

        # self.display_errors('test_csv_load_with_no_validation_errors', validation_errors)
        self.assertEqual(len(validation_errors), 0)

    @patch("metadata.lib.upload_handler.urlopen")
    def test_tsv_load_with_no_validation_errors(self, urlopen_mock) -> None:
        urlopen_mock.return_value.__enter__.return_value.read.return_value = RESPONSE_STRING_INSTITUTIONS

        validation_errors = self.under_test.load(glob.glob(self.TEST_TSV_SPREADSHEET_WITH_NO_ERRORS, recursive=True)[0])

        # self.display_errors('test_load_with_no_validation_errors', validation_errors)
        self.assertEqual(len(validation_errors), 0)

    @patch("metadata.lib.upload_handler.urlopen")
    def test_txt_load_with_no_validation_errors(self, urlopen_mock) -> None:
        urlopen_mock.return_value.__enter__.return_value.read.return_value = RESPONSE_STRING_INSTITUTIONS

        validation_errors = self.under_test.load(glob.glob(self.TEST_TXT_SPREADSHEET_WITH_NO_ERRORS, recursive=True)[0])
        # self.display_errors("test_txt_load_with_no_validation_errors", validation_errors)

        self.assertEqual(len(validation_errors), 0)

    @patch("metadata.lib.upload_handler.urlopen")
    def test_no_extension_load_with_no_validation_errors(self, urlopen_mock) -> None:
        urlopen_mock.return_value.__enter__.return_value.read.return_value = RESPONSE_STRING_INSTITUTIONS
        previous_check_file_extension_value = self.under_test.check_file_extension
        previous_file_delimiter = self.under_test.file_delimiter
        self.under_test.check_file_extension = False
        self.under_test.file_delimiter = ","

        validation_errors = self.under_test.load(
            glob.glob(self.TEST_CSV_SPREADSHEET_WITH_VALIDATION_ERRORS, recursive=True)[0]
        )
        self.under_test.check_file_extension = previous_check_file_extension_value
        self.under_test.file_delimiter = previous_file_delimiter

        # self.display_errors('test_no_extension_load_with_no_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)

    @patch("metadata.lib.upload_handler.urlopen")
    def test_parse_metadata(self, urlopen_mock) -> None:
        urlopen_mock.return_value.__enter__.return_value.read.return_value = RESPONSE_STRING_INSTITUTIONS
        previous_check_file_extension_value = self.under_test.check_file_extension
        previous_file_delimiter = self.under_test.file_delimiter
        self.under_test.check_file_extension = False
        self.under_test.file_delimiter = ","

        validation_errors = self.under_test.load(glob.glob(self.TEST_CSV_SPREADSHEET_WITH_NO_ERRORS, recursive=True)[0])
        # self.display_errors('test_parse', validation_errors)

        self.assertEqual(len(validation_errors), 0)

        expected_results = [
            TEST_UPLOAD_SAMPLE_1,
            TEST_UPLOAD_SAMPLE_2,
            TEST_UPLOAD_SAMPLE_3,
            TEST_UPLOAD_SAMPLE_4,
            TEST_UPLOAD_SAMPLE_5,
        ]

        samples = self.under_test.parse()
        self.under_test.check_file_extension = previous_check_file_extension_value
        self.under_test.file_delimiter = previous_file_delimiter
        self.assertEqual(len(samples), len(expected_results))

        for idx in range(0, len(expected_results) - 1):
            # print(samples[idx])
            self.assertEqual(samples[idx], expected_results[idx])

    def test_store_metadata_nothing_loaded(self) -> None:
        with self.assertRaises(RuntimeError):
            self.under_test.store()

    @patch("metadata.lib.upload_handler.urlopen")
    def test_store_metadata(self, urlopen_mock) -> None:
        urlopen_mock.return_value.__enter__.return_value.read.return_value = RESPONSE_STRING_INSTITUTIONS
        previous_check_file_extension_value = self.under_test.check_file_extension
        previous_file_delimiter = self.under_test.file_delimiter
        self.under_test.check_file_extension = False
        self.under_test.file_delimiter = ","
        self.under_test.load(glob.glob(self.TEST_CSV_SPREADSHEET_WITH_NO_ERRORS, recursive=True)[0])

        self.under_test.store()

        self.dao_mock.update_sample_metadata.assert_called_once()
        self.under_test.check_file_extension = previous_check_file_extension_value
        self.under_test.file_delimiter = previous_file_delimiter


class TestInSilicoUploadHandler(unittest.TestCase):
    """Unit tests for the UploadHandler class"""

    TEST_TXT_WITH_VALIDATION_ERRORS = "**/validation_test_in_silico_data.txt"
    TEST_TXT_WITH_NO_ERRORS = "**/valid_in_silico_data.txt"
    CONFIG_FILE_PATH = "config.json"

    def display_errors(self, test_method, errors: List[str]) -> None:
        print("{} errors:".format(test_method))
        for error in errors:
            print(str(error))

    def setUp(self) -> None:
        self.maxDiff = None
        with patch("metadata.api.database.monocle_database_service.MonocleDatabaseService", autospec=True) as dao_mock:
            self.dao_mock = dao_mock

        # Read in the spreadsheet field definitions
        with open(self.CONFIG_FILE_PATH, "r") as app_config_file:
            data = app_config_file.read()
        self.config = json.loads(data)
        self.test_spreadsheet_def = SpreadsheetDefinition(
            self.config["in_silico_data"]["spreadsheet_header_row_position"],
            self.config["in_silico_data"]["spreadsheet_definition"],
        )

        self.under_test = UploadInSilicoHandler(self.dao_mock, self.test_spreadsheet_def, True)

    def __check_validation_errors(self, validation_errors: List[str]):
        """Assert validation errors are correct"""
        self.assertEqual(len(validation_errors), 37)

        for expected in EXPECTED_VALIDATION_ERRORS2:
            self.assertIn(expected, validation_errors)

    def test_allowed_file_types(self):
        self.assertIsNotNone(self.under_test.allowed_file_types())
        self.assertEqual(sorted(self.under_test.allowed_file_types()), sorted(["tab", "tsv", "txt"]))

    def test_is_valid_file_type(self):
        # check that file names are checked when file extension check is enabled
        previous_check_file_extension_value = self.under_test.check_file_extension
        self.under_test.check_file_extension = True
        self.assertTrue(self.under_test.is_valid_file_type(self.TEST_TXT_WITH_NO_ERRORS))
        self.assertFalse(self.under_test.is_valid_file_type("foo"))
        self.assertFalse(self.under_test.is_valid_file_type(None))
        self.assertFalse(self.under_test.is_valid_file_type(""))
        self.under_test.check_file_extension = previous_check_file_extension_value

    @patch("metadata.lib.upload_handler.urlopen")
    def test_txt_load_with_no_validation_errors(self, urlopen_mock) -> None:
        urlopen_mock.return_value.__enter__.return_value.read.return_value = RESPONSE_STRING_INSTITUTIONS

        validation_errors = self.under_test.load(glob.glob(self.TEST_TXT_WITH_NO_ERRORS, recursive=True)[0])

        # self.display_errors('test_txt_load_with_no_validation_errors', validation_errors)
        self.assertEqual(len(validation_errors), 0)

    @patch("metadata.lib.upload_handler.urlopen")
    def test_txt_load_with_validation_errors(self, urlopen_mock) -> None:
        urlopen_mock.return_value.__enter__.return_value.read.return_value = RESPONSE_STRING_INSTITUTIONS

        validation_errors = self.under_test.load(glob.glob(self.TEST_TXT_WITH_VALIDATION_ERRORS, recursive=True)[0])

        # self.display_errors('test_txt_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)
