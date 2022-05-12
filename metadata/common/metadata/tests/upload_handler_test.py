import glob
import json
import unittest
from typing import List
from unittest.mock import patch

from metadata.api.model.institution import Institution
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition
from metadata.api.upload_handlers import UploadInSilicoHandler, UploadMetadataHandler
from metadata.tests.test_data import (
    TEST_UPLOAD_SAMPLE_1,
    TEST_UPLOAD_SAMPLE_2,
    TEST_UPLOAD_SAMPLE_3,
    TEST_UPLOAD_SAMPLE_4,
    TEST_UPLOAD_SAMPLE_5,
)


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
            self.dao_mock.get_institutions.return_value = [
                Institution("Test Institution A", "TestCountryA"),
                Institution("Test Institution B", "TestCountryB"),
            ]
            self.dao_mock.get_authenticated_username.return_value = "mock_user"

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

        self.assertTrue(
            '{row: 4, column: "Sanger_Sample_ID"}: "ZZZ;;{}{}{[[STUDY" contains illegal characters' in validation_errors
        )
        self.assertTrue(
            '{row: 5, column: "Supplier_Sample_Name"}: "%%%%%@qwe" contains illegal characters' in validation_errors
        )
        self.assertTrue(
            '{row: 7, column: "Supplier_Sample_Name"}: "EY 70603" contains illegal characters' in validation_errors
        )
        self.assertTrue('{row: 8, column: "Public_Name"}: "^&*%RTYUT" contains illegal characters' in validation_errors)
        self.assertTrue(
            '{row: 10, column: "Lane_ID"}: "ABCDE_2#FGI" is not a recognised lane Id format' in validation_errors
        )
        self.assertTrue('{row: 11, column: "Lane_ID"}: "ABCDE" is not a recognised lane Id format' in validation_errors)
        self.assertTrue(
            '{row: 12, column: "Lane_ID"}: "50000-1%316" is not a recognised lane Id format' in validation_errors
        )
        self.assertTrue(
            '{row: 16, column: "Study_Reference"}: "PMID: 1" must be a comma-separated list of study references, e.g. PMID: 1234567, PMID: 23456789'
            in validation_errors
        )
        self.assertTrue(
            '{row: 19, column: "Study_Reference"}: "PMID: 1, PMID: 223" must be a comma-separated list of study references, e.g. PMID: 1234567, PMID: 23456789'
            in validation_errors
        )
        self.assertTrue(
            '{row: 23, column: "Selection_Random"}: "INVALID" is not in the list of legal options (yes, no)'
            in validation_errors
        )
        self.assertTrue(
            '{row: 24, column: "Country"}: "UNKNOWNCOUNTRY" is not in the list of legal options (TestCountryA, TestCountryB)'
            in validation_errors
        )
        # self.assertTrue(
        #    '{row: 25, column: "County/state"}: "%%%&*" contains illegal characters' in validation_errors)
        # self.assertTrue(
        #    '{row: 27, column: "City"}: "%%%&*" contains illegal characters' in validation_errors)
        self.assertTrue(
            '{row: 29, column: "Submitting_Institution"}: "UNKNOWN" is not in the list of legal options (Test Institution A, Test Institution B)'
            in validation_errors
        )
        self.assertTrue('{row: 30, column: "Collection_year"}: "1" must be a YYYY format year' in validation_errors)
        self.assertTrue('{row: 31, column: "Collection_year"}: "AB" must be a YYYY format year' in validation_errors)
        self.assertTrue('{row: 32, column: "Collection_month"}: "200" must be a MM format month' in validation_errors)
        self.assertTrue('{row: 33, column: "Collection_month"}: "AB" must be a MM format month' in validation_errors)
        self.assertTrue('{row: 34, column: "Collection_day"}: "500000" must be a DD format day' in validation_errors)
        self.assertTrue('{row: 35, column: "Collection_day"}: "ABCD" must be a DD format day' in validation_errors)
        self.assertTrue(
            '{row: 37, column: "Host_species"}: "Panda" is not in the list of legal options (human, bovine, fish, goat, camel, other)'
            in validation_errors
        )
        self.assertTrue(
            '{row: 38, column: "Gender"}: "INVALID" is not in the list of legal options (M, F)' in validation_errors
        )
        self.assertTrue(
            '{row: 44, column: "Age_years"}: "11111" should be a valid 1 to 3 digit number' in validation_errors
        )
        self.assertTrue(
            '{row: 44, column: "Age_months"}: "22222" should be a valid 1 to 4 digit number' in validation_errors
        )
        self.assertTrue(
            '{row: 44, column: "Age_weeks"}: "333333" should be a valid 1 to 4 digit number' in validation_errors
        )
        self.assertTrue(
            '{row: 44, column: "Age_days"}: "4444444" should be a valid 1 to 5 digit number' in validation_errors
        )
        self.assertTrue(
            '{row: 46, column: "Host_status"}: "GGG" is not in the list of legal options (carriage, invasive disease, non-invasive disease)'
            in validation_errors
        )
        self.assertTrue(
            '{row: 46, column: "Disease_type"}: "aaa" is not in the list of legal options (sepsis, bacteraemia, meningitis, pneumonia, urinary tract infection, skin and soft-tissue infection, osteomyelitis, endocarditis, septic arthritis, chorioamnionitis, peritonitis, empyema, surgical site infection, urosepsis, endometritis, mastitis, septicaemia, invasive other, non-invasive other)'
            in validation_errors
        )
        self.assertTrue(
            '{row: 46, column: "Disease_onset"}: "ZOG" is not in the list of legal options (EOD, LOD, VLOD, other)'
            in validation_errors
        )
        self.assertTrue(
            '{row: 46, column: "Isolation_source"}: "finger nails" is not in the list of legal options (rectovaginal swab, vaginal swab, ear swab, umbilical swab, umbilical swab, throat swab, skin swab, rectal swab, placenta, blood, cerebrospinal fluid, cord blood, pus: skin infection, pus: brain abscess, pus: other abscess, sputum, urine, pleural fluid, peritoneal fluid, pericardial fluid, joint/synovial fluid, bone, lymph node, semen, milk, spleen, kidney, liver, brain, heart, pancreas, other sterile site, other non-sterile site, abscess, abscess/pus fluid, aspirate fluid, blood vessels, bronchoalveolar lavage, burn, cellulitis/erysipelas, decubitus, drains/tubes, endotracheal aspirate, furuncle, gall bladder, impetiginous lesions, lungs, muscle tissue, prostate, skin ulcer, spinal cord, stomach, thoracentesis fluid, tissue fluid, trachea, ulcer fluid, urethra, urinary bladder, uterus, wound)'
            in validation_errors
        )
        self.assertTrue(
            '{row: 47, column: "Serotype"}: "IIIIIIII" is not in the list of legal options (Ia, Ib, II, III, IV, V, VI, VII, VIII, IX, NT)'
            in validation_errors
        )
        self.assertTrue(
            '{row: 47, column: "Infection_during_pregnancy"}: "HUH?" is not in the list of legal options (yes, no)'
            in validation_errors
        )
        self.assertTrue(
            '{row: 51, column: "Gestational_age_weeks"}: "ZZ" should be a valid 1 to 3 digit number'
            in validation_errors
        )
        self.assertTrue(
            '{row: 51, column: "Birthweight_gram"}: "HHHH" should be a valid 1 to 7 digit number' in validation_errors
        )
        self.assertTrue(
            '{row: 51, column: "Apgar_score"}: "AAA" should be a valid number between 0 and 10' in validation_errors
        )
        self.assertTrue(
            '{row: 52, column: "Maternal_infection_type"}: "OTHER" is not in the list of legal options (urinary tract infection, chorioamnionitis/intrauterine infection, sepsis, meningitis, arthritis, skin and soft-tissue infection, invasive other, non-invasive other)'
            in validation_errors
        )
        self.assertTrue(
            '{row: 58, column: "Ceftizoxime_method"}: "ZZZ" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)'
            in validation_errors
        )

        self.assertTrue(
            '{row: 58, column: "Cefoxitin"}: "A" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R'
            in validation_errors
        )
        self.assertTrue(
            '{row: 58, column: "Cefoxitin_method"}: "AAA" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)'
            in validation_errors
        )

        self.assertTrue(
            '{row: 58, column: "Cefotaxime"}: "B" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R'
            in validation_errors
        )
        self.assertTrue(
            '{row: 58, column: "Cefotaxime_method"}: "BBB" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)'
            in validation_errors
        )

        self.assertTrue(
            '{row: 58, column: "Cefazolin"}: "C" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R'
            in validation_errors
        )
        self.assertTrue(
            '{row: 58, column: "Cefazolin_method"}: "CCC" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)'
            in validation_errors
        )

        self.assertTrue(
            '{row: 58, column: "Ampicillin"}: "D" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R'
            in validation_errors
        )
        self.assertTrue(
            '{row: 58, column: "Ampicillin_method"}: "DDD" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)'
            in validation_errors
        )

        self.assertTrue(
            '{row: 58, column: "Penicillin"}: "R1" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R'
            in validation_errors
        )
        self.assertTrue(
            '{row: 58, column: "Penicillin_method"}: "EEE" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)'
            in validation_errors
        )

        self.assertTrue(
            '{row: 58, column: "Erythromycin"}: "F" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R'
            in validation_errors
        )
        self.assertTrue(
            '{row: 58, column: "Erythromycin_method"}: "FFF" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)'
            in validation_errors
        )

        self.assertTrue(
            '{row: 58, column: "Clindamycin"}: "G" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R'
            in validation_errors
        )
        self.assertTrue(
            '{row: 58, column: "Clindamycin_method"}: "GGG" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)'
            in validation_errors
        )

        self.assertTrue(
            '{row: 58, column: "Tetracycline"}: "H" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R'
            in validation_errors
        )
        self.assertTrue(
            '{row: 58, column: "Tetracycline_method"}: "HHH" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)'
            in validation_errors
        )

        self.assertTrue(
            '{row: 58, column: "Tetracycline"}: "H" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R'
            in validation_errors
        )
        self.assertTrue(
            '{row: 58, column: "Tetracycline_method"}: "HHH" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)'
            in validation_errors
        )

        self.assertTrue(
            '{row: 58, column: "Levofloxacin"}: "I1" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R'
            in validation_errors
        )
        self.assertTrue(
            '{row: 58, column: "Levofloxacin_method"}: "III" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)'
            in validation_errors
        )

        self.assertTrue(
            '{row: 58, column: "Ciprofloxacin"}: "J" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R'
            in validation_errors
        )
        self.assertTrue(
            '{row: 58, column: "Ciprofloxacin_method"}: "JJJJ" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)'
            in validation_errors
        )

        self.assertTrue(
            '{row: 58, column: "Daptomycin"}: "K" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R'
            in validation_errors
        )
        self.assertTrue(
            '{row: 58, column: "Daptomycin_method"}: "KKKK" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)'
            in validation_errors
        )

        self.assertTrue(
            '{row: 58, column: "Vancomycin"}: "S1" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R'
            in validation_errors
        )
        self.assertTrue(
            '{row: 58, column: "Vancomycin_method"}: "LLLL" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)'
            in validation_errors
        )

        self.assertTrue(
            '{row: 58, column: "Linezolid"}: "M" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R'
            in validation_errors
        )
        self.assertTrue(
            '{row: 58, column: "Linezolid_method"}: "MMMM" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)'
            in validation_errors
        )

        # Confirm the length checking works...
        self.assertTrue(
            '{row: 58, column: "Public_Name"}: "CD_XX_EW00056TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT" field length is greater than 256 characters'
            in validation_errors
        )

        self.assertTrue(
            '{row: 61, column: "Apgar_score"}: "9 [extra text 5]" should be a valid number between 0 and 10'
            in validation_errors
        )

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

    def test_csv_load_with_validation_errors(self) -> None:
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

    def test_tsv_load_with_validation_errors(self) -> None:
        validation_errors = self.under_test.load(
            glob.glob(self.TEST_TSV_SPREADSHEET_WITH_VALIDATION_ERRORS, recursive=True)[0]
        )
        # self.display_errors('test_csv_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)

    def test_txt_load_with_validation_errors(self) -> None:
        validation_errors = self.under_test.load(
            glob.glob(self.TEST_TXT_SPREADSHEET_WITH_VALIDATION_ERRORS, recursive=True)[0]
        )
        # self.display_errors('test_csv_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)

    def test_no_extension_load_with_validation_errors(self) -> None:
        previous_check_file_extension_value = self.under_test.check_file_extension
        previous_file_delimiter = self.under_test.file_delimiter
        self.under_test.check_file_extension = False
        self.under_test.file_delimiter = ","
        validation_errors = self.under_test.load(
            glob.glob(self.TEST_NO_EXTENSION_WITH_VALIDATION_ERRORS, recursive=True)[0]
        )
        self.under_test.check_file_extension = previous_check_file_extension_value
        self.under_test.file_delimiter = previous_file_delimiter
        # self.display_errors('test_csv_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)

    def test_csv_load_with_no_validation_errors(self) -> None:
        previous_check_file_extension_value = self.under_test.check_file_extension
        previous_file_delimiter = self.under_test.file_delimiter
        self.under_test.check_file_extension = False
        self.under_test.file_delimiter = ","
        validation_errors = self.under_test.load(
            glob.glob(self.TEST_NO_EXTENSION_SPREADSHEET_WITH_NO_ERRORS, recursive=True)[0]
        )
        self.under_test.check_file_extension = previous_check_file_extension_value
        self.under_test.file_delimiter = previous_file_delimiter
        # self.display_errors('test_load_with_no_validation_errors', validation_errors)
        self.assertEqual(len(validation_errors), 0)

    def test_tsv_load_with_no_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TSV_SPREADSHEET_WITH_NO_ERRORS, recursive=True)[0])
        # self.display_errors('test_load_with_no_validation_errors', validation_errors)

        self.assertEqual(len(validation_errors), 0)

    def test_txt_load_with_no_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TXT_SPREADSHEET_WITH_NO_ERRORS, recursive=True)[0])
        # self.display_errors('test_load_with_no_validation_errors', validation_errors)

        self.assertEqual(len(validation_errors), 0)

    def test_no_extension_load_with_no_validation_errors(self) -> None:
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

    def test_parse_metadata(self) -> None:
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

    def test_store_metadata(self) -> None:
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
            self.dao_mock.get_institutions.return_value = [
                Institution("Test Institution A", "TestCountryA"),
                Institution("Test Institution B", "TestCountryB"),
            ]

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

        self.assertTrue(
            '{row: 2, column: "Sample_id"}: "ZZZ;;{}{}{[[STUDY" contains illegal characters' in validation_errors
        )
        self.assertTrue('{row: 2, column: "23S1"}: "[pos]" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "23S3"}: "*" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "ERMB"}: "_" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "ERMT"}: "0" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "FOSA"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "GYRA"}: "+" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "LNUB"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "LSAC"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "MEFA"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "MPHC"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "MSRA"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "MSRD"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "PARC"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "RPOBGBS-1"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "RPOBGBS-2"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "RPOBGBS-3"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "RPOBGBS-4"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "SUL2"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "TETB"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "TETL"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "TETM"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "TETO"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "TETS"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "ALP1"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "ALP23"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "ALPHA"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "HVGA"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "PI1"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "PI2A1"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "PI2A2"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "PI2B"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "RIB"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 3, column: "SRR1"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue('{row: 2, column: "SRR2"}: "\'\'" must be pos, neg or empty' in validation_errors)
        self.assertTrue(
            '{row: 3, column: "23S1_SNP"}: "\'\'" must contain comma-separated variants (e.g. T78Q,L55A) or empty value'
            in validation_errors
        )
        self.assertTrue(
            '{row: 3, column: "23S3_SNP"}: "\'\'" must contain comma-separated variants (e.g. T78Q,L55A) or empty value'
            in validation_errors
        )

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

    def test_txt_load_with_no_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TXT_WITH_NO_ERRORS, recursive=True)[0])
        # self.display_errors('test_txt_load_with_no_validation_errors', validation_errors)
        self.assertEqual(len(validation_errors), 0)

    def test_txt_load_with_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TXT_WITH_VALIDATION_ERRORS, recursive=True)[0])
        # self.display_errors('test_tab_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)
