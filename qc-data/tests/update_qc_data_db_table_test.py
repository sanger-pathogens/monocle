import argparse
import os
from   unittest      import TestCase
from   unittest.mock import patch

from bin.update_qc_data_db_table import (
    get_api_config,
    _make_request,
    _find_files,
    _get_qc_data,
    _get_update_request_body,
    update_database,
    delete_qc_data_from_database,
    get_arguments,
    main
)

TEST_API_CONFIG   = {   'base_url'           : 'http://mock.metadata.api',
                        'qc_data_upload'     : '/metadata/mock_upload_endpoint',
                        'qc_data_delete_all' : '/metadata/mock_delete_endpoint'
                        }
TEST_DATA_DIR     = 'tests/test_data'
TEST_ENVIRONMENT  = {'MONOCLE_PIPELINE_QC_DATA': 'other/dir'}

class UpdateQCDataDBTable(TestCase):

   def test_get_api_config(self):
      # TODO add tests
      pass
   
   def test_make_request(self):
      # TODO add tests
      pass
   
   def test_find_files(self):
      # TODO add tests
      pass
   
   def test_get_qc_data(self):
      # TODO add tests
      pass
   
   def test_get_update_request_body(self):
      # TODO add tests
      pass
   
   def test_update_database(self):
      # TODO add tests
      pass

   @patch('bin.update_qc_data_db_table._make_request')
   def test_delete_qc_data_from_database(self, mock_make_request):
      delete_qc_data_from_database(TEST_API_CONFIG)
      mock_make_request.assert_called_once_with( TEST_API_CONFIG['base_url'] + TEST_API_CONFIG['qc_data_delete_all'] )
      
   def test_get_arguments(self):
      actual = get_arguments().parse_args(['--pipeline_qc_dir', 'qc_data_root_directory', '--log_level', 'INFO'])
      self.assertEqual(actual, argparse.Namespace(pipeline_qc_dir='qc_data_root_directory', log_level='INFO'))
      
   def test_get_arguments_short(self):
      actual = get_arguments().parse_args(['-D', 'qc_data_root_directory', '-L', 'DEBUG'])
      self.assertEqual(actual, argparse.Namespace(pipeline_qc_dir='qc_data_root_directory', log_level='DEBUG'))
      
   @patch.dict(os.environ, TEST_ENVIRONMENT, clear=True)
   def test_get_arguments_using_environ(self):
      actual = get_arguments().parse_args(['--log_level', 'ERROR'])
      self.assertEqual(actual, argparse.Namespace(pipeline_qc_dir='other/dir', log_level='ERROR'))
      
   def test_get_arguments_default(self):
      actual = get_arguments().parse_args([])
      self.assertEqual(actual, argparse.Namespace(pipeline_qc_dir='/app/monocle_pipeline_qc', log_level='WARNING'))
      
   @patch('bin.update_qc_data_db_table.get_arguments')
   @patch('bin.update_qc_data_db_table.get_api_config')
   @patch('bin.update_qc_data_db_table.delete_qc_data_from_database')
   @patch('bin.update_qc_data_db_table.update_database')
   def test_main(self, mock_update_database, mock_delete_qc_data_from_database, mock_get_api_config, mock_get_arguments):

      args = mock_get_arguments.return_value.parse_args()
      args.pipeline_qc_dir = TEST_DATA_DIR
      args.log_level = 'WARNING'
      mock_get_api_config.return_value = TEST_API_CONFIG

      main()
   
      mock_get_api_config.assert_called_once()
      mock_delete_qc_data_from_database.assert_called_once_with(TEST_API_CONFIG)
      mock_update_database.assert_called_once_with(TEST_DATA_DIR, TEST_API_CONFIG)
