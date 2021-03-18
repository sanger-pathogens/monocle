import sqlalchemy
from   unittest               import TestCase
from   unittest.mock          import patch
from   DataSources.monocledb  import MonocleDB

import logging
logging.basicConfig(format='%(asctime)-15s %(levelname)s:  %(message)s', level='INFO')

class MonocleDBTest(TestCase):

   test_config       = 'DataSources/tests/mock_data/data_sources.yml'
   bad_config        = 'DataSources/tests/mock_data/data_sources_bad.yml'
   bad_db_cnf        = 'DataSources/tests/mock_data/bad.cnf'
   # these patterns for database username and password may be too strict
   db_user_regex     = '[\w]+'
   db_passwd_regex   = '[\w%\-\.]+'
   db_host_regex     = '[\w\-]+\.internal\.sanger\.ac\.uk'
   db_name_regex     = 'monocle_\w+'
   expected_institution_names = ['Ministry of Health, Central laboratories', 'National Reference Laboratories', 'The Chinese University of Hong Kong']
   required_sample_dict_keys  = ['sample_id', 'public_name', 'host_status', 'serotype', 'submitting_institution_id']

   def setUp(self):
      self.db = MonocleDB(set_up=False)
      self.db.set_up(self.test_config)

   def test_init(self):
      self.assertIsInstance(self.db,         MonocleDB)
      self.assertIsInstance(self.db.db_url,  type('a string'))
      self.assertRegex(self.db.db_url,       '^mysql://'+self.db_user_regex+':'+self.db_passwd_regex+'@'+self.db_host_regex+':\d{4}/'+self.db_name_regex+'$')

   def test_reject_bad_config(self):
      with self.assertRaises(KeyError):
         doomed = MonocleDB(set_up=False)
         doomed.set_up(self.bad_config)
         
   def test_missing_config(self):
      with self.assertRaises(FileNotFoundError):
         doomed = MonocleDB(set_up=False)
         doomed.set_up('no_such_config.yml')

   def test_reject_bad_db_cnf(self):
      with self.assertRaises(KeyError):
         doomed = MonocleDB(set_up=False)
         doomed.read_db_config(self.bad_db_cnf)

   def test_missing_db_cnf(self):
      with self.assertRaises(FileNotFoundError):
         doomed = MonocleDB(set_up=False)
         doomed.read_db_config('no_such.cnf')

   @patch.object(MonocleDB, 'make_query')
   def test_institution_names(self,mock_query):
      mock_query.return_value = [[n] for n in self.expected_institution_names ]
      names = self.db.get_institution_names()
      self.assertIsInstance(names, type(['a list']))
      for expected in self.expected_institution_names:
         self.assertTrue(expected in names, msg="expected institution name '{}' not found in institution names".format(expected))

   @patch.object(MonocleDB, 'make_query')
   def test_samples(self,mock_query):
      mock_query.return_value = [   ['fake_lane_1#123', 'fake_sample_id', 'fake_name', 'fake disease', 'fake_serotype', n]
                                    for n in self.expected_institution_names
                                    ]
      samples = self.db.get_samples()
      self.assertIsInstance(samples, type(['a list']))
      for this_sample in samples:
         for required in self.required_sample_dict_keys:
            self.assertTrue(required in this_sample, msg="required key '{}' not found in sample dict".format(required))
            self.assertIsInstance(this_sample[required], type('a string'), msg="sample item {} should be a string".format(required))

