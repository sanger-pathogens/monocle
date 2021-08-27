import unittest
from unittest.mock import patch, Mock, call
from metadata.api.model.institution import Institution
from metadata.api.database.monocle_database_service_impl import MonocleDatabaseServiceImpl
from metadata.tests.test_data import *


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

    def test_get_institutions(self) -> None:
        self.connection.execute.return_value = [
            dict(name='Institution1', country='Israel', latitude=20.0, longitude=30.0),
            dict(name='Institution2', country='China', latitude=50.0, longitude=60.0)
        ]

        institutions = self.under_test.get_institutions()
        self.assertIsNotNone(institutions)
        self.assertIsInstance(institutions, list)
        self.connection.execute.assert_called_with(MonocleDatabaseServiceImpl.SELECT_INSTITUTIONS_SQL)
        self.assertEqual(len(institutions), 2)
        self.assertIsInstance(institutions[0], Institution)
        self.assertEqual(institutions[0].name, 'Institution1')
        self.assertEqual(institutions[0].country, 'Israel')
        self.assertEqual(institutions[0].latitude, 20.0)
        self.assertEqual(institutions[0].longitude, 30.0)
        self.assertIsInstance(institutions[1], Institution)
        self.assertEqual(institutions[1].name, 'Institution2')
        self.assertEqual(institutions[1].country, 'China')
        self.assertEqual(institutions[1].latitude, 50.0)
        self.assertEqual(institutions[1].longitude, 60.0)

    def test_get_institutions_noresults(self) -> None:
        self.connection.execute.return_value = []
        institutions = self.under_test.get_institutions()
        self.connection.execute.assert_called_with(MonocleDatabaseServiceImpl.SELECT_INSTITUTIONS_SQL)
        self.assertIsNotNone(institutions)
        self.assertEqual(len(institutions), 0)
        
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
            dict(sample_id='9999STDY8113123',
                lane_id='2000_2#10',
                submitting_institution_id='UniversityA',
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
                birthweight_gram='400',
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
            dict(sample_id='9999STDY8113124',
                 lane_id='2000_2#11',
                 submitting_institution_id='UniversityB',
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
                 birthweight_gram='500',
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

    def test_update_sample_metadata(self) -> None:
        metadata_list = [TEST_SAMPLE_1, TEST_SAMPLE_2]
        self.under_test.update_sample_metadata(metadata_list)
        calls = [
            call(
                MonocleDatabaseServiceImpl.INSERT_OR_UPDATE_SAMPLE_SQL,
                sanger_sample_id='9999STDY8113123',
                lane_id='2000_2#10',
                submitting_institution_id='UniversityA',
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
        in_silico_data_list = [TEST_LANE_1, TEST_LANE_2]
        self.under_test.update_lane_in_silico_data(in_silico_data_list)
        calls = [
            call(
                MonocleDatabaseServiceImpl.INSERT_OR_UPDATE_IN_SILICO_SQL,
                lane_id='50000_2#282',
                cps_type='III',
                ST='ST-I',
                adhP=15,
                pheS=8,
                atr=4,
                glnA=4,
                sdhA=22,
                glcK=1,
                tkt=9,
                twenty_three_S1='pos',
                twenty_three_S3='pos',
                CAT='neg',
                ERMB='neg',
                ERMT='neg',
                FOSA='neg',
                GYRA='pos',
                LNUB='neg',
                LSAC='neg',
                MEFA='neg',
                MPHC='neg',
                MSRA='neg',
                MSRD='neg',
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
                GYRA_variant='*',
                PARC_variant='*'
            ),
            call(
                MonocleDatabaseServiceImpl.INSERT_OR_UPDATE_IN_SILICO_SQL,
                lane_id='50000_2#287',
                cps_type='III',
                ST='ST-II',
                adhP=3,
                pheS=11,
                atr=0,
                glnA=16,
                sdhA=14,
                glcK=31,
                tkt=6,
                twenty_three_S1='pos',
                twenty_three_S3='pos',
                CAT='neg',
                ERMB='neg',
                ERMT='neg',
                FOSA='neg',
                GYRA='pos',
                LNUB='neg',
                LSAC='neg',
                MEFA='neg',
                MPHC='neg',
                MSRA='neg',
                MSRD='neg',
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
                GYRA_variant='GYRA-T78Q,L55A',
                PARC_variant='PARC-Q17S'
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
        in_silic_data_list = []
        self.under_test.update_sample_metadata(in_silic_data_list)
        self.transactional_connection.get_connection.assert_not_called()
        in_silic_data_list = None
        self.under_test.update_sample_metadata(in_silic_data_list)
        self.transactional_connection.get_connection.assert_not_called()

    def test_get_download_metadata(self) -> None:

        input_list = ['9999STDY8113123:2000_2#10', '9999STDY8113124:2000_2#11']
        # Fake a returned result set...
        self.connection.execute.return_value = [
            dict(sample_id='9999STDY8113123',
                lane_id='2000_2#10',
                submitting_institution_id='UniversityA',
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
                birthweight_gram='400',
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
            dict(sample_id='9999STDY8113124',
                 lane_id='2000_2#11',
                 submitting_institution_id='UniversityB',
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
                 birthweight_gram='500',
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
        self.connection.execute.assert_called_with(MonocleDatabaseServiceImpl.SELECT_LANES_SQL,
                                                   lanes=('2000_2#10', '2000_2#11'))

    def test_get_download_metadata_noresults(self) -> None:
        input_list = ['9999STDY8113123:2000_2#10', '9999STDY8113124:2000_2#11']
        self.connection.execute.return_value = []

        metadata = self.under_test.get_download_metadata(input_list)
        self.assertIsNotNone(metadata)
        self.assertIsInstance(metadata, list)
        self.connection.execute.assert_called_with(MonocleDatabaseServiceImpl.SELECT_LANES_SQL, lanes=('2000_2#10', '2000_2#11'))
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
