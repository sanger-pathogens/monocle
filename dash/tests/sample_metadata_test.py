from   unittest                     import TestCase
from   unittest.mock                import patch
from   DataSources.sample_metadata  import SampleMetadata, Monocle_Client

import logging
logging.basicConfig(format='%(asctime)-15s %(levelname)s:  %(message)s', level='CRITICAL')

class SampleMetadataTest(TestCase):

   test_config       = 'tests/mock_data/data_sources.yml'
   bad_config        = 'tests/mock_data/data_sources_bad.yml'
   bad_db_cnf        = 'tests/mock_data/bad.cnf'

   expected_institution_names = ['Ministry of Health, Central laboratories', 'National Reference Laboratories', 'The Chinese University of Hong Kong']
   required_sample_dict_keys  = ['sample_id', 'public_name', 'host_status', 'serotype', 'submitting_institution_id']

   def setUp(self):
      self.sample_metadata = SampleMetadata()
      self.sample_metadata.monocle_client = Monocle_Client(set_up=False)
      self.sample_metadata.monocle_client.set_up(self.test_config)

   def test_init(self):
      self.assertIsInstance(self.sample_metadata, SampleMetadata)

   def test_reject_bad_config(self):
      with self.assertRaises(KeyError):
         doomed = Monocle_Client(set_up=False)
         doomed.set_up(self.bad_config)
         
   def test_missing_config(self):
      with self.assertRaises(FileNotFoundError):
         doomed = Monocle_Client(set_up=False)
         doomed.set_up('no_such_config.yml')

   # this test case exists to ensure the unit tests fail, whilst still incomplete
   # we need to make sure nobody sees unit tests completing OK and thinks the tests are OK
   def test_DELIBERATELY_SETTING_UP_FAILED_TEST_BECAUSE_THESE_UNIT_TESTS_NOT_COMPLETED(self):
      self.assetEqual(True,False)

   #require equivalents of the following tests from monocledb:

   #@patch.object(MonocleDB, 'make_query')
   #def test_institution_names(self,mock_query):
      #mock_query.return_value = [[n] for n in self.expected_institution_names ]
      #names = self.db.get_institution_names()
      #self.assertIsInstance(names, type(['a list']))
      #for expected in self.expected_institution_names:
         #self.assertTrue(expected in names, msg="expected institution name '{}' not found in institution names".format(expected))

   #@patch.object(MonocleDB, 'make_query')
   #def test_samples(self,mock_query):
      #mock_query.return_value = [   ['fake_lane_1#123', 'fake_sample_id', 'fake_name', 'fake disease', 'fake_serotype', n]
                                    #for n in self.expected_institution_names
                                    #]
      #samples = self.db.get_samples()
      #self.assertIsInstance(samples, type(['a list']))
      #for this_sample in samples:
         #for required in self.required_sample_dict_keys:
            #self.assertTrue(required in this_sample, msg="required key '{}' not found in sample dict".format(required))
            #self.assertIsInstance(this_sample[required], type('a string'), msg="sample item {} should be a string".format(required))

