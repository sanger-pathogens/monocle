import unittest
import flask
import logging
from unittest.mock import patch, Mock, call
from metadata.api.model.institution import Institution
from metadata.api.database.monocle_database_service_impl import MonocleDatabaseServiceImpl
from metadata.tests.test_data import *
from metadata.api.database.monocle_database_service_impl import ProtocolError
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text

class TestMonocleDatabaseServiceImpl(unittest.TestCase):
    """ Unit test class for MonocleDatabaseServiceImpl """

    def setUp(self) -> None:
        with patch('metadata.api.database.monocle_database_service_impl.Connector', autospec=True) as connector_mock:
            self.connector = connector_mock
            self.connection = Mock()
            self.transactional_connection = Mock()
            self.connection.__enter__ = lambda x: self.connection
            self.connection.__exit__ = Mock()
            self.transactional_connection.__enter__ = lambda x: self.transactional_connection
            self.transactional_connection.__exit__ = Mock()
            self.connector.get_transactional_connection.return_value = self.transactional_connection
            self.connector.get_connection.return_value = self.connection
            self.under_test = MonocleDatabaseServiceImpl(self.connector)

        self.response_as_string = '{"user_details": {"username": "mock_user", \
        "memberOf": [{"inst_id": "mock_id", "inst_name": "mock_name", "country_names": ["name1", "name2"]}, \
        {"inst_id": "LabCenEstPar", "inst_name": "Laboratório Central do Estado do Paraná", "country_names": ["Brazil"]}]}}'

        self.response_as_dict = {'user_details': {
            'username': 'mock_user',
            'memberOf': [{
                'inst_id': 'mock_id',
                'inst_name': 'mock_name',
                'country_names': ['name1', 'name2']
                },
                {
                'inst_id': 'LabCenEstPar',
                'inst_name': 'Laboratório Central do Estado do Paraná',
                'country_names': ['Brazil']
            }]
        }}

    @patch('metadata.api.database.monocle_database_service_impl.MonocleDatabaseServiceImpl.parse_response')
    @patch('metadata.api.database.monocle_database_service_impl.MonocleDatabaseServiceImpl.make_request')
    def test_get_institutions(self, make_request_mock, parse_response_mock) -> None:
        make_request_mock.return_value = self.response_as_string
        parse_response_mock.return_value = self.response_as_dict

        institutions = self.under_test.get_institutions('mock_user')

        self.assertIsNotNone(institutions)
        self.assertIsInstance(institutions, list)
        self.assertEqual(len(institutions), 3)
        self.assertIsInstance(institutions[0], Institution)
        self.assertEqual(institutions[0].name, 'mock_name')
        self.assertEqual(institutions[0].country, 'name1')
        self.assertIsInstance(institutions[1], Institution)
        self.assertEqual(institutions[1].name, 'mock_name')
        self.assertEqual(institutions[1].country, 'name2')
        self.assertIsInstance(institutions[2], Institution)
        self.assertEqual(institutions[2].name, 'Laboratório Central do Estado do Paraná')
        self.assertEqual(institutions[2].country, 'Brazil')

    def test_parse_response(self) -> None:
        actual = self.under_test.parse_response(self.response_as_string, ['user_details'])
        self.assertEqual(actual, self.response_as_dict)

    def test_parse_response_incorrect(self) -> None:
        response_as_string = '[{"Not": "a dictionary"}]'
        with self.assertRaises(ProtocolError):
            self.under_test.parse_response(response_as_string, ['user_details'])

    @patch.object(flask, 'request')
    def test_get_authenticated_username(self, mock_request) -> None:
        mock_request.headers = {'X-Remote-User': 'mock_user'}

        actual = self.under_test.get_authenticated_username(mock_request)

        self.assertEqual(actual, 'mock_user')

    def test_get_institution_names(self) -> None:
        self.connection.execute.return_value = [
            dict(name='Institution1', country='Israel', latitude=20.0, longitude=30.0),
            dict(name='Institution2', country='China', latitude=50.0, longitude=60.0)
        ]

        names = self.under_test.get_institution_names()
        self.assertIsNotNone(names)
        self.assertIsInstance(names, list)
        self.connection.execute.assert_called_with(MonocleDatabaseServiceImpl.SELECT_INSTITUTIONS_SQL)
        self.assertEqual(len(names), 2)
        self.assertEqual(names[0], 'Institution1')
        self.assertEqual(names[1], 'Institution2')

    def test_get_institution_names_noresults(self) -> None:
        self.connection.execute.return_value = []
        names = self.under_test.get_institution_names()
        self.connection.execute.assert_called_with(MonocleDatabaseServiceImpl.SELECT_INSTITUTIONS_SQL)
        self.assertIsNotNone(names)
        self.assertEqual(len(names), 0)

    # basically the same as test_get_download_metadata except query is SELECT_ALL_SAMPLES_SQL
    def test_get_samples(self) -> None:
        # Fake a returned result set...
        self.connection.execute.return_value = [
            dict(sanger_sample_id='9999STDY8113123',
                lane_id='2000_2#10',
                submitting_institution='UniversityA',
                supplier_sample_name='SUPPLIER_1',
                public_name='PUB_NAME_1',
                host_status='CARRIAGE',
                study_name='My_study1',
                study_ref='5201',
                selection_random='Y',
                country='UK',
                county_state='Cambridgeshire',
                city='Cambridge',
                collection_year='2019',
                collection_month='12',
                collection_day='05',
                host_species='human',
                gender='M',
                age_group='adult',
                age_years='35',
                age_months='10',
                age_weeks='2',
                age_days='2',
                disease_type='GBS',
                disease_onset='EOD',
                isolation_source='blood',
                serotype='IV',
                serotype_method='PCR',
                infection_during_pregnancy='N',
                maternal_infection_type='oral',
                gestational_age_weeks='10',
                birth_weight_gram='400',
                apgar_score='10',
                ceftizoxime='1',
                ceftizoxime_method='method1',
                cefoxitin='2',
                cefoxitin_method='method2',
                cefotaxime='3',
                cefotaxime_method='method3',
                cefazolin='4',
                cefazolin_method='method4',
                ampicillin='5',
                ampicillin_method='method5',
                penicillin='6',
                penicillin_method='method6',
                erythromycin='7',
                erythromycin_method='method7',
                clindamycin='8',
                clindamycin_method='method8',
                tetracycline='9',
                tetracycline_method='method9',
                levofloxacin='10',
                levofloxacin_method='method10',
                ciprofloxacin='11',
                ciprofloxacin_method='method11',
                daptomycin='12',
                daptomycin_method='method12',
                vancomycin='13',
                vancomycin_method='method13',
                linezolid='14',
                linezolid_method='method14'),
            dict(sanger_sample_id='9999STDY8113124',
                 lane_id='2000_2#11',
                 submitting_institution='UniversityB',
                 supplier_sample_name='SUPPLIER_2',
                 public_name='PUB_NAME_2',
                 host_status='INVASIVE',
                 study_name='My_stud2',
                 study_ref='5202',
                 selection_random='N',
                 country='US',
                 county_state='California',
                 city='Los Angeles',
                 collection_year='2020',
                 collection_month='10',
                 collection_day='07',
                 host_species='chimp',
                 gender='N',
                 age_group='adult',
                 age_years='45',
                 age_months='4',
                 age_weeks='1',
                 age_days='1',
                 disease_type='other',
                 disease_onset='LOD',
                 isolation_source='skin',
                 serotype='IX',
                 serotype_method='PCR2',
                 infection_during_pregnancy='Y',
                 maternal_infection_type='other',
                 gestational_age_weeks='12',
                 birth_weight_gram='500',
                 apgar_score='3',
                 ceftizoxime='11',
                 ceftizoxime_method='method11',
                 cefoxitin='12',
                 cefoxitin_method='method12',
                 cefotaxime='13',
                 cefotaxime_method='method13',
                 cefazolin='14',
                 cefazolin_method='method14',
                 ampicillin='15',
                 ampicillin_method='method15',
                 penicillin='16',
                 penicillin_method='method16',
                 erythromycin='17',
                 erythromycin_method='method17',
                 clindamycin='18',
                 clindamycin_method='method18',
                 tetracycline='19',
                 tetracycline_method='method19',
                 levofloxacin='20',
                 levofloxacin_method='method20',
                 ciprofloxacin='21',
                 ciprofloxacin_method='method21',
                 daptomycin='22',
                 daptomycin_method='method22',
                 vancomycin='23',
                 vancomycin_method='method23',
                 linezolid='24',
                 linezolid_method='method24')
        ]

        samples = self.under_test.get_samples()

        self.assertIsNotNone(samples)
        self.assertEqual(len(samples), 2)
        self.assertEqual(samples[0], TEST_SAMPLE_1)
        self.assertEqual(samples[1], TEST_SAMPLE_2)
        self.connection.execute.assert_called_with(MonocleDatabaseServiceImpl.SELECT_ALL_SAMPLES_SQL)

    def test_get_samples_noresults(self) -> None:
        self.connection.execute.return_value = []
        samples = self.under_test.get_samples()
        self.connection.execute.assert_called_with(MonocleDatabaseServiceImpl.SELECT_ALL_SAMPLES_SQL)
        self.assertIsNotNone(samples)
        self.assertEqual(len(samples), 0)

    def test_get_samples_filtered_by_metadata(self) -> None:
        self.connection.execute.return_value = [
                dict(sanger_sample_id='9999STDY8113123')
        ]
        samples_ids = self.under_test.get_samples_filtered_by_metadata({'serotype': ['IV']})
        execute_args    = list(self.connection.execute.call_args)
        execute_sql     = str(execute_args[0][0])
        execute_values  = execute_args[1]    
        self.assertEqual(2, len(execute_args), "expected 2 arguments to be passed to self.connection.execute")
        self.assertEqual(1, len(execute_args[0]), "expected 1 SQL query to be passed as first positional argument to self.connection.execute")
        self.assertEqual(execute_sql, MonocleDatabaseServiceImpl.FILTER_SAMPLES_IN_SQL.format('serotype'), "not the expected SQL query")
        self.assertEqual(execute_values, {'values': ('IV',)}, "not what was expected for :values in {}".format(MonocleDatabaseServiceImpl.FILTER_SAMPLES_IN_SQL))
        self.assertEqual(samples_ids, ['9999STDY8113123'])

    def test_get_samples_filtered_by_metadata_incl_null(self) -> None:
        self.connection.execute.return_value = [
                dict(sanger_sample_id='9999STDY8113123')
        ]
        # passing `None` is values list should result in SQL query that includes records with NULL serotype
        samples_ids = self.under_test.get_samples_filtered_by_metadata({'serotype': ['IV', None]})
        execute_args    = list(self.connection.execute.call_args)
        execute_sql     = str(execute_args[0][0])
        execute_values  = execute_args[1]    
        self.assertEqual(2, len(execute_args), "expected 2 arguments to be passed to self.connection.execute")
        self.assertEqual(1, len(execute_args[0]), "expected 1 SQL query to be passed as first positional argument to self.connection.execute")
        self.assertEqual(execute_sql, MonocleDatabaseServiceImpl.FILTER_SAMPLES_IN_SQL_INCL_NULL.format('serotype','serotype'), "not the expected SQL query")
        self.assertEqual(execute_values, {'values': ('IV', None)}, "not what was expected for :values in {}".format(MonocleDatabaseServiceImpl.FILTER_SAMPLES_IN_SQL_INCL_NULL))
        self.assertEqual(samples_ids, ['9999STDY8113123'])

    def test_get_samples_filtered_by_metadata_noresults(self) -> None:
        self.connection.execute.return_value = []
        samples_ids = self.under_test.get_samples_filtered_by_metadata({'serotype': ['None']})
        self.assertEqual(samples_ids, [])

    def test_get_samples_filtered_by_metadata_reject_request_if_bad_field_name(self) -> None:
        self.connection.execute.side_effect = OperationalError('mock params', 'mock orig', 'mock message including the substring Unknown column')
        expected = None
        samples_ids = self.under_test.get_samples_filtered_by_metadata({"bad_field_name": ['anything']})
        self.assertEqual(self.connection.execute.call_count, 1)
        self.assertEqual(samples_ids, expected)

    def test_get_lanes_filtered_by_in_silico_data(self) -> None:
        self.connection.execute.return_value = [
                {'lane_id':  '2000_2#10'}
        ]
        # passing `None` is values list should result in SQL query that includes records with NULL ST
        lanes_ids = self.under_test.get_lanes_filtered_by_in_silico_data({'ST': [None, '14']})
        execute_args    = list(self.connection.execute.call_args)
        execute_sql     = str(execute_args[0][0])
        execute_values  = execute_args[1]    
        self.assertEqual(2, len(execute_args), "expected 2 arguments to be passed to self.connection.execute")
        self.assertEqual(1, len(execute_args[0]), "expected 1 SQL query to be passed as first positional argument to self.connection.execute")
        self.assertEqual(execute_sql, MonocleDatabaseServiceImpl.IN_SILICO_FILTER_LANES_IN_SQL_INCL_NULL.format('ST','ST'), "not the expected SQL query")
        self.assertEqual(execute_values, {'values': (None,'14')}, "not what was expected for :values in {}".format(MonocleDatabaseServiceImpl.IN_SILICO_FILTER_LANES_IN_SQL_INCL_NULL))
        self.assertEqual(lanes_ids, ['2000_2#10'])

    def test_get_lanes_filtered_by_in_silico_data_incl_null(self) -> None:
        self.connection.execute.return_value = [
                {'lane_id':  '2000_2#10'}
        ]
        lanes_ids = self.under_test.get_lanes_filtered_by_in_silico_data({'ST': ['14']})
        execute_args    = list(self.connection.execute.call_args)
        execute_sql     = str(execute_args[0][0])
        execute_values  = execute_args[1]    
        self.assertEqual(2, len(execute_args), "expected 2 arguments to be passed to self.connection.execute")
        self.assertEqual(1, len(execute_args[0]), "expected 1 SQL query to be passed as first positional argument to self.connection.execute")
        self.assertEqual(execute_sql, MonocleDatabaseServiceImpl.IN_SILICO_FILTER_LANES_IN_SQL.format('ST'), "not the expected SQL query")
        self.assertEqual(execute_values, {'values': ('14',)}, "not what was expected for :values in {}".format(MonocleDatabaseServiceImpl.IN_SILICO_FILTER_LANES_IN_SQL))
        self.assertEqual(lanes_ids, ['2000_2#10'])

    def test_get_lanes_filtered_by_in_silico_data_noresults(self) -> None:
        self.connection.execute.return_value = []
        samples_ids = self.under_test.get_samples_filtered_by_metadata({'ST': ['None']})
        self.assertEqual(samples_ids, [])

    def test_get_lanes_filtered_by_in_silico_data_reject_request_if_bad_field_name(self) -> None:
        self.connection.execute.side_effect = OperationalError('mock params', 'mock orig', 'mock message including the substring Unknown column')
        expected = None
        samples_ids = self.under_test.get_samples_filtered_by_metadata({"bad_field_name": ['anything']})
        self.assertEqual(self.connection.execute.call_count, 1)
        self.assertEqual(samples_ids, expected)

    def test_get_samples_filtered_by_metadata_nofilters(self) -> None:
        self.connection.execute.return_value = [
            dict(sanger_sample_id='9999STDY8113123'),
            dict(sanger_sample_id='9999STDY8113124')
        ]
        samples_ids = self.under_test.get_samples_filtered_by_metadata({})
        self.assertEqual(samples_ids, ['9999STDY8113123', '9999STDY8113124'])

    def test_get_distinct_values(self) -> None:
        self.connection.execute.return_value = [
           {"serotype":"Ia"}, {"serotype":"II"}, {"serotype":"III"}, {"serotype":"Ib"}, {"serotype":None},
           ]
        expected = [
           {"name": "serotype", "values": ["II","III","Ia","Ib",None]}
           ]
        values = self.under_test.get_distinct_values('metadata', ["serotype"], ["National Reference Laboratories"])
        self.connection.execute.assert_called_once()
        #logging.critical("\nEXPECTED:\n{}\nGOT:{}".format(expected, values))
        self.assertEqual(values, expected)

    def test_get_distinct_values_multiple_fields_and_institutions(self) -> None:
        self.connection.execute.side_effect = [
           [{"serotype":"Ia"}, {"serotype":"II"}, {"serotype":"III"}, {"serotype":"Ib"}],
           [{"age_years":23},{"age_years":31}]
           ]
        expected = [
           {"name": "serotype",  "values": ["II","III","Ia","Ib"]},
           {"name": "age_years", "values": ["23", "31"]}
           ]
        values = self.under_test.get_distinct_values('metadata', ["serotype","age_years"], ["National Reference Laboratories", "The Chinese University of Hong Kong"])
        self.assertEqual(self.connection.execute.call_count, 2)
        self.assertEqual(values, expected)

    def test_get_distinct_values_reject_request_if_bad_field_name(self) -> None:
        self.connection.execute.side_effect = [
           [{"serotype":"Ia"}, {"serotype":"II"}, {"serotype":"III"}, {"serotype":"Ib"}],
           OperationalError('mock params', 'mock orig', 'mock message including the substring Unknown column')
           ]
        expected = None
        values = self.under_test.get_distinct_values('metadata', ["serotype","bad_field_name"], ["National Reference Laboratories"])
        self.assertEqual(self.connection.execute.call_count, 2)
        self.assertEqual(values, expected)

    def test_get_distinct_in_silico_values(self) -> None:
        self.connection.execute.return_value = [
           {"ST":"1"}, {"ST":"17"}, {"ST":None},
           ]
        expected = [
           {"name": "ST",  "values": ["1", "17", None]}
           ]
        values = self.under_test.get_distinct_values('in silico', ["ST"], ["National Reference Laboratories"])
        self.connection.execute.assert_called_once()
        self.assertEqual(values, expected)

    def test_get_distinct_in_silico_values_reject_request_if_bad_field_name(self) -> None:
        self.connection.execute.side_effect = [
           [{"ST":"1"}, {"ST":"17"}, {"ST":None}],
           OperationalError('mock params', 'mock orig', 'mock message including the substring Unknown column')
           ]
        expected = None
        values = self.under_test.get_distinct_values('in silico', ["ST","bad_field_name"], ["National Reference Laboratories"])
        self.assertEqual(self.connection.execute.call_count, 2)
        self.assertEqual(values, expected)

    def test_get_distinct_qc_data_values(self) -> None:
        self.connection.execute.return_value = [
           {"rel_abun_sa": 1.46}, {"rel_abun_sa": 92.93}, {"rel_abun_sa":None},
           ]
        expected = [
           {"name": "rel_abun_sa",  "values": ["1.46","92.93",None]},
           ]
        values = self.under_test.get_distinct_values('qc data', ["rel_abun_sa"], ["National Reference Laboratories"])
        self.connection.execute.assert_called_once()
        self.assertEqual(values, expected)

    def test_get_distinct_dc_data_values_reject_request_if_bad_field_name(self) -> None:
        self.connection.execute.side_effect = [
           [{"rel_abun_sa": 1.46}, {"rel_abun_sa": 92.93}, {"rel_abun_sa":None}],
           OperationalError('mock params', 'mock orig', 'mock message including the substring Unknown column')
           ]
        expected = None
        values = self.under_test.get_distinct_values('qc data', ["rel_abun_sa","bad_field_name"], ["National Reference Laboratories"])
        self.assertEqual(self.connection.execute.call_count, 2)
        self.assertEqual(values, expected)

    def test_update_sample_metadata(self) -> None:
        metadata_list = [TEST_SAMPLE_1, TEST_SAMPLE_2]
        self.under_test.update_sample_metadata(metadata_list)
        calls = [
            call(
                MonocleDatabaseServiceImpl.INSERT_OR_UPDATE_SAMPLE_SQL,
                sanger_sample_id='9999STDY8113123',
                lane_id='2000_2#10',
                submitting_institution='UniversityA',
                supplier_sample_name='SUPPLIER_1',
                public_name='PUB_NAME_1',
                host_status='CARRIAGE',
                study_name='My_study1',
                study_ref='5201',
                selection_random='Y',
                country='UK',
                county_state='Cambridgeshire',
                city='Cambridge',
                collection_year=2019,
                collection_month=12,
                collection_day=5,
                host_species='human',
                gender='M',
                age_group='adult',
                age_years=35,
                age_months=10,
                age_weeks=2,
                age_days=2,
                disease_type='GBS',
                disease_onset='EOD',
                isolation_source='blood',
                serotype='IV',
                serotype_method='PCR',
                infection_during_pregnancy='N',
                maternal_infection_type='oral',
                gestational_age_weeks=10,
                birth_weight_gram=400,
                apgar_score=10,
                ceftizoxime='1',
                ceftizoxime_method='method1',
                cefoxitin='2',
                cefoxitin_method='method2',
                cefotaxime='3',
                cefotaxime_method='method3',
                cefazolin='4',
                cefazolin_method='method4',
                ampicillin='5',
                ampicillin_method='method5',
                penicillin='6',
                penicillin_method='method6',
                erythromycin='7',
                erythromycin_method='method7',
                clindamycin='8',
                clindamycin_method='method8',
                tetracycline='9',
                tetracycline_method='method9',
                levofloxacin='10',
                levofloxacin_method='method10',
                ciprofloxacin='11',
                ciprofloxacin_method='method11',
                daptomycin='12',
                daptomycin_method='method12',
                vancomycin='13',
                vancomycin_method='method13',
                linezolid='14',
                linezolid_method='method14'
            )
        ]

        self.transactional_connection.execute.assert_has_calls(calls, any_order=False)

    def test_update_lane_in_silico_data(self) -> None:
        in_silico_data_list = [TEST_LANE_IN_SILICO_1, TEST_LANE_IN_SILICO_2]
        self.under_test.update_lane_in_silico_data(in_silico_data_list)
        calls = [
            call(
                MonocleDatabaseServiceImpl.INSERT_OR_UPDATE_IN_SILICO_SQL,
                lane_id='50000_2#282',
                cps_type='III',
                ST='ST-I',
                adhP='15',
                pheS='8',
                atr='4',
                glnA='4',
                sdhA='22',
                glcK='1',
                tkt='9',
                twenty_three_S1='pos',
                twenty_three_S3='pos',
                AAC6APH2='neg',
                AADECC='neg',
                ANT6='neg',
                APH3III='neg',
                APH3OTHER='neg',
                CATPC194='neg',
                CATQ='neg',
                ERMA='neg',
                ERMB='neg',
                ERMT='neg',
                LNUB='neg',
                LNUC='neg',
                LSAC='neg',
                MEFA='neg',
                MPHC='neg',
                MSRA='neg',
                MSRD='neg',
                FOSA='neg',
                GYRA='pos',
                PARC='pos',
                RPOBGBS_1='neg',
                RPOBGBS_2='neg',
                RPOBGBS_3='neg',
                RPOBGBS_4='neg',
                SUL2='neg',
                TETB='neg',
                TETL='neg',
                TETM='pos',
                TETO='neg',
                TETS='neg',
                ALP1='neg',
                ALP23='neg',
                ALPHA='neg',
                HVGA='pos',
                PI1='pos',
                PI2A1='neg',
                PI2A2='neg',
                PI2B='pos',
                RIB='pos',
                SRR1='neg',
                SRR2='pos',
                twenty_three_S1_variant = None,
                twenty_three_S3_variant = None,
                GYRA_variant='*',
                PARC_variant='*',
                RPOBGBS_1_variant = None,
                RPOBGBS_2_variant = None,
                RPOBGBS_3_variant = None,
                RPOBGBS_4_variant = None
            ),
            call(
                MonocleDatabaseServiceImpl.INSERT_OR_UPDATE_IN_SILICO_SQL,
                lane_id='50000_2#287',
                cps_type='III',
                ST='ST-II',
                adhP='3',
                pheS='11',
                atr='0',
                glnA='16',
                sdhA='14',
                glcK='31',
                tkt='6',
                twenty_three_S1='pos',
                twenty_three_S3='pos',
                AAC6APH2='neg',
                AADECC='neg',
                ANT6='neg',
                APH3III='neg',
                APH3OTHER='neg',
                CATPC194='neg',
                CATQ='neg',
                ERMA='neg',
                ERMB='neg',
                ERMT='neg',
                LNUB='neg',
                LNUC='neg',
                LSAC='neg',
                MEFA='neg',
                MPHC='neg',
                MSRA='neg',
                MSRD='neg',
                FOSA='neg',
                GYRA='pos',
                PARC='pos',
                RPOBGBS_1='neg',
                RPOBGBS_2='neg',
                RPOBGBS_3='neg',
                RPOBGBS_4='neg',
                SUL2='neg',
                TETB='neg',
                TETL='neg',
                TETM='pos',
                TETO='neg',
                TETS='neg',
                ALP1='neg',
                ALP23='neg',
                ALPHA='neg',
                HVGA='pos',
                PI1='pos',
                PI2A1='neg',
                PI2A2='neg',
                PI2B='pos',
                RIB='pos',
                SRR1='neg',
                SRR2='pos',
                twenty_three_S1_variant = None,
                twenty_three_S3_variant = None,
                GYRA_variant='GYRA-T78Q,L55A',
                PARC_variant='PARC-Q17S',
                RPOBGBS_1_variant = None,
                RPOBGBS_2_variant = None,
                RPOBGBS_3_variant = None,
                RPOBGBS_4_variant = None
            )
        ]

        self.transactional_connection.execute.assert_has_calls(calls, any_order=False)

    def test_update_lane_qc_data(self) -> None:
        qc_data_list = [TEST_LANE_QC_DATA_1, TEST_LANE_QC_DATA_2]
        self.under_test.update_lane_qc_data(qc_data_list)
        calls = [
            call(
                MonocleDatabaseServiceImpl.INSERT_OR_UPDATE_QC_DATA_SQL,
                lane_id='50000_2#282',
                rel_abun_sa='93.21',
            ),
            call(
                MonocleDatabaseServiceImpl.INSERT_OR_UPDATE_QC_DATA_SQL,
                lane_id='50000_2#287',
                rel_abun_sa='68.58',
            )
        ]
        self.transactional_connection.execute.assert_has_calls(calls, any_order=False)

    def test_update_sample_metadata_noinput(self) -> None:
        metadata_list = []
        self.under_test.update_sample_metadata(metadata_list)
        self.transactional_connection.get_connection.assert_not_called()
        metadata_list = None
        self.under_test.update_sample_metadata(metadata_list)
        self.transactional_connection.get_connection.assert_not_called()

    def test_update_lane_in_silico_data_noinput(self) -> None:
        in_silico_data_list = []
        self.under_test.update_sample_metadata(in_silico_data_list)
        self.transactional_connection.get_connection.assert_not_called()
        in_silico_data_list = None
        self.under_test.update_sample_metadata(in_silico_data_list)
        self.transactional_connection.get_connection.assert_not_called()
        
    def test_update_lane_qc_data_noinput(self) -> None:
        qc_data_list = []
        self.under_test.update_sample_metadata(qc_data_list)
        self.transactional_connection.get_connection.assert_not_called()
        qc_data_list = None
        self.under_test.update_sample_metadata(qc_data_list)
        self.transactional_connection.get_connection.assert_not_called()

    def test_get_download_metadata(self) -> None:

        input_list = ['9999STDY8113123', '9999STDY8113124']
        # Fake a returned result set...
        self.connection.execute.return_value = [
            dict(sanger_sample_id='9999STDY8113123',
                lane_id='2000_2#10',
                submitting_institution='UniversityA',
                supplier_sample_name='SUPPLIER_1',
                public_name='PUB_NAME_1',
                host_status='CARRIAGE',
                study_name='My_study1',
                study_ref='5201',
                selection_random='Y',
                country='UK',
                county_state='Cambridgeshire',
                city='Cambridge',
                collection_year='2019',
                collection_month='12',
                collection_day='05',
                host_species='human',
                gender='M',
                age_group='adult',
                age_years='35',
                age_months='10',
                age_weeks='2',
                age_days='2',
                disease_type='GBS',
                disease_onset='EOD',
                isolation_source='blood',
                serotype='IV',
                serotype_method='PCR',
                infection_during_pregnancy='N',
                maternal_infection_type='oral',
                gestational_age_weeks='10',
                birth_weight_gram='400',
                apgar_score='10',
                ceftizoxime='1',
                ceftizoxime_method='method1',
                cefoxitin='2',
                cefoxitin_method='method2',
                cefotaxime='3',
                cefotaxime_method='method3',
                cefazolin='4',
                cefazolin_method='method4',
                ampicillin='5',
                ampicillin_method='method5',
                penicillin='6',
                penicillin_method='method6',
                erythromycin='7',
                erythromycin_method='method7',
                clindamycin='8',
                clindamycin_method='method8',
                tetracycline='9',
                tetracycline_method='method9',
                levofloxacin='10',
                levofloxacin_method='method10',
                ciprofloxacin='11',
                ciprofloxacin_method='method11',
                daptomycin='12',
                daptomycin_method='method12',
                vancomycin='13',
                vancomycin_method='method13',
                linezolid='14',
                linezolid_method='method14'),
            dict(sanger_sample_id='9999STDY8113124',
                 lane_id='2000_2#11',
                 submitting_institution='UniversityB',
                 supplier_sample_name='SUPPLIER_2',
                 public_name='PUB_NAME_2',
                 host_status='INVASIVE',
                 study_name='My_stud2',
                 study_ref='5202',
                 selection_random='N',
                 country='US',
                 county_state='California',
                 city='Los Angeles',
                 collection_year='2020',
                 collection_month='10',
                 collection_day='07',
                 host_species='chimp',
                 gender='N',
                 age_group='adult',
                 age_years='45',
                 age_months='4',
                 age_weeks='1',
                 age_days='1',
                 disease_type='other',
                 disease_onset='LOD',
                 isolation_source='skin',
                 serotype='IX',
                 serotype_method='PCR2',
                 infection_during_pregnancy='Y',
                 maternal_infection_type='other',
                 gestational_age_weeks='12',
                 birth_weight_gram='500',
                 apgar_score='3',
                 ceftizoxime='11',
                 ceftizoxime_method='method11',
                 cefoxitin='12',
                 cefoxitin_method='method12',
                 cefotaxime='13',
                 cefotaxime_method='method13',
                 cefazolin='14',
                 cefazolin_method='method14',
                 ampicillin='15',
                 ampicillin_method='method15',
                 penicillin='16',
                 penicillin_method='method16',
                 erythromycin='17',
                 erythromycin_method='method17',
                 clindamycin='18',
                 clindamycin_method='method18',
                 tetracycline='19',
                 tetracycline_method='method19',
                 levofloxacin='20',
                 levofloxacin_method='method20',
                 ciprofloxacin='21',
                 ciprofloxacin_method='method21',
                 daptomycin='22',
                 daptomycin_method='method22',
                 vancomycin='23',
                 vancomycin_method='method23',
                 linezolid='24',
                 linezolid_method='method24')
        ]

        metadata = self.under_test.get_download_metadata(input_list)

        self.assertIsNotNone(metadata)
        self.assertEqual(len(metadata), 2)
        self.assertEqual(metadata[0], TEST_SAMPLE_1)
        self.assertEqual(metadata[1], TEST_SAMPLE_2)
        self.connection.execute.assert_called_with(MonocleDatabaseServiceImpl.SELECT_SAMPLES_SQL,
                                                   samples=('9999STDY8113123', '9999STDY8113124'))

    def test_get_download_metadata_noresults(self) -> None:
        input_list = ['9999STDY8113123', '9999STDY8113124']
        self.connection.execute.return_value = []

        metadata = self.under_test.get_download_metadata(input_list)
        self.assertIsNotNone(metadata)
        self.assertIsInstance(metadata, list)
        self.connection.execute.assert_called_with(MonocleDatabaseServiceImpl.SELECT_SAMPLES_SQL, samples=('9999STDY8113123', '9999STDY8113124'))
        self.assertEqual(len(metadata), 0)

    def test_convert_string(self) -> None:
        self.assertIsNone(self.under_test.convert_string(''))
        self.assertIsNone(self.under_test.convert_string(None))
        self.assertIsNotNone(self.under_test.convert_string('hello'))

    def test_convert_int(self) -> None:
        self.assertIsNone(self.under_test.convert_int(''))
        self.assertIsNone(self.under_test.convert_int(None))
        self.assertEqual(self.under_test.convert_int('12'), 12)
        self.assertEqual(self.under_test.convert_int('0'), 0)
        with self.assertRaises(ValueError):
            self.under_test.convert_int('hello')

    def test_get_download_in_silico_data(self) -> None:

        input_list = ['50000_2#282', '50000_2#287']
        # Fake a returned result set...
        self.connection.execute.return_value = [
            dict(lane_id='50000_2#282',
                cps_type='III',
                ST='ST-I',
                adhP='15',
                pheS='8',
                atr='4',
                glnA='4',
                sdhA='22',
                glcK='1',
                tkt='9',
                twenty_three_S1='pos',
                twenty_three_S3='pos',
                AAC6APH2='neg',
                AADECC='neg',
                ANT6='neg',
                APH3III='neg',
                APH3OTHER='neg',
                CATPC194='neg',
                CATQ='neg',
                ERMA='neg',
                ERMB='neg',
                ERMT='neg',
                LNUB='neg',
                LNUC='neg',
                LSAC='neg',
                MEFA='neg',
                MPHC='neg',
                MSRA='neg',
                MSRD='neg',
                FOSA='neg',
                GYRA='pos',
                PARC='pos',
                RPOBGBS_1='neg',
                RPOBGBS_2='neg',
                RPOBGBS_3='neg',
                RPOBGBS_4='neg',
                SUL2='neg',
                TETB='neg',
                TETL='neg',
                TETM='pos',
                TETO='neg',
                TETS='neg',
                ALP1='neg',
                ALP23='neg',
                ALPHA='neg',
                HVGA='pos',
                PI1='pos',
                PI2A1='neg',
                PI2A2='neg',
                PI2B='pos',
                RIB='pos',
                SRR1='neg',
                SRR2='pos',
                twenty_three_S1_variant = '',
                twenty_three_S3_variant = '',
                GYRA_variant = '*',
                PARC_variant = '*',
                RPOBGBS_1_variant = '',
                RPOBGBS_2_variant = '',
                RPOBGBS_3_variant = '',
                RPOBGBS_4_variant = ''),
            dict(lane_id='50000_2#287',
                cps_type='III',
                ST='ST-II',
                adhP='3',
                pheS='11',
                atr='0',
                glnA='16',
                sdhA='14',
                glcK='31',
                tkt='6',
                twenty_three_S1='pos',
                twenty_three_S3='pos',
                AAC6APH2='neg',
                AADECC='neg',
                ANT6='neg',
                APH3III='neg',
                APH3OTHER='neg',
                CATPC194='neg',
                CATQ='neg',
                ERMA='neg',
                ERMB='neg',
                ERMT='neg',
                LNUB='neg',
                LNUC='neg',
                LSAC='neg',
                MEFA='neg',
                MPHC='neg',
                MSRA='neg',
                MSRD='neg',
                FOSA='neg',
                GYRA='pos',
                PARC='pos',
                RPOBGBS_1='neg',
                RPOBGBS_2='neg',
                RPOBGBS_3='neg',
                RPOBGBS_4='neg',
                SUL2='neg',
                TETB='neg',
                TETL='neg',
                TETM='pos',
                TETO='neg',
                TETS='neg',
                ALP1='neg',
                ALP23='neg',
                ALPHA='neg',
                HVGA='pos',
                PI1='pos',
                PI2A1='neg',
                PI2A2='neg',
                PI2B='pos',
                RIB='pos',
                SRR1='neg',
                SRR2='pos',
                twenty_three_S1_variant = '',
                twenty_three_S3_variant = '',
                GYRA_variant='GYRA-T78Q,L55A',
                PARC_variant='PARC-Q17S',
                RPOBGBS_1_variant = '',
                RPOBGBS_2_variant = '',
                RPOBGBS_3_variant = '',
                RPOBGBS_4_variant = '')]

        in_silico_data = self.under_test.get_download_in_silico_data(input_list)
        self.assertIsNotNone(in_silico_data)
        self.assertEqual(len(in_silico_data), 2)
        self.assertEqual(in_silico_data[0], TEST_LANE_IN_SILICO_1)
        self.assertEqual(in_silico_data[1], TEST_LANE_IN_SILICO_2)
        self.connection.execute.assert_called_with(MonocleDatabaseServiceImpl.SELECT_LANES_IN_SILICO_SQL,
                                                   lanes=('50000_2#282', '50000_2#287'))
        
    def test_get_download_qc_data(self) -> None:

        input_list = ['50000_2#282', '50000_2#287']
        # Fake a returned result set...
        self.connection.execute.return_value = [
            dict(lane_id='50000_2#282',
                rel_abun_sa='93.21'),
            dict(lane_id='50000_2#287',
                rel_abun_sa='68.58')]

        qc_data = self.under_test.get_download_qc_data(input_list)
        self.assertIsNotNone(qc_data)
        self.assertEqual(len(qc_data), 2)
        self.assertEqual(qc_data[0], TEST_LANE_QC_DATA_1)
        self.assertEqual(qc_data[1], TEST_LANE_QC_DATA_2)
        self.connection.execute.assert_called_with(MonocleDatabaseServiceImpl.SELECT_LANES_QC_DATA_SQL,
                                                   lanes=('50000_2#282', '50000_2#287'))

