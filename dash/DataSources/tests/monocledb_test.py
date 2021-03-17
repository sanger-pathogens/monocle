# TO DO: use a mock/dummy API, these tests rely on the MLWH API

import sqlalchemy
import unittest
import DataSources.monocledb

#import logging
#logging.basicConfig(format='%(asctime)-15s %(levelname)s:  %(message)s', level='DEBUG')

class MonocleDBTest(unittest.TestCase):

   connection_class  = sqlalchemy.engine.base.Connection
   # these patterns for database username and password may be too strict
   db_user_regex     = '[\w]+'
   db_passwd_regex   = '[\w]+'
   db_host_regex     = '[\w\-]+\.internal\.sanger\.ac\.uk'
   db_name_regex     = 'monocle_\w+'
   expected_institution_names = ['Ministry of Health, Central laboratories', 'National Reference Laboratories', 'The Chinese University of Hong Kong']
   required_sample_dict_keys  = ['sample_id', 'public_name', 'host_status', 'serotype', 'submitting_institution_id']

   def setUp(self):
      self.db = DataSources.monocledb.MonocleDB()

   def test_init(self):
      self.assertIsInstance(self.db,               DataSources.monocledb.MonocleDB)
      self.assertIsInstance(self.db.connection(),  self.connection_class)
      self.assertIsInstance(self.db.db_url,        type('a string'))
      self.assertRegex(self.db.db_url,             '^mysql://'+self.db_user_regex+':'+self.db_passwd_regex+'@'+self.db_host_regex+':\d{4}/'+self.db_name_regex+'$')
      
   def test_missing_config(self):
      with self.assertRaises(FileNotFoundError):
         doomed = DataSources.monocledb.MonocleDB()
         doomed.data_sources_config = 'no_such_config.yml'
         doomed.__init__()

   def test_institution_names(self):
      names = self.db.get_institution_names()
      self.assertIsInstance(names, type(['a list']))
      for expected in self.expected_institution_names:
         self.assertTrue(expected in names, msg="expected institution name '{}' not found in institution names".format(expected))
      
   def test_samples(self):
      samples = self.db.get_samples()
      self.assertIsInstance(samples, type(['a list']))
      for this_sample in samples[0:3]:
         for required in self.required_sample_dict_keys:
            self.assertTrue(required in this_sample, msg="required key '{}' not found in sample dict".format(required))
            self.assertIsInstance(this_sample[required], type('a string'), msg="sample item {} should be a string".format(required))

