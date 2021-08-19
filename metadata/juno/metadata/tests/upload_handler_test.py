import unittest
from unittest.mock import patch
import json
import glob
from typing import List
from metadata.api.upload_handlers import UploadMetadataHandler, UploadInSilicoHandler
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition
from metadata.api.model.institution import Institution
from metadata.api.model.metadata import Metadata
from metadata.api.model.in_silico_data import InSilicoData


class TestUploadHandler(unittest.TestCase):
    """ Unit tests for the UploadHandler class """

    TEST_TAB_SPREADSHEET_WITH_VALIDATION_ERRORS = '**/validation_test_spreadsheet.tab'
    TEST_TAB_SPREADSHEET_WITH_NO_ERRORS = '**/valid_spreadsheet.tab'
    TEST_TSV_SPREADSHEET_WITH_VALIDATION_ERRORS = '**/validation_test_spreadsheet.tsv'
    TEST_TSV_SPREADSHEET_WITH_NO_ERRORS = '**/valid_spreadsheet.tsv'
    TEST_TXT_SPREADSHEET_WITH_VALIDATION_ERRORS = '**/validation_test_spreadsheet.txt'
    TEST_TXT_SPREADSHEET_WITH_NO_ERRORS = '**/valid_spreadsheet.txt'
    CONFIG_FILE_PATH = 'config.json'

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
                    self.config['metadata']['spreadsheet_header_row_position'], self.config['metadata']['spreadsheet_definition'])
            self.under_test = UploadMetadataHandler(self.dao_mock, self.test_spreadsheet_def, True)

    def __check_validation_errors(self, validation_errors: List[str]):
        """ Assert validation errors are correct """
        self.assertEqual(len(validation_errors), 66)

        self.assertTrue(
            '{row: 4, column: "Sanger_Sample_ID"}: "ZZZ;;{}{}{[[STUDY" contains illegal characters' in validation_errors)
        self.assertTrue(
            '{row: 5, column: "Supplier_Sample_Name"}: "%%%%%@qwe" contains illegal characters' in validation_errors)
        self.assertTrue(
            '{row: 7, column: "Supplier_Sample_Name"}: "EY 70603" contains illegal characters' in validation_errors)
        self.assertTrue(
            '{row: 8, column: "Public_Name"}: "^&*%RTYUT" contains illegal characters' in validation_errors)
        self.assertTrue(
            '{row: 10, column: "Lane_ID"}: "ABCDE_2#FGI" is not a recognised lane Id format' in validation_errors)
        self.assertTrue(
            '{row: 11, column: "Lane_ID"}: "ABCDE" is not a recognised lane Id format' in validation_errors)
        self.assertTrue(
            '{row: 12, column: "Lane_ID"}: "50000-1%316" is not a recognised lane Id format' in validation_errors)
        self.assertTrue(
            '{row: 16, column: "Study_Reference"}: "PMID: 1" must be a comma-separated list of study references, e.g. PMID: 1234567, PMID: 23456789' in validation_errors)
        self.assertTrue(
            '{row: 19, column: "Study_Reference"}: "PMID: 1, PMID: 223" must be a comma-separated list of study references, e.g. PMID: 1234567, PMID: 23456789' in validation_errors)
        self.assertTrue(
            '{row: 23, column: "Selection_Random"}: "INVALID" is not in the list of legal options (yes, no)' in validation_errors)
        self.assertTrue(
            '{row: 24, column: "Country"}: "UNKNOWNCOUNTRY" is not in the list of legal options (TestCountryA, TestCountryB)' in validation_errors)
        self.assertTrue(
            '{row: 25, column: "County/state"}: "%%%&*" contains illegal characters' in validation_errors)
        self.assertTrue(
            '{row: 27, column: "City"}: "%%%&*" contains illegal characters' in validation_errors)
        self.assertTrue(
            '{row: 29, column: "Submitting_Institution"}: "UNKNOWN" is not in the list of legal options (Test Institution A, Test Institution B)' in validation_errors)
        self.assertTrue(
            '{row: 30, column: "Collection_year"}: "1" must be a YYYY format year' in validation_errors)
        self.assertTrue(
            '{row: 31, column: "Collection_year"}: "AB" must be a YYYY format year' in validation_errors)
        self.assertTrue(
            '{row: 32, column: "Collection_month"}: "200" must be a MM format month' in validation_errors)
        self.assertTrue(
            '{row: 33, column: "Collection_month"}: "AB" must be a MM format month' in validation_errors)
        self.assertTrue(
            '{row: 34, column: "Collection_day"}: "500000" must be a DD format day' in validation_errors)
        self.assertTrue(
            '{row: 35, column: "Collection_day"}: "ABCD" must be a DD format day' in validation_errors)
        self.assertTrue(
            '{row: 37, column: "Host_species"}: "Panda" is not in the list of legal options (human, bovine, fish, goat, camel, other)' in validation_errors)
        self.assertTrue(
            '{row: 38, column: "Gender"}: "INVALID" is not in the list of legal options (M, F)' in validation_errors)
        self.assertTrue(
            '{row: 44, column: "Age_years"}: "11111" should be a valid 1 to 3 digit number' in validation_errors)
        self.assertTrue(
            '{row: 44, column: "Age_months"}: "22222" should be a valid 1 to 4 digit number' in validation_errors)
        self.assertTrue(
            '{row: 44, column: "Age_weeks"}: "333333" should be a valid 1 to 4 digit number' in validation_errors)
        self.assertTrue(
            '{row: 44, column: "Age_days"}: "4444444" should be a valid 1 to 5 digit number' in validation_errors)
        self.assertTrue(
            '{row: 46, column: "Host_status"}: "GGG" is not in the list of legal options (carriage, invasive disease, non-invasive disease)' in validation_errors)
        self.assertTrue(
            '{row: 46, column: "Disease_type"}: "aaa" is not in the list of legal options (sepsis, bacteraemia, meningitis, pneumonia, urinary tract infection, skin and soft-tissue infection, osteomyelitis, endocarditis, septic arthritis, chorioamnionitis, peritonitis, empyema, surgical site infection, urosepsis, endometritis, mastitis, septicaemia, invasive other, non-invasive other)' in validation_errors)
        self.assertTrue(
            '{row: 46, column: "Disease_onset"}: "ZOG" is not in the list of legal options (EOD, LOD, VLOD, other)' in validation_errors)
        self.assertTrue(
            '{row: 46, column: "Isolation_source"}: "finger nails" is not in the list of legal options (rectovaginal swab, vaginal swab, ear swab, umbilical swab, umbilical swab, throat swab, skin swab, rectal swab, placenta, blood, cerebrospinal fluid, cord blood, pus: skin infection, pus: brain abscess, pus: other abscess, sputum, urine, pleural fluid, peritoneal fluid, pericardial fluid, joint/synovial fluid, bone, lymph node, semen, milk, spleen, kidney, liver, brain, heart, pancreas, other sterile site, other non-sterile site, abscess, abscess/pus fluid, aspirate fluid, blood vessels, bronchoalveolar lavage, burn, cellulitis/erysipelas, decubitus, drains/tubes, endotracheal aspirate, furuncle, gall bladder, impetiginous lesions, lungs, muscle tissue, prostate, skin ulcer, spinal cord, stomach, thoracentesis fluid, tissue fluid, trachea, ulcer fluid, urethra, urinary bladder, uterus, wound)' in validation_errors)
        self.assertTrue(
            '{row: 47, column: "Serotype"}: "IIIIIIII" is not in the list of legal options (Ia, Ib, II, III, IV, V, VI, VII, VIII, IX, NT)' in validation_errors)
        self.assertTrue(
            '{row: 47, column: "Infection_during_pregnancy"}: "HUH?" is not in the list of legal options (yes, no)' in validation_errors)
        self.assertTrue(
            '{row: 51, column: "Gestational_age_weeks"}: "ZZ" should be a valid 1 to 3 digit number' in validation_errors)
        self.assertTrue(
            '{row: 51, column: "Birthweight_gram"}: "HHHH" should be a valid 1 to 7 digit number' in validation_errors)
        self.assertTrue(
            '{row: 51, column: "Apgar_score"}: "AAA" should be a valid number between 0 and 10' in validation_errors)
        self.assertTrue(
            '{row: 52, column: "Maternal_infection_type"}: "OTHER" is not in the list of legal options (urinary tract infection, chorioamnionitis/intrauterine infection, sepsis, meningitis, arthritis, skin and soft-tissue infection, invasive other, non-invasive other)' in validation_errors)
        self.assertTrue(
            '{row: 58, column: "Ceftizoxime_method"}: "ZZZ" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)' in validation_errors)

        self.assertTrue(
            '{row: 58, column: "Cefoxitin"}: "A" should be a valid floating point number or alternatively S, I, or R' in validation_errors)
        self.assertTrue(
            '{row: 58, column: "Cefoxitin_method"}: "AAA" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)' in validation_errors)

        self.assertTrue(
            '{row: 58, column: "Cefotaxime"}: "B" should be a valid floating point number or alternatively S, I, or R' in validation_errors)
        self.assertTrue(
            '{row: 58, column: "Cefotaxime_method"}: "BBB" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)' in validation_errors)

        self.assertTrue(
            '{row: 58, column: "Cefazolin"}: "C" should be a valid floating point number or alternatively S, I, or R' in validation_errors)
        self.assertTrue(
            '{row: 58, column: "Cefazolin_method"}: "CCC" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)' in validation_errors)

        self.assertTrue(
            '{row: 58, column: "Ampicillin"}: "D" should be a valid floating point number or alternatively S, I, or R' in validation_errors)
        self.assertTrue(
            '{row: 58, column: "Ampicillin_method"}: "DDD" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)' in validation_errors)

        self.assertTrue(
            '{row: 58, column: "Penicillin"}: "R1" should be a valid floating point number or alternatively S, I, or R' in validation_errors)
        self.assertTrue(
            '{row: 58, column: "Penicillin_method"}: "EEE" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)' in validation_errors)

        self.assertTrue(
            '{row: 58, column: "Erythromycin"}: "F" should be a valid floating point number or alternatively S, I, or R' in validation_errors)
        self.assertTrue(
            '{row: 58, column: "Erythromycin_method"}: "FFF" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)' in validation_errors)

        self.assertTrue(
            '{row: 58, column: "Clindamycin"}: "G" should be a valid floating point number or alternatively S, I, or R' in validation_errors)
        self.assertTrue(
            '{row: 58, column: "Clindamycin_method"}: "GGG" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)' in validation_errors)

        self.assertTrue(
            '{row: 58, column: "Tetracycline"}: "H" should be a valid floating point number or alternatively S, I, or R' in validation_errors)
        self.assertTrue(
            '{row: 58, column: "Tetracycline_method"}: "HHH" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)' in validation_errors)

        self.assertTrue(
            '{row: 58, column: "Tetracycline"}: "H" should be a valid floating point number or alternatively S, I, or R' in validation_errors)
        self.assertTrue(
            '{row: 58, column: "Tetracycline_method"}: "HHH" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)' in validation_errors)

        self.assertTrue(
            '{row: 58, column: "Levofloxacin"}: "I1" should be a valid floating point number or alternatively S, I, or R' in validation_errors)
        self.assertTrue(
            '{row: 58, column: "Levofloxacin_method"}: "III" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)' in validation_errors)

        self.assertTrue(
            '{row: 58, column: "Ciprofloxacin"}: "J" should be a valid floating point number or alternatively S, I, or R' in validation_errors)
        self.assertTrue(
            '{row: 58, column: "Ciprofloxacin_method"}: "JJJJ" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)' in validation_errors)

        self.assertTrue(
            '{row: 58, column: "Daptomycin"}: "K" should be a valid floating point number or alternatively S, I, or R' in validation_errors)
        self.assertTrue(
            '{row: 58, column: "Daptomycin_method"}: "KKKK" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)' in validation_errors)

        self.assertTrue(
            '{row: 58, column: "Vancomycin"}: "S1" should be a valid floating point number or alternatively S, I, or R' in validation_errors)
        self.assertTrue(
            '{row: 58, column: "Vancomycin_method"}: "LLLL" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)' in validation_errors)

        self.assertTrue(
            '{row: 58, column: "Linezolid"}: "M" should be a valid floating point number or alternatively S, I, or R' in validation_errors)
        self.assertTrue(
            '{row: 58, column: "Linezolid_method"}: "MMMM" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)' in validation_errors)

        # Confirm the length checking works...
        self.assertTrue(
            '{row: 58, column: "Public_Name"}: "CD_XX_EW00056TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT" field length is greater than 256 characters' in validation_errors)

    def test_allowed_file_types(self):
        self.assertIsNotNone(self.under_test.allowed_file_types())
        self.assertEqual(sorted(self.under_test.allowed_file_types()), sorted(['tab', 'tsv', 'txt']))

    def test_is_valid_file_type(self):
        self.assertTrue(UploadMetadataHandler.is_valid_file_type(self.TEST_TAB_SPREADSHEET_WITH_NO_ERRORS))
        self.assertTrue(UploadMetadataHandler.is_valid_file_type(self.TEST_TSV_SPREADSHEET_WITH_NO_ERRORS))
        self.assertTrue(UploadMetadataHandler.is_valid_file_type(self.TEST_TXT_SPREADSHEET_WITH_NO_ERRORS))
        self.assertFalse(UploadMetadataHandler.is_valid_file_type('foo'))
        self.assertFalse(UploadMetadataHandler.is_valid_file_type(None))
        self.assertFalse(UploadMetadataHandler.is_valid_file_type(''))

    def test_tab_load_with_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TAB_SPREADSHEET_WITH_VALIDATION_ERRORS, recursive=True)[0])
        # self.display_errors('test_csv_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)

    def test_tsv_load_with_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TSV_SPREADSHEET_WITH_VALIDATION_ERRORS, recursive=True)[0])
        # self.display_errors('test_csv_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)

    def test_txt_load_with_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TXT_SPREADSHEET_WITH_VALIDATION_ERRORS, recursive=True)[0])
        # self.display_errors('test_csv_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)

    def test_tab_load_with_no_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TAB_SPREADSHEET_WITH_NO_ERRORS, recursive=True)[0])
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

    def test_parse_metadata(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TXT_SPREADSHEET_WITH_NO_ERRORS, recursive=True)[0])
        # self.display_errors('test_parse', validation_errors)

        self.assertEqual(len(validation_errors), 0)

        expected_results = [
            Metadata(sanger_sample_id='1000STDY7000166', lane_id='50000_2#282', submitting_institution='Test Institution A',
                 supplier_sample_name='EY70425', public_name='CD_XX_EW00001', host_status='invasive disease',
                 study_name='TEST-stUDY NA_ME1 (123), [ABC] %.', study_ref='PMID: 1234567, PMID: 12345678', selection_random='yes',
                 country='TestCountryA', county_state='State', city='London', collection_year='2014',
                 collection_month='10', collection_day='2', host_species='human', gender='M', age_group='neonate',
                 age_years='', age_months='', age_weeks='', age_days='', disease_type='bacteraemia',
                 disease_onset='EOD', isolation_source='blood', serotype='V', serotype_method='PCR',
                 infection_during_pregnancy='yes', maternal_infection_type='arthritis', gestational_age_weeks='12',
                 birth_weight_gram='130', apgar_score='3', ceftizoxime='1.2', ceftizoxime_method='Etest',
                 cefoxitin='10.334545', cefoxitin_method='disk diffusion', cefotaxime='100.4',
                 cefotaxime_method='agar dilution', cefazolin='1000.5', cefazolin_method='agar dilution',
                 ampicillin='10000.6', ampicillin_method='agar dilution', penicillin='100000.7',
                 penicillin_method='agar dilution', erythromycin='20.8', erythromycin_method='agar dilution',
                 clindamycin='70.4', clindamycin_method='agar dilution', tetracycline='0.3',
                 tetracycline_method='agar dilution', levofloxacin='12.2', levofloxacin_method='agar dilution',
                 ciprofloxacin='10.1', ciprofloxacin_method='agar dilution', daptomycin='10',
                 daptomycin_method='agar dilution', vancomycin='100', vancomycin_method='agar dilution', linezolid='20',
                 linezolid_method='agar dilution'),
            Metadata(sanger_sample_id='1000STDY7000167', lane_id='50000_2#287', submitting_institution='Test Institution A',
                 supplier_sample_name='EY_70601', public_name='CD_XX_EW00002', host_status='invasive disease',
                 study_name='', study_ref='PMID: 12345678', selection_random='no', country='TestCountryA',
                 county_state='', city='', collection_year='2014', collection_month='', collection_day='',
                 host_species='human', gender='', age_group='adult', age_years='25', age_months='1', age_weeks='1',
                 age_days='2', disease_type='bacteraemia', disease_onset='', isolation_source='blood', serotype='VI',
                 serotype_method='latex agglutination, PCR', infection_during_pregnancy='no',
                 maternal_infection_type='', gestational_age_weeks='', birth_weight_gram='',
                 apgar_score='', ceftizoxime='S', ceftizoxime_method='', cefoxitin='I', cefoxitin_method='',
                 cefotaxime='R', cefotaxime_method='', cefazolin='S', cefazolin_method='', ampicillin='S',
                 ampicillin_method='', penicillin='S', penicillin_method='', erythromycin='S', erythromycin_method='',
                 clindamycin='S', clindamycin_method='', tetracycline='S', tetracycline_method='', levofloxacin='S',
                 levofloxacin_method='', ciprofloxacin='S', ciprofloxacin_method='', daptomycin='S',
                 daptomycin_method='', vancomycin='S', vancomycin_method='', linezolid='S', linezolid_method=''),
            Metadata(sanger_sample_id='1000STDY7000168', lane_id='50000_2#291', submitting_institution='Test Institution A',
                 supplier_sample_name='EY_70602', public_name='CD_XX_EW00003', host_status='invasive disease',
                 study_name='', study_ref='', selection_random='no', country='TestCountryA', county_state='', city='',
                 collection_year='2014', collection_month='', collection_day='', host_species='',
                 gender='M', age_group='infant', age_years='', age_months='', age_weeks='',
                 age_days='', disease_type='septic arthritis', disease_onset='EOD', isolation_source='blood',
                 serotype='III', serotype_method='', infection_during_pregnancy='',
                 maternal_infection_type='', gestational_age_weeks='', birth_weight_gram='', apgar_score='',
                 ceftizoxime='1', ceftizoxime_method='Etest', cefoxitin='', cefoxitin_method='', cefotaxime='',
                 cefotaxime_method='', cefazolin='', cefazolin_method='', ampicillin='', ampicillin_method='',
                 penicillin='', penicillin_method='', erythromycin='', erythromycin_method='', clindamycin='',
                 clindamycin_method='', tetracycline='', tetracycline_method='', levofloxacin='',
                 levofloxacin_method='', ciprofloxacin='', ciprofloxacin_method='', daptomycin='', daptomycin_method='',
                 vancomycin='', vancomycin_method='', linezolid='', linezolid_method=''),
            Metadata(sanger_sample_id='1000STDY7000169', lane_id='50000_2#296', submitting_institution='Test Institution A',
                 supplier_sample_name='EY70603', public_name='CD_XX_EW00004', host_status='carriage', study_name='',
                 study_ref='', selection_random='no', country='TestCountryA', county_state='', city='',
                 collection_year='2014', collection_month='', collection_day='', host_species='human', gender='F',
                 age_group='adolescent', age_years='15', age_months='10', age_weeks='2', age_days='4', disease_type='',
                 disease_onset='', isolation_source='other sterile site', serotype='III', serotype_method='Lancefield',
                 infection_during_pregnancy='', maternal_infection_type='', gestational_age_weeks='',
                 birth_weight_gram='', apgar_score='', ceftizoxime='', ceftizoxime_method='', cefoxitin='',
                 cefoxitin_method='', cefotaxime='', cefotaxime_method='', cefazolin='', cefazolin_method='',
                 ampicillin='', ampicillin_method='', penicillin='', penicillin_method='', erythromycin='',
                 erythromycin_method='', clindamycin='', clindamycin_method='', tetracycline='', tetracycline_method='',
                 levofloxacin='', levofloxacin_method='', ciprofloxacin='', ciprofloxacin_method='', daptomycin='',
                 daptomycin_method='', vancomycin='', vancomycin_method='', linezolid='', linezolid_method='')]

        samples = self.under_test.parse()
        self.assertEqual(len(samples), len(expected_results))

        for idx in range(0, len(expected_results)-1):
            # print(samples[idx])
            self.assertEqual(samples[idx], expected_results[idx])

    def test_store_metadata_nothing_loaded(self) -> None:
        with self.assertRaises(RuntimeError):
            self.under_test.store()

    def test_store_metadata(self) -> None:
        self.under_test.load(glob.glob(self.TEST_TXT_SPREADSHEET_WITH_NO_ERRORS, recursive=True)[0])
        self.under_test.store()
        self.dao_mock.update_sample_metadata.assert_called_once()


