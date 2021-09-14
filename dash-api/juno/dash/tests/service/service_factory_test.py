from   unittest      import TestCase
from   unittest.mock import patch
from   datetime      import datetime
import logging
from   os            import environ
from   pathlib       import Path
import yaml

from   DataSources.sample_metadata     import SampleMetadata, Monocle_Client
from   DataSources.sequencing_status   import SequencingStatus, MLWH_Client
from   DataSources.pipeline_status     import PipelineStatus
from   DataSources.metadata_download   import MetadataDownload, Monocle_Download_Client
from   DataSources.user_data           import UserData
from   data_services                   import MonocleUser, MonocleData

class MonocleUserTest(TestCase):
   
   test_config             = 'dash/tests/mock_data/data_sources.yml'
   mock_ldap_result_user   = (   'cn=mock_user_sanger_ac_uk,ou=users,dc=monocle,dc=pam,dc=sanger,dc=ac,dc=uk',
                                 {  'cn': [b'mock_user_sanger_ac_uk'],
                                    'gidNumber': [b'501'],
                                    'homeDirectory': [b'/home/users/tmock_user_sanger_ac_uk'],
                                    'mail': [b'mock_user@sanger.ac.uk'],
                                    'o': [b'501', b'502'],
                                    'objectClass': [b'inetOrgPerson', b'posixAccount', b'top'],
                                    'sn': [b'mock_user_sanger_ac_uk'],
                                    'uid': [b'mock_user'],
                                    'uidNumber': [b'1000']
                                    }
                                 )
   mock_ldap_result_group  = (   'cn=WelSanIns,ou=groups,dc=monocle,dc=dev,dc=pam,dc=sanger,dc=ac,dc=uk',
                                 {  'cn': [b'WelSanIns'],
                                    'description': [b'Wellcome Sanger Institute'],
                                    'gidNumber': [b'501'],
                                    'objectClass': [b'posixGroup', b'top']
                                    }
                                 )

   def setUp(self):
      self.user = MonocleUser(set_up=False)
      self.user.user_data.set_up(self.test_config)

   def test_init(self):
      self.assertIsInstance(self.user, MonocleUser)

   @patch.object(UserData, 'ldap_search_group_by_gid')
   @patch.object(UserData, 'ldap_search_user_by_username')
   def test_load_user_record(self,mock_user_query,mock_group_query):
      mock_user_query.return_value  = self.mock_ldap_result_user
      mock_group_query.return_value = self.mock_ldap_result_group
      user_record = self.user.load_user_record('mock_user')
      self.assertIsInstance(user_record, type({'a': 'dict'}))
      self.assertIsInstance( user_record,                              type({'a': 'dict'})  )
      self.assertIsInstance( user_record['username'],                  type('a string')     )
      self.assertIsInstance( user_record['memberOf'],                  type(['a', 'list'])  )
      self.assertIsInstance( user_record['memberOf'][0],               type({'a': 'dict'})  )
      self.assertIsInstance( user_record['memberOf'][0]['inst_id'],    type('a string')     )
      self.assertIsInstance( user_record['memberOf'][0]['inst_name'],  type('a string')     )
      # data values
      self.assertEqual( 'mock_user',                  user_record['username']                  )
      self.assertEqual( 'WelSanIns',                  user_record['memberOf'][0]['inst_id']    )
      self.assertEqual( 'Wellcome Sanger Institute',  user_record['memberOf'][0]['inst_name']  )
      
 
