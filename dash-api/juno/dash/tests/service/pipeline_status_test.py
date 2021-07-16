from   pandas     import DataFrame, errors
import logging
from   unittest   import TestCase

from   DataSources.pipeline_status  import PipelineStatus, PipelineStatusDataError

# this helps to supress messages that may crop up with using TestCase.assertRaises()
logging.basicConfig(format='%(asctime)-15s %(levelname)s:  %(message)s', level='CRITICAL')

class PipelineStatusTest(TestCase):

   test_config          = 'dash/tests/mock_data/data_sources.yml'
   bad_config           = 'dash/tests/mock_data/data_sources_bad.yml'
   test_csv_file        = 'dash/tests/mock_data/s3/status/pipelines.csv'
   bad_csv_file         = 'dash/tests/mock_data/s3/status/pipelines_bad.csv'
   missing_col_csv_file = 'dash/tests/mock_data/s3/status/pipelines_9_cols.csv'
   empty_csv_file       = 'dash/tests/mock_data/s3/status/pipelines_empty.csv'
   
   # these lane IDs should be picked from test_csv_file as examples of various states
   mock_missing_lane_id       = 'no_such#lane'
   mock_successful_lane_id    = '31663_7#2'
   mock_all_pending_lane_id   = '31663_7#56'
   mock_qc_pending_lane_id    = '31663_7#7'
   mock_qc_failed_lane_id     = '31663_7#11'
   mock_aa_pending_lane_id    = '31663_7#48'
   mock_aa_failed_lane_id     = '31663_7#90'
   mock_all_failed_lane_id    = '31663_7#68'
   
   expected_csv_file                = test_csv_file
   expected_num_columns             = 10
   expected_dataframe_type          = DataFrame 
   expected_missing_lane_status     = {'FAILED': False, 'SUCCESS': False, 'Import': None,      'QC': None,      'Assemble': None,      'Annotate': None}
   expected_successful_lane_status  = {'FAILED': False, 'SUCCESS': True,  'Import': 'Done',    'QC': 'Done',    'Assemble': 'Done',    'Annotate': 'Done'}
   expected_all_pending_lane_status = {'FAILED': False, 'SUCCESS': False, 'Import': 'Pending', 'QC': 'Pending', 'Assemble': 'Pending', 'Annotate': 'Pending'}
   expected_qc_pending_lane_status  = {'FAILED': False, 'SUCCESS': False, 'Import': 'Done',    'QC': 'Pending', 'Assemble': 'Pending', 'Annotate': 'Pending'}
   expected_qc_failed_lane_status   = {'FAILED': True,  'SUCCESS': False, 'Import': 'Done',    'QC': 'Failed',  'Assemble': 'Failed',  'Annotate': 'Failed'}
   expected_aa_pending_lane_status  = {'FAILED': False, 'SUCCESS': False, 'Import': 'Done',    'QC': 'Done',    'Assemble': 'Pending', 'Annotate': 'Pending'}
   expected_aa_failed_lane_status   = {'FAILED': True,  'SUCCESS': False, 'Import': 'Done',    'QC': 'Done',    'Assemble': 'Failed',  'Annotate': 'Failed'}
   expected_all_failed_lane_status  = {'FAILED': True,  'SUCCESS': False, 'Import': 'Failed',  'QC': 'Failed',  'Assemble': 'Failed',  'Annotate': 'Failed'}

    
   def setUp(self):
      self.pipeline_status = PipelineStatus(config=self.test_config)
   
   def test_init(self):
      self.assertIsInstance(self.pipeline_status,           PipelineStatus)
      self.assertEqual(self.pipeline_status.csv_file,       self.expected_csv_file)
      self.assertEqual(self.pipeline_status.num_columns,    self.expected_num_columns)
      self.assertIsInstance(self.pipeline_status.dataframe, self.expected_dataframe_type)
 
   def test_reject_bad_config(self):
      with self.assertRaises(KeyError):
         PipelineStatus(config=self.bad_config)

   def test_reject_bad_input_file(self):
      with self.assertRaises(FileNotFoundError):
         PipelineStatus(config=self.test_config).populate_dataframe('good_luck_finding_this_chum')
      with self.assertRaises(errors.EmptyDataError):
         PipelineStatus(config=self.test_config).populate_dataframe(self.empty_csv_file)
      with self.assertRaises(PipelineStatusDataError):
         PipelineStatus(config=self.test_config).populate_dataframe(self.missing_col_csv_file)
      with self.assertRaises(PipelineStatusDataError):
         PipelineStatus(config=self.test_config).populate_dataframe(self.bad_csv_file)
   
   def test_missing_lane_status(self):
      lane_status = self.pipeline_status.lane_status(self.mock_missing_lane_id)
      self.assertEqual(self.expected_missing_lane_status, lane_status)
      
   def test_successful_lane_status(self):
      lane_status = self.pipeline_status.lane_status(self.mock_successful_lane_id)
      self.assertEqual(self.expected_successful_lane_status, lane_status)

   def test_all_pending_lane_status(self):
      lane_status = self.pipeline_status.lane_status(self.mock_all_pending_lane_id)
      self.assertEqual(self.expected_all_pending_lane_status, lane_status)
      
   def test_qc_pending_lane_status(self):
      lane_status = self.pipeline_status.lane_status(self.mock_qc_pending_lane_id)
      self.assertEqual(self.expected_qc_pending_lane_status, lane_status)
      
   def test_qc_failed_lane_status(self):
      lane_status = self.pipeline_status.lane_status(self.mock_qc_failed_lane_id)
      self.assertEqual(self.expected_qc_failed_lane_status, lane_status)
      
   def test_aa_pending_lane_status(self):
      lane_status = self.pipeline_status.lane_status(self.mock_aa_pending_lane_id)
      self.assertEqual(self.expected_aa_pending_lane_status, lane_status)
      
   def test_aa_failed_lane_status(self):
      lane_status = self.pipeline_status.lane_status(self.mock_aa_failed_lane_id)
      self.assertEqual(self.expected_aa_failed_lane_status, lane_status)
      
   def test_all_failed_lane_status(self):
      lane_status = self.pipeline_status.lane_status(self.mock_all_failed_lane_id)
      self.assertEqual(self.expected_all_failed_lane_status, lane_status)
