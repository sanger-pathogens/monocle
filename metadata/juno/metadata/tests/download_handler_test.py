import unittest
import json
from unittest.mock import patch, Mock
from metadata.tests.test_data import *
from metadata.api.download_handler import DownloadHandler
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition


class TestDownloadHandler(unittest.TestCase):
    """ Unit tests for the DownloadHandler class """

    CONFIG_FILE = 'config.json'

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
        value_field_name = 'value'
        with open(self.CONFIG_FILE) as cfg:
            data = json.load(cfg)
            sprd_def = SpreadsheetDefinition(2, data['spreadsheet_definition'])
            handler = DownloadHandler(self.dao_mock, sprd_def)
            results = handler.create_download_response([TEST_SAMPLE_1, TEST_SAMPLE_2])
            self.assertIsNotNone(results)
            self.assertEqual(len(results), 2)
            # Sample 1
            self.assertEqual(results[0]['sanger_sample_id'][value_field_name], '9999STDY8113123')
            self.assertEqual(results[0]['supplier_sample_name'][value_field_name], 'SUPPLIER_1')
            self.assertEqual(results[0]['public_name'][value_field_name], 'PUB_NAME_1')
            self.assertEqual(results[0]['lane_id'][value_field_name], '2000_2#10')
            self.assertEqual(results[0]['study_name'][value_field_name], 'My_study1')
            self.assertEqual(results[0]['study_ref'][value_field_name], '5201')
            self.assertEqual(results[0]['selection_random'][value_field_name], 'Y')
            self.assertEqual(results[0]['country'][value_field_name], 'UK')
            self.assertEqual(results[0]['county_state'][value_field_name], 'Cambridgeshire')
            self.assertEqual(results[0]['city'][value_field_name], 'Cambridge')
            self.assertEqual(results[0]['submitting_institution'][value_field_name], 'UniversityA')
            self.assertEqual(results[0]['collection_year'][value_field_name], '2019')
            self.assertEqual(results[0]['collection_month'][value_field_name], '12')
            self.assertEqual(results[0]['collection_day'][value_field_name], '05')
            self.assertEqual(results[0]['host_species'][value_field_name], 'human')
            self.assertEqual(results[0]['gender'][value_field_name], 'M')
            self.assertEqual(results[0]['age_group'][value_field_name], '30')
            self.assertEqual(results[0]['age_years'][value_field_name], '35')
            self.assertEqual(results[0]['age_months'][value_field_name], '10')
            self.assertEqual(results[0]['age_weeks'][value_field_name], '2')
            self.assertEqual(results[0]['age_days'][value_field_name], '2')
            self.assertEqual(results[0]['host_status'][value_field_name], 'CARRIAGE')
            self.assertEqual(results[0]['disease_type'][value_field_name], 'GBS')
            self.assertEqual(results[0]['disease_onset'][value_field_name], 'EOD')
            self.assertEqual(results[0]['isolation_source'][value_field_name], 'blood')
            self.assertEqual(results[0]['serotype'][value_field_name], 'IV')
            self.assertEqual(results[0]['serotype_method'][value_field_name], 'PCR')
            self.assertEqual(results[0]['infection_during_pregnancy'][value_field_name], 'N')
            self.assertEqual(results[0]['maternal_infection_type'][value_field_name], 'oral')
            self.assertEqual(results[0]['gestational_age_weeks'][value_field_name], '10')
            self.assertEqual(results[0]['birth_weight_gram'][value_field_name], '400')
            self.assertEqual(results[0]['apgar_score'][value_field_name], '10')
            self.assertEqual(results[0]['ceftizoxime'][value_field_name], '1')
            self.assertEqual(results[0]['ceftizoxime_method'][value_field_name], 'method1')
            self.assertEqual(results[0]['cefoxitin'][value_field_name], '2')
            self.assertEqual(results[0]['cefoxitin_method'][value_field_name], 'method2')
            self.assertEqual(results[0]['cefotaxime'][value_field_name], '3')
            self.assertEqual(results[0]['cefotaxime_method'][value_field_name], 'method3')
            self.assertEqual(results[0]['cefazolin'][value_field_name], '4')
            self.assertEqual(results[0]['cefazolin_method'][value_field_name], 'method4')
            self.assertEqual(results[0]['ampicillin'][value_field_name], '5')
            self.assertEqual(results[0]['ampicillin_method'][value_field_name], 'method5')
            self.assertEqual(results[0]['penicillin'][value_field_name], '6')
            self.assertEqual(results[0]['penicillin_method'][value_field_name], 'method6')
            self.assertEqual(results[0]['erythromycin'][value_field_name], '7')
            self.assertEqual(results[0]['erythromycin_method'][value_field_name], 'method7')
            self.assertEqual(results[0]['clindamycin'][value_field_name], '8')
            self.assertEqual(results[0]['clindamycin_method'][value_field_name], 'method8')
            self.assertEqual(results[0]['tetracycline'][value_field_name], '9')
            self.assertEqual(results[0]['tetracycline_method'][value_field_name], 'method9')
            self.assertEqual(results[0]['levofloxacin'][value_field_name], '10')
            self.assertEqual(results[0]['levofloxacin_method'][value_field_name], 'method10')
            self.assertEqual(results[0]['ciprofloxacin'][value_field_name], '11')
            self.assertEqual(results[0]['ciprofloxacin_method'][value_field_name], 'method11')
            self.assertEqual(results[0]['daptomycin'][value_field_name], '12')
            self.assertEqual(results[0]['daptomycin_method'][value_field_name], 'method12')
            self.assertEqual(results[0]['vancomycin'][value_field_name], '13')
            self.assertEqual(results[0]['vancomycin_method'][value_field_name], 'method13')
            self.assertEqual(results[0]['linezolid'][value_field_name], '14')
            self.assertEqual(results[0]['linezolid_method'][value_field_name], 'method14')
            # Sample 2 - test a few fields as sanity check
            self.assertEqual(results[1]['sanger_sample_id'][value_field_name], '9999STDY8113124')
            self.assertEqual(results[1]['supplier_sample_name'][value_field_name], 'SUPPLIER_2')
            self.assertEqual(results[1]['public_name'][value_field_name], 'PUB_NAME_2')
            self.assertEqual(results[1]['lane_id'][value_field_name], '2000_2#11')