class TestInSilicoUploadHandler(unittest.TestCase):
    """ Unit tests for the UploadHandler class """

    TEST_TAB_WITH_VALIDATION_ERRORS = '**/validation_test_in_silico_data.tab'
    TEST_TAB_WITH_NO_ERRORS = '**/valid_in_silico_data.tab'
    TEST_TSV_WITH_VALIDATION_ERRORS = '**/validation_test_in_silico_data.tsv'
    TEST_TSV_WITH_NO_ERRORS = '**/valid_in_silico_data.tsv'
    TEST_TXT_WITH_VALIDATION_ERRORS = '**/validation_test_in_silico_data.txt'
    TEST_TXT_WITH_NO_ERRORS = '**/valid_in_silico_data.txt'
    CONFIG_FILE_PATH = 'config.json'

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
                    self.config['in_silico_data']['spreadsheet_header_row_position'], self.config['in_silico_data']['spreadsheet_definition'])

            self.under_test = UploadInSilicoHandler(self.dao_mock, self.test_spreadsheet_def, True)

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
            '{row: 2, column: "glcK"}: "" must be a whole positive number' in validation_errors)
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
        self.assertTrue(UploadInSilicoHandler.is_valid_file_type(self.TEST_TAB_WITH_NO_ERRORS))
        self.assertTrue(UploadInSilicoHandler.is_valid_file_type(self.TEST_TSV_WITH_NO_ERRORS))
        self.assertTrue(UploadInSilicoHandler.is_valid_file_type(self.TEST_TXT_WITH_NO_ERRORS))
        self.assertFalse(UploadInSilicoHandler.is_valid_file_type('foo'))
        self.assertFalse(UploadInSilicoHandler.is_valid_file_type(None))
        self.assertFalse(UploadInSilicoHandler.is_valid_file_type(''))

    def test_tab_load_with_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TAB_WITH_VALIDATION_ERRORS, recursive=True)[0])
        #self.display_errors('test_tab_load_with_validation_errors', validation_errors)
        self.__check_validation_errors(validation_errors)

    def test_tab_load_with_no_validation_errors(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TAB_WITH_NO_ERRORS, recursive=True)[0])
        #self.display_errors('test_tab_load_with_no_validation_errors', validation_errors)
        self.assertEqual(len(validation_errors), 0)

    def test_tsv_load_with_validation_errors(self) -> None:
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

    def test_parse_in_silico_data(self) -> None:
        validation_errors = self.under_test.load(glob.glob(self.TEST_TXT_WITH_NO_ERRORS, recursive=True)[0])
        #self.display_errors('test_parse_in_silico_data', validation_errors)

        self.assertEqual(len(validation_errors), 0)

        expected_results = [
            InSilicoData(lane_id='50000_2#282', cps_type='III', ST='ST-I', adhP='15', pheS='8', atr='4', glnA='4', sdhA='22', glcK='1', tkt='9',
                twenty_three_S1='pos', twenty_three_S3='pos', CAT='neg', ERMB='neg', ERMT='neg', FOSA='neg', GYRA='pos', LNUB='neg',
                LSAC='neg', MEFA='neg', MPHC='neg', MSRA='neg', MSRD='neg', PARC='pos', RPOBGBS_1='neg', RPOBGBS_2='neg', RPOBGBS_3='neg',
                RPOBGBS_4='neg', SUL2='neg', TETB='neg', TETL='neg', TETM='pos', TETO='neg', TETS='neg', ALP1='neg', ALP23='neg', ALPHA='neg',
                HVGA='pos', PI1='pos', PI2A1='neg', PI2A2='neg', PI2B='pos', RIB='pos', SRR1='neg', SRR2='pos', GYRA_variant='*', PARC_variant='*'),
            InSilicoData(lane_id='50000_2#287', cps_type='III', ST='ST-2', adhP='3', pheS='11', atr='0', glnA='16', sdhA='14', glcK='31', tkt='6',
                twenty_three_S1='pos', twenty_three_S3='pos', CAT='neg', ERMB='neg', ERMT='neg', FOSA='neg', GYRA='pos', LNUB='neg',
                LSAC='neg', MEFA='neg', MPHC='neg', MSRA='neg', MSRD='neg', PARC='pos', RPOBGBS_1='neg', RPOBGBS_2='neg', RPOBGBS_3='neg',
                RPOBGBS_4='neg', SUL2='neg', TETB='neg', TETL='neg', TETM='pos', TETO='neg', TETS='neg', ALP1='neg', ALP23='neg', ALPHA='neg',
                HVGA='pos', PI1='pos', PI2A1='neg', PI2A2='neg', PI2B='pos', RIB='pos', SRR1='neg', SRR2='pos', GYRA_variant='GYRA-T78Q,L55A', PARC_variant='PARC-Q17S')]

        samples = self.under_test.parse()
        self.assertEqual(len(samples), len(expected_results))

        for idx in range(0, len(expected_results)-1):
            #print(samples[idx])
            self.assertEqual(samples[idx], expected_results[idx])

    def test_store_in_silico_nothing_loaded(self) -> None:
        with self.assertRaises(RuntimeError):
            self.under_test.store()

    def test_store_in_silico(self) -> None:
        self.under_test.load(glob.glob(self.TEST_TXT_WITH_NO_ERRORS, recursive=True)[0])
        self.under_test.store()
        self.dao_mock.update_lane_in_silico_data.assert_called_once()
