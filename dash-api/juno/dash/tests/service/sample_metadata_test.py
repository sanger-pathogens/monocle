from   unittest                     import TestCase
from   unittest.mock                import patch
from   urllib.error  import URLError
from   DataSources.sample_metadata  import SampleMetadata, Monocle_Client
from   DataSources.sample_metadata  import ProtocolError

import logging
logging.basicConfig(format='%(asctime)-15s %(levelname)s:  %(message)s', level='CRITICAL')

class SampleMetadataTest(TestCase):

   test_config       = 'dash/tests/mock_data/data_sources.yml' # ADD TEST PATH BEFORE DEPLOYMENT
   bad_config        = 'dash/tests/mock_data/data_sources_bad.yml'
   bad_db_cnf        = 'dash/tests/mock_data/bad.cnf'
   bad_api_host      = 'http://no.such.host/'
   bad_api_endpoint  = '/no/such/endpoint'
   genuine_api_host  = 'http://metadata_api.dev.pam.sanger.ac.uk/'

   mock_bad_get_sample     =  """{  "wrong key":
                                       {  "does": "not matter what appears here"
                                       }
                                    }"""
                                    
   mock_get_samples  = """{   "samples":  [  {  "lane_id": "fake_lane_1#123", "sanger_sample_id":"fake_sample_id_1", "public_name":"fake_name",
                                                "disease_name":"fake disease", "serotype": "fake_serotype", "host_status": "unknown",
                                                "submitting_institution": "Ministry of Health, Central laboratories", "id": "an_id"},
                                             {  "lane_id": "fake_lane_1#124", "sanger_sample_id":"fake_sample_id_2", "public_name":"fake_name",
                                                "disease_name":"fake disease", "serotype": "fake_serotype", "host_status": "unknown",
                                                "submitting_institution": "National Reference Laboratories", "id": "an_id"},
                                             {  "lane_id": "fake_lane_1#125", "sanger_sample_id":"fake_sample_id_3", "public_name":"fake_name",
                                                "disease_name":"fake disease", "serotype": "fake_serotype", "host_status": "unknown",
                                                "submitting_institution": "The Chinese University of Hong Kong", "id": "an_id"}
                                             ]
                              }"""

   mock_institution_names = """{ "institutions":   [  "Ministry of Health, Central laboratories",
                                                      "National Reference Laboratories",
                                                      "The Chinese University of Hong Kong"
                                                      ]
                                 }"""
                     

   expected_sample_ids = ['5903STDY8059053', '5903STDY8059055']
   expected_institution_names = ['Ministry of Health, Central laboratories', 'National Reference Laboratories', 'The Chinese University of Hong Kong']
   required_sample_dict_keys  = ['sample_id', 'public_name', 'host_status', 'serotype', 'submitting_institution_id']

   def setUp(self):
      self.sample_metadata = SampleMetadata(set_up=False)
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

   def test_reject_bad_url(self):
      with self.assertRaises(URLError):
         doomed = Monocle_Client(set_up=False)
         doomed.set_up(self.test_config)
         doomed.config['base_url'] = self.bad_api_host
         endpoint = doomed.config['samples'] + self.expected_sample_ids[0]
         doomed.make_request(endpoint)

   def test_reject_bad_endpoint(self):
      with self.assertRaises(URLError):
         doomed = Monocle_Client(set_up=False)
         doomed.set_up(self.test_config)
         doomed.config['base_url'] = self.genuine_api_host
         endpoint = self.bad_api_endpoint + self.expected_sample_ids[0]
         doomed.make_request(endpoint)


   #require equivalents of the following tests from monocledb:

   @patch('DataSources.sample_metadata.Monocle_Client.make_request')
   def test_institution_names(self,mock_query):
      mock_query.return_value = self.mock_institution_names
      names = self.sample_metadata.get_institution_names()
      self.assertIsInstance(names, type(['a list']))
      for expected in self.expected_institution_names:
         self.assertTrue(expected in names, msg="expected institution name '{}' not found in institution names".format(expected))

   @patch('DataSources.sample_metadata.Monocle_Client.make_request')
   def test_samples(self,mock_query):
      mock_query.return_value = self.mock_get_samples
      samples = self.sample_metadata.get_samples()
      self.assertIsInstance(samples, type(['a list']))
      for this_sample in samples:
         for required in self.required_sample_dict_keys:
            self.assertTrue(required in this_sample, msg="required key '{}' not found in sample dict".format(required))
            self.assertIsInstance(this_sample[required], type('a string'), msg="sample item {} should be a string".format(required))

   @patch.object(Monocle_Client, 'make_request')
   def test_reject_bad_get_sample_response(self, mock_request):
      with self.assertRaises(ProtocolError):
         mock_request.return_value = self.mock_bad_get_sample
         self.sample_metadata.get_samples(self.expected_sample_ids[0])

