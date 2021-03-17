# TO DO: use a mock/dummy API, these tests rely on the MLWH API

import unittest
import DataSources.sequencing_status

#import logging
#logging.basicConfig(format='%(asctime)-15s %(levelname)s:  %(message)s', level='DEBUG')

#sequencing_status = DataSources.sequencing_status.SequencingStatus()
#print("\nSequencing status:\n")
#test_set = samples[0:3]
#sample_id_list = [ s['sample_id'] for s in test_set ]
#sequencing_status_data = sequencing_status.get_multiple_samples(sample_id_list)
##pp.pprint( sequencing_status_data )
#for this_sample in test_set:
   #this_sample['lane_id'] = [ lane['id'] for lane in sequencing_status_data[this_sample['sample_id']]['lanes'] ]
   #this_sample['sequencing_status'] = sequencing_status_data[this_sample['sample_id']]
#pp.pprint( test_set )




class SequencingStatusTest(unittest.TestCase):

   required_mlwh_config    = ['base_url', 'swagger', 'findById', 'findByIds']
   base_url_regex          = '^https?://[\w\-]+(\.dev)?\.pam\.sanger\.ac\.uk$'
   endpoint_regex          = '(/[\w\-\.]+)+'
   expected_sample_ids     = ['5903STDY8059053', '5903STDY8059054', '5903STDY8059055']
   required_sample_keys    = {'lanes'                 : type(['a list']),
                              'dna_measured_volume'   : type(1.1),
                              'dna_concentration'     : type(1.1),
                              'total_dna_ng'          : type(1.1),
                              }
   absent_sample_keys      = ['id']
   required_lane_keys      = {"id"                 : type('a string'),
                              "qc_lib"             : type(1),
                              "qc_seq"             : type(1),
                              "run_status"         : type('a string'),
                              "q30_yield_forward"  : type(1),
                              "q30_yield_reverse"  : type(1),
                              "q30_total_yield"    : type(1.1),
                              }
   def setUp(self):
      self.seq_status = DataSources.sequencing_status.SequencingStatus()

   def test_init(self):
      self.assertIsInstance(self.seq_status,             DataSources.sequencing_status.SequencingStatus)
      self.assertIsInstance(self.seq_status.mlwh_client, DataSources.sequencing_status.MLWH_Client)
            
   def test_config(self):
      self.assertRegex(self.seq_status.mlwh_client.base_url,            self.base_url_regex)
      self.assertRegex(self.seq_status.mlwh_client.swagger,             self.endpoint_regex)
      self.assertRegex(self.seq_status.mlwh_client.findById_ep,         self.endpoint_regex)
      self.assertIsInstance(self.seq_status.mlwh_client.findById_key,   type('a string'))
      self.assertRegex(self.seq_status.mlwh_client.findByIds_ep,        self.endpoint_regex)
      self.assertIsInstance(self.seq_status.mlwh_client.findByIds_key,  type('a string'))
      with self.assertRaises(FileNotFoundError):
         doomed = DataSources.sequencing_status.MLWH_Client()
         doomed.data_sources_config = 'no_such_config.yml'
         doomed.__init__()
         
   def test_get_sample(self):
      sample = self.seq_status.get_sample(self.expected_sample_ids[0])
      self.assertIsInstance(sample, type({'a': 'dict'}))
      for required in self.required_sample_keys.keys():
         self.assertTrue(required in sample, msg="required key '{}' not found in sample dict".format(required))
         self.assertIsInstance(sample[required], self.required_sample_keys[required], msg="sample item {} is wrong thpe".format(required))
         
   def test_get_multiple_samples(self):
      samples = self.seq_status.get_multiple_samples(self.expected_sample_ids)
      self.assertIsInstance(samples, type({'a': 'dict'}))
      for this_sample_id in self.expected_sample_ids:
         self.assertTrue(this_sample_id in samples, msg="test sample ID '{}' not returned by get_multiple_samples()".format(this_sample_id))
      for this_sample_id in samples.keys():
         this_sample = samples[this_sample_id]
         self.assertIsInstance(this_sample,   type({'a': 'dict'}), msg="sample should be a dict, not {}".format(type(this_sample)))
         for required in self.required_sample_keys.keys():
            self.assertTrue(required in this_sample, msg="required key '{}' not found in sample dict".format(required))
            self.assertIsInstance(this_sample[required], self.required_sample_keys[required], msg="sample item {} is wrong type".format(required))
         for required_absent in self.absent_sample_keys:
            self.assertFalse(required_absent in this_sample, msg="key '{}' found in sample dict, but it should be absent".format(required_absent))
         for this_lane in this_sample['lanes']:
            for required in self.required_lane_keys.keys():
               self.assertTrue(required in this_lane, msg="required key '{}' not found in lane dict".format(required))
               self.assertIsInstance(this_lane[required], self.required_lane_keys[required], msg="lane item {} is wrong type".format(required))
      