class MonocleDataTest(TestCase):

   test_config = 'dash/tests/mock_data/data_sources.yml'
   with open(test_config, 'r') as file:
      data_sources = yaml.load(file, Loader=yaml.FullLoader)
      mock_url_path  = data_sources['data_download']['url_path']
      mock_web_dir   = data_sources['data_download']['web_dir']
   
   # this is the path to the actual data directory, i.e. the target of the data download symlinks
   mock_inst_view_dir = 'dash/tests/mock_data/monocle_juno_institution_view'
   
   # this has mock values for the environment variables set by docker-compose
   mock_environment = {'DATA_INSTITUTION_VIEW': mock_inst_view_dir}

   # this is the mock date for the instantiation of MonocleData; it must match the latest month used in `expected_progress_data`
   # (because get_progeress() always returns date values up to "now")
   mock_data_updated = datetime(2021,5,15)

   # mock values for patching queries in DataSources modules
   mock_institutions          = [   'Fake institution One',
                                    'Fake institution Two'
                                    ]
   mock_samples               = [   {'sample_id': 'fake_sample_id_1', 'submitting_institution_id': 'Fake institution One'},
                                    {'sample_id': 'fake_sample_id_2', 'submitting_institution_id': 'Fake institution One'},
                                    {'sample_id': 'fake_sample_id_3', 'submitting_institution_id': 'Fake institution Two'},
                                    {'sample_id': 'fake_sample_id_4', 'submitting_institution_id': 'Fake institution Two'}
                                    ]
   mock_seq_status            = {   'fake_sample_id_1': {   'mock data': 'anything', 'creation_datetime': '2019-09-13T08:11:23Z',
                                                            'lanes': [  {  'id': 'fake_lane_id_1',
                                                                           'qc_lib': 1,
                                                                           'qc_seq': 1,
                                                                           'run_status': 'qc complete',
                                                                           'qc_started': 1,
                                                                           'qc_complete_datetime': 'any string will do',
                                                                           }
                                                                        ]
                                                            },
                                    'fake_sample_id_2': {   'mock data': 'anything', 'creation_datetime': '2020-04-29T11:03:35Z',
                                                            'lanes': [  {  'id': 'fake_lane_id_2',
                                                                           'qc_lib': 1,
                                                                           'qc_seq': 1,
                                                                           'run_status': 'qc complete',
                                                                           'qc_started': 1,
                                                                           'qc_complete_datetime': 'any string will do',
                                                                           },
                                                                        {  'id': 'fake_lane_id_3',
                                                                           'qc_lib': 1,
                                                                           'qc_seq': 0,
                                                                           'run_status': 'qc complete',
                                                                           'qc_started': 1,
                                                                           'qc_complete_datetime': 'any string will do',
                                                                           }
                                                                        ]
                                                            },
                                    'fake_sample_id_3': {   'mock data': 'anything', 'creation_datetime': '2020-11-16T16:43:04Z',
                                                            'lanes': [  {  'id': 'fake_lane_id_4',
                                                                           'qc_lib': 1,
                                                                           'qc_seq': 1,
                                                                           'run_status': 'qc complete',
                                                                           'qc_started': 1,
                                                                           'qc_complete_datetime': 'any string will do',
                                                                           }
                                                                        ]
                                                            },
                                    'fake_sample_id_4': {   'mock data': 'anything', 'creation_datetime': '2021-05-02T10:31:49Z',
                                                            'lanes': [  {  'id': 'fake_lane_id_5',
                                                                           'qc_lib': 1,
                                                                           'qc_seq': 1,
                                                                           'run_status': 'qc complete',
                                                                           'qc_started': 1,
                                                                           'qc_complete_datetime': 'any string will do',
                                                                           }
                                                                        ]
                                                            },
                                    }
   mock_metadata              =     [  {  "sanger_sample_id":     {"order": 1, "name": "Sanger_Sample_ID",  "value": "fake_sample_id_1"   },
                                          "some_other_column":    {"order": 2, "name": "Something_Made_Up", "value": ""                   },
                                          "another_fake_column":  {"order": 3, "name": "Also_Made_Up",      "value": "whatevs"            },
                                          "lane_id":              {"order": 4, "name": "Lane_ID",           "value": "fake_lane_id_1"     }
                                          }
                                       ]
   mock_in_silico_data        =     [  {  "lane_id":                 {"order": 1, "name": "Lane_ID",                 "value": "fake_lane_id_1"  },
                                          "some_in_silico_thing":    {"order": 2, "name": "In_Silico_Thing",         "value": "pos"             },
                                          "another_in_silico_thing": {"order": 3, "name": "Another_In_Silico_Thing", "value": "neg"             }
                                          }
                                       ]

   mock_download_host         =     'mock.host'
   mock_download_path         =     'path/incl/mock/download/symlink'
   mock_download_url          =     'https://'+mock_download_host+'/'+mock_download_path
   
   # data we expect MonocleData method to return, given patched queries with the value above
   # the latest month included here must match the date provided by `mock_data_updated`
   expected_progress_data     = {   'date': ['Sep 2019', 'Oct 2019', 'Nov 2019', 'Dec 2019', 'Jan 2020', 'Feb 2020', 'Mar 2020',
                                             'Apr 2020', 'May 2020', 'Jun 2020', 'Jul 2020', 'Aug 2020', 'Sep 2020', 'Oct 2020',
                                             'Nov 2020', 'Dec 2020', 'Jan 2021', 'Feb 2021', 'Mar 2021', 'Apr 2021', 'May 2021'],
                                    'samples received':  [2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 8],
                                    'samples sequenced': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                                    }
   
   expected_institution_data  = {   'FakOne' : {'name': 'Fake institution One', 'db_key': 'Fake institution One'},
                                    'FakTwo' : {'name': 'Fake institution Two', 'db_key': 'Fake institution Two'},
                                    }
   expected_sample_data       = {   'FakOne': [{'sample_id': 'fake_sample_id_1'}, {'sample_id': 'fake_sample_id_2'}],
                                    'FakTwo': [{'sample_id': 'fake_sample_id_3'}, {'sample_id': 'fake_sample_id_4'}]
                                    }
   expected_seq_status        = {   'FakOne': mock_seq_status,
                                    'FakTwo': mock_seq_status
                                    }
   expected_batches           = {   'FakOne': { 'expected': 2, 'received': 4, 'deliveries': [   {'name': 'Batch 1', 'date': '2019-09-13', 'number': 1},
                                                                                                {'name': 'Batch 2', 'date': '2020-04-29', 'number': 1},
                                                                                                {'name': 'Batch 3', 'date': '2020-11-16', 'number': 1},
                                                                                                {'name': 'Batch 4', 'date': '2021-05-02', 'number': 1}
                                                                                                ]
                                                },
                                    'FakTwo': { 'expected': 2, 'received': 4, 'deliveries': [   {'name': 'Batch 1', 'date': '2019-09-13', 'number': 1},
                                                                                                {'name': 'Batch 2', 'date': '2020-04-29', 'number': 1},
                                                                                                {'name': 'Batch 3', 'date': '2020-11-16', 'number': 1},
                                                                                                {'name': 'Batch 4', 'date': '2021-05-02', 'number': 1}
                                                                                                ]
                                                }
                                    }
   expected_seq_summary       =  {  'FakOne': { 'received': 4, 'completed': 5, 'success': 4, 'failed': 1,
                                                'fail_messages': [   {  'lane': 'fake_lane_id_3 (sample fake_sample_id_2)', 'stage': 'sequencing',
                                                                        'issue': 'sorry, failure mesages cannot currently be seen here'
                                                                        }
                                                                     ]
                                                },
                                    'FakTwo': { 'received': 4, 'completed': 5, 'success': 4, 'failed': 1,
                                                'fail_messages': [   {  'lane': 'fake_lane_id_3 (sample fake_sample_id_2)', 'stage': 'sequencing',
                                                                        'issue': 'sorry, failure mesages cannot currently be seen here'
                                                                        }
                                                                     ]
                                                }
                                    }
   expected_pipeline_summary  = {   'FakOne': {'running': 5, 'completed': 0, 'success': 0, 'failed': 0, 'fail_messages': []},
                                    'FakTwo': {'running': 5, 'completed': 0, 'success': 0, 'failed': 0, 'fail_messages': []}
                                    }

   expected_metadata          =  '''"Sanger_Sample_ID","Something_Made_Up","Also_Made_Up","Lane_ID","Download link"
"fake_sample_id_1","","whatevs","fake_lane_id_1","'''+mock_download_url+'/fake_lane_id_1/"'

   expected_metadata_download  = {  'success'   : True,
                                    'filename'  : 'FakeinstitutionOne_sequencing_successful.csv',
                                    'content'   : expected_metadata
                                    }

   expected_metadata_download_reject_missing  = {  'success'   : False ,
                                                   'error'     : 'request'
                                                   }

   expected_metadata_download_error_response  = {  'success'   : False ,
                                                   'error'     : 'internal'
                                                   }
   
   # create MonocleData object outside setUp() to avoid creating multipe instances
   # this means we use cached data rather than making multiple patched queries to SampleMetadata etc.
   monocle_data = MonocleData(set_up=False)
   monocle_data.download_symlink_config = test_config

   def setUp(self):
      # mock moncoledb
      self.monocle_data.sample_metadata = SampleMetadata(set_up=False)
      self.monocle_data.sample_metadata.monocle_client = Monocle_Client(set_up=False)
      self.monocle_data.sample_metadata.monocle_client.set_up(self.test_config)
      self.monocle_data.updated = self.mock_data_updated
      # mock sequencing_status
      self.monocle_data.sequencing_status_source = SequencingStatus(set_up=False)
      self.monocle_data.sequencing_status_source.mlwh_client = MLWH_Client(set_up=False)
      self.monocle_data.sequencing_status_source.mlwh_client.set_up(self.test_config)
      # mock pipeline_status
      self.monocle_data.pipeline_status = PipelineStatus(config=self.test_config)
      # mock metadata_download
      self.monocle_data.metadata_source = MetadataDownload(set_up=False)
      self.monocle_data.metadata_source.dl_client = Monocle_Download_Client(set_up=False)
      self.monocle_data.metadata_source.dl_client.set_up(self.test_config)
      # load mock data
      self.get_mock_data()
      
 
   def test_init(self):
      self.assertIsInstance(self.monocle_data, MonocleData)

   @patch.object(SampleMetadata,    'get_institution_names')
   @patch.object(SampleMetadata,    'get_samples')
   @patch.object(SequencingStatus,  'get_multiple_samples')
   def get_mock_data(self, mock_seq_samples_query, mock_db_sample_query, mock_institution_query):
      mock_institution_query.return_value = self.mock_institutions
      mock_db_sample_query.return_value   = self.mock_samples
      mock_seq_samples_query.return_value = self.mock_seq_status
      self.monocle_data.get_institutions()
      self.monocle_data.get_samples()
      self.monocle_data.get_sequencing_status()
      
   def test_get_progress(self):
      progress_data = self.monocle_data.get_progress()
      self.assertEqual(self.expected_progress_data, progress_data)
      
   def test_get_institutions(self):
      institution_data = self.monocle_data.get_institutions()
      self.assertEqual(self.expected_institution_data, institution_data)
      
   def test_get_samples(self):
      sample_data = self.monocle_data.get_samples()
      self.assertEqual(self.expected_sample_data, sample_data)
      
   def test_get_sequencing_status(self):
      seq_status_data = self.monocle_data.get_sequencing_status()
      self.assertEqual(self.expected_seq_status, seq_status_data)
           
   def test_get_batches(self):
      batches_data = self.monocle_data.get_batches()
      self.assertEqual(self.expected_batches, batches_data)
    
   def test_sequencing_status_summary(self):
      seq_status_summary = self.monocle_data.sequencing_status_summary()
      self.assertEqual(self.expected_seq_summary, seq_status_summary)
      
   def test_pipeline_status_summary(self):
      pipeline_summary = self.monocle_data.pipeline_status_summary()
      self.assertEqual(self.expected_pipeline_summary, pipeline_summary)

   @patch.object(MonocleData,              'make_download_symlink')
   @patch.object(Monocle_Download_Client,  'in_silico_data')
   @patch.object(Monocle_Download_Client,  'metadata')
   def test_get_metadata_for_download(self, mock_metadata_fetch, mock_in_silico_data_fetch, mock_make_symlink):
      mock_metadata_fetch.return_value       = self.mock_metadata
      mock_in_silico_data_fetch.return_value = self.mock_in_silico_data
      mock_make_symlink.return_value         = self.mock_download_path
      metadata_download = self.monocle_data.get_metadata_for_download(self.mock_download_host, self.mock_institutions[0], 'sequencing', 'successful')
      self.assertEqual(self.expected_metadata_download, metadata_download)

   @patch.object(Monocle_Download_Client,  'in_silico_data')
   @patch.object(Monocle_Download_Client,  'metadata')
   def test_get_metadata_for_download_reject_missing_institution(self, mock_metadata_fetch, mock_in_silico_data_fetch):
      mock_metadata_fetch.return_value       = self.mock_metadata
      mock_in_silico_data_fetch.return_value = self.mock_in_silico_data
      metadata_download = self.monocle_data.get_metadata_for_download(self.mock_download_host, 'This Institution Does Not Exist', 'sequencing', 'successful')
      self.assertEqual(self.expected_metadata_download_reject_missing, metadata_download)

   @patch.object(MonocleData,              'make_download_symlink')
   @patch.object(Monocle_Download_Client,  'in_silico_data')
   @patch.object(Monocle_Download_Client,  'metadata')
   def test_get_metadata_for_download_error_response(self, mock_metadata_fetch, mock_in_silico_data_fetch, mock_make_symlink):
      mock_metadata_fetch.return_value       = self.mock_metadata
      mock_in_silico_data_fetch.return_value = self.mock_in_silico_data
      mock_make_symlink.return_value         = None
      metadata_download = self.monocle_data.get_metadata_for_download(self.mock_download_host, self.mock_institutions[0], 'sequencing', 'successful')
      self.assertEqual(self.expected_metadata_download_error_response, metadata_download)

   @patch.object(Monocle_Download_Client,  'in_silico_data')
   @patch.object(Monocle_Download_Client,  'metadata')
   def test_metadata_as_csv(self, mock_metadata_fetch, mock_in_silico_data_fetch):
      mock_metadata_fetch.return_value       = self.mock_metadata
      mock_in_silico_data_fetch.return_value = self.mock_in_silico_data
      metadata_as_csv = self.monocle_data.metadata_as_csv(self.mock_institutions[0], 'sequencing', 'successful', self.mock_download_url)
      self.assertEqual(self.expected_metadata, metadata_as_csv)

   @patch.dict(environ, mock_environment, clear=True)
   def test_make_download_symlink(self):
      test_inst_name = self.mock_institutions[0]
      test_inst_key  = self.monocle_data.institution_db_key_to_dict[test_inst_name]
      self._symlink_test_setup(test_inst_key)
      symlink_url_path  = self.monocle_data.make_download_symlink(test_inst_name)
      symlink_disk_path = symlink_url_path.replace(self.mock_url_path, self.mock_web_dir, 1)
      # test the symlink is actually a symlink, and that it points at the intended target
      self.assertTrue( Path(symlink_disk_path).is_symlink() )
      self.assertEqual( Path(self.mock_inst_view_dir, test_inst_key).absolute(),
                        Path(symlink_disk_path).resolve()
                        )
      self._symlink_test_teardown()

   def _symlink_test_setup(self, mock_inst_key):
      Path(self.mock_inst_view_dir,mock_inst_key).mkdir(parents=True, exist_ok=True)
      Path(self.mock_web_dir).mkdir(parents=True, exist_ok=True)

   def _symlink_test_teardown(self):
      self._rm_minus_r(Path(self.mock_inst_view_dir))
      self._rm_minus_r(Path(self.mock_web_dir))

   def _rm_minus_r(self, this_path: Path):
      for child in this_path.iterdir():
         if child.is_file() or child.is_symlink():
            child.unlink()
         else:
            self._rm_minus_r(child)
      this_path.rmdir()
