from   unittest      import TestCase
from   unittest.mock import patch, Mock
from   copy          import deepcopy
from   datetime      import datetime
import logging
import urllib.request
import urllib.error
from   os            import environ
from   pandas.errors import MergeError
from   pathlib       import Path, PurePath
import yaml

from   DataSources.sample_metadata     import SampleMetadata, Monocle_Client
from   DataSources.sequencing_status   import SequencingStatus, MLWH_Client
from   DataSources.pipeline_status     import PipelineStatus
from   DataSources.metadata_download   import MetadataDownload, Monocle_Download_Client
from   DataSources.user_data           import UserData
from   data_services                   import MonocleUser, MonocleData, DataSourceConfigError, ZIP_COMPRESSION_FACTOR_ASSEMBLIES_ANNOTATIONS
from   utils.file                      import format_file_size

INSTITUTION_KEY = 'GenWel'
PUBLIC_NAME = 'SCN9A'

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

   test_config       = 'dash/tests/mock_data/data_sources.yml'
   test_config_bad   = 'dash/tests/mock_data/data_sources_bad.yml'
   with open(test_config, 'r') as file:
      data_sources   = yaml.load(file, Loader=yaml.FullLoader)
      mock_url_path  = data_sources['data_download']['url_path']
      mock_web_dir   = data_sources['data_download']['web_dir']

   inst_key_batch_date_pairs = [
      {'institution key': 'FakOne', 'batch date': '2020-04-29'},
      {'institution key': 'FakTwo', 'batch date': '2021-05-02'},
      {'institution key': 'FakOne', 'batch date': '1892-01-30'}
   ]
   
   mock_monocle_data_dir = 'dash/tests/mock_data/s3'

   # this is the path to the actual data directory, i.e. the target of the data download symlinks
   mock_inst_view_dir = 'dash/tests/mock_data/monocle_juno_institution_view'
   
   # this has mock values for the environment variables set by docker-compose
   mock_environment = {'MONOCLE_DATA': mock_monocle_data_dir, 'DATA_INSTITUTION_VIEW': mock_inst_view_dir}

   # this is the mock date for the instantiation of MonocleData; it must match the latest month used in `expected_progress_data`
   # (because get_progeress() always returns date values up to "now")
   mock_data_updated = datetime(2021,5,15)

   # mock values for patching queries in DataSources modules
   mock_institutions          = [   'Fake institution One',
                                    'Fake institution Two'
                                    ]
   mock_samples               = [   {'sample_id': 'fake_sample_id_1', 'submitting_institution_id': 'Fake institution One', 'public_name': f'{PUBLIC_NAME}_1'},
                                    {'sample_id': 'fake_sample_id_2', 'submitting_institution_id': 'Fake institution One', 'public_name': f'{PUBLIC_NAME}_2'},
                                    {'sample_id': 'fake_sample_id_3', 'submitting_institution_id': 'Fake institution Two', 'public_name': f'{PUBLIC_NAME}_3'},
                                    {'sample_id': 'fake_sample_id_4', 'submitting_institution_id': 'Fake institution Two', 'public_name': f'{PUBLIC_NAME}_4'}
                                    ]
   mock_seq_status            = {   '_ERROR': None,
                                    'fake_sample_id_1': {   'mock data': 'anything', 'creation_datetime': '2020-04-29T11:03:35Z',
                                                            'lanes': [  {  'id': 'fake_lane_id_1',
                                                                           'qc_lib': 1,
                                                                           'qc_seq': 1,
                                                                           'run_status': 'qc complete',
                                                                           'qc_started': 1,
                                                                           'qc_complete_datetime': 'any string will do',
                                                                           },
                                                                        {  'id': 'fake_lane_id_2',
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
                                    'fake_sample_id_2': {   'mock data': 'anything', 'creation_datetime': '2020-11-16T16:43:04Z',
                                                            'lanes': [  {  'id': 'fake_lane_id_4',
                                                                           'qc_lib': 1,
                                                                           'qc_seq': 1,
                                                                           'run_status': 'qc complete',
                                                                           'qc_started': 1,
                                                                           'qc_complete_datetime': 'any string will do',
                                                                           }
                                                                        ]
                                                            },
                                    'fake_sample_id_3': {   'mock data': 'anything', 'creation_datetime': '2021-05-02T10:31:49Z',
                                                            'lanes': [  {  'id': 'fake_lane_id_5',
                                                                           'qc_lib': 1,
                                                                           'qc_seq': 1,
                                                                           'run_status': 'qc complete',
                                                                           'qc_started': 1,
                                                                           'qc_complete_datetime': 'any string will do',
                                                                           }
                                                                        ]
                                                            },
                                    'fake_sample_id_4': {   'mock data': 'anything', 'creation_datetime': '2021-05-02T14:07:23Z',
                                                            'lanes': [  {  'id': 'fake_lane_id_6',
                                                                           'qc_lib': 1,
                                                                           'qc_seq': 1,
                                                                           'run_status': 'qc complete',
                                                                           'qc_started': 1,
                                                                           'qc_complete_datetime': 'any string will do',
                                                                           }
                                                                        ]
                                                            },
                                    }

   mock_filtered_samples      = [   {  'creation_datetime': '2020-04-29T11:03:35Z',
                                       'lanes': ['fake_lane_id_1', 'fake_lane_id_2', 'fake_lane_id_3'],
                                       'sample_id': 'fake_sample_id_1',
                                       'inst_key': 'FakOne',
                                       'public_name': 'SCN9A_1'
                                       },
                                    {  'creation_datetime': '2021-05-02T10:31:49Z',
                                       'lanes': ['fake_lane_id_5'],
                                       'sample_id': 'fake_sample_id_3',
                                       'inst_key': 'FakTwo',
                                       'public_name': 'SCN9A_3'
                                       },
                                    {  'creation_datetime': '2021-05-02T14:07:23Z',
                                       'lanes': ['fake_lane_id_6'],
                                       'sample_id': 'fake_sample_id_4',
                                       'inst_key': 'FakTwo',
                                       'public_name': 'SCN9A_4'
                                       }
                                    ]
   
   mock_metadata              =     [  {  "sanger_sample_id":     {"order": 1, "name": "Sanger_Sample_ID",  "value": "fake_sample_id_1"   },
                                          "some_other_column":    {"order": 2, "name": "Something_Made_Up", "value": ""                   },
                                          # note use of `None`, which should end up in CSV as ""
                                          "another_fake_column":  {"order": 3, "name": "Also_Made_Up",      "value": None                 },
                                          "lane_id":              {"order": 4, "name": "Lane_ID",           "value": "fake_lane_id_1"     },
                                          "public_name":          {"order": 5, "name": "Public_Name",       "value": "fake_public_name_1" }
                                          },
                                       {  "sanger_sample_id":     {"order": 1, "name": "Sanger_Sample_ID",  "value": "fake_sample_id_2"   },
                                          "some_other_column":    {"order": 2, "name": "Something_Made_Up", "value": ""                   },
                                          "another_fake_column":  {"order": 3, "name": "Also_Made_Up",      "value": "whatevs"            },
                                          "lane_id":              {"order": 4, "name": "Lane_ID",           "value": "fake_lane_id_2"     },
                                          "public_name":          {"order": 5, "name": "Public_Name",       "value": "fake public name 2" }
                                          }
                                       ]
   mock_in_silico_data        =     [  {  "lane_id":                 {"order": 1, "name": "Sample_id",               "value": "fake_lane_id_3"  },
                                          "some_in_silico_thing":    {"order": 2, "name": "In_Silico_Thing",         "value": "pos"             },
                                          "another_in_silico_thing": {"order": 3, "name": "Another_In_Silico_Thing", "value": "neg"             }
                                          }
                                       ]
   # the return value when no in silico data are available
   in_silico_data_available_not_available =  []
   # this contains a bad lane ID, so it should be ignored and *not* merged into the metadata download
   mock_in_silico_data_bad_lane_id        =  [  {  "lane_id":                 {"order": 1, "name": "Sample_id",               "value": "this_is_a_bad_id"},
                                                   "some_in_silico_thing":    {"order": 2, "name": "In_Silico_Thing",         "value": "pos"             },
                                                   "another_in_silico_thing": {"order": 3, "name": "Another_In_Silico_Thing", "value": "neg"             }
                                                   },
                                                {  "lane_id":                 {"order": 1, "name": "Sample_id",               "value": "fake_lane_id_2"  },
                                                   "some_in_silico_thing":    {"order": 2, "name": "In_Silico_Thing",         "value": "pos"             },
                                                   "another_in_silico_thing": {"order": 3, "name": "Another_In_Silico_Thing", "value": "neg"             }
                                                   }
                                             ]

   mock_combined_metadata                    =  { "samples":   [  {  "metadata":    mock_metadata[0]
                                                                     },
                                                                  {  "metadata":    mock_metadata[1],
                                                                     }
                                                                  ],
                                                   "total":    3,
                                                   "last":     3
                                                   }
   mock_combined_metadata_plus_in_silico     =  { "samples":   [  {  "metadata":    mock_metadata[0],
                                                                  "in silico":      mock_in_silico_data[0]
                                                                  },
                                                               {  "metadata":       mock_metadata[1],
                                                                  }
                                                               ],
                                                   "total":    3,
                                                   "last":     3
                                                   }
   mock_combined_metadata_filtered           =  { "samples":   [  {  "metadata":    {"public_name": mock_metadata[0]["public_name"]}
                                                                     },
                                                                  {  "metadata":    {"public_name": mock_metadata[1]["public_name"]}
                                                                     }
                                                                  ],
                                                   "total":    3,
                                                   "last":     3
                                                   }
   mock_combined_metadata_in_silico_filtered =  { "samples":   [  {  "metadata":    {"public_name": mock_metadata[0]["public_name"]},
                                                                     "in silico":   {"some_in_silico_thing": mock_in_silico_data[0]["some_in_silico_thing"]}
                                                                     },
                                                                  {  "metadata":    {"public_name": mock_metadata[1]["public_name"]}
                                                                     }
                                                                  ],
                                                   "total":    3,
                                                   "last":     3
                                                   }

   # these are invalid because the lane ID appears twice:  pandas merge should catch this in validation
   mock_invalid_metadata      =     [  mock_metadata[0], mock_metadata[1], mock_metadata[0] ]
   mock_invalid_in_silico_data =    [  mock_in_silico_data[0], mock_in_silico_data[0] ]

   mock_download_host         =     'mock.host'
   mock_download_path         =     'path/incl/mock/download/symlink'
   mock_download_url          =     'https://'+mock_download_host+'/'+mock_download_path
   
   # data we expect MonocleData method to return, given patched queries with the value above
   # the latest month included here must match the date provided by `mock_data_updated`
   expected_progress_data     =  {  'date': ['Sep 2019', 'Oct 2019', 'Nov 2019', 'Dec 2019', 'Jan 2020', 'Feb 2020', 'Mar 2020',
                                             'Apr 2020', 'May 2020', 'Jun 2020', 'Jul 2020', 'Aug 2020', 'Sep 2020', 'Oct 2020',
                                             'Nov 2020', 'Dec 2020', 'Jan 2021', 'Feb 2021', 'Mar 2021', 'Apr 2021', 'May 2021'],
                                    'samples received':  [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 8],
                                    'samples sequenced': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                                    }                                                                                                                       
   
   expected_institution_data  = {   'FakOne' : {'name': 'Fake institution One', 'db_key': 'Fake institution One'},
                                    'FakTwo' : {'name': 'Fake institution Two', 'db_key': 'Fake institution Two'},
                                    }

   expected_dropout_data      = { 'FakOne' : { '_ERROR': 'Server Error: Records cannot be collected at this time. Please try again later.' },
                                  'FakTwo' : { '_ERROR': 'Server Error: Records cannot be collected at this time. Please try again later.' }
                                    }

   expected_sample_data       = {   'FakOne': [{'sample_id': 'fake_sample_id_1', 'public_name': f'{PUBLIC_NAME}_1'}, {'sample_id': 'fake_sample_id_2', 'public_name': f'{PUBLIC_NAME}_2'}],
                                    'FakTwo': [{'sample_id': 'fake_sample_id_3', 'public_name': f'{PUBLIC_NAME}_3'}, {'sample_id': 'fake_sample_id_4', 'public_name': f'{PUBLIC_NAME}_4'}]
                                    }
   expected_seq_status        = {   'FakOne': mock_seq_status,
                                    'FakTwo': mock_seq_status
                                    }
   expected_batches           = {   'FakOne': { '_ERROR': None, 'expected': 2, 'received': 4, 'deliveries':  [ {'name': 'Batch 1', 'date': '2020-04-29', 'number': 1},
                                                                                                {'name': 'Batch 2', 'date': '2020-11-16', 'number': 1},
                                                                                                {'name': 'Batch 3', 'date': '2021-05-02', 'number': 2}
                                                                                                ]
                                                },
                                    'FakTwo': { '_ERROR': None, 'expected': 2, 'received': 4, 'deliveries':   [  {'name': 'Batch 1', 'date': '2020-04-29', 'number': 1},
                                                                                                {'name': 'Batch 2', 'date': '2020-11-16', 'number': 1},
                                                                                                {'name': 'Batch 3', 'date': '2021-05-02', 'number': 2}
                                                                                                ]
                                                }
                                    }
   expected_seq_summary       =  {  'FakOne': { '_ERROR': None, 'received': 4, 'completed': 6, 'success': 5, 'failed': 1,
                                                'fail_messages': [  {   'lane': 'fake_lane_id_3 (sample fake_sample_id_1)', 'stage': 'sequencing',
                                                                        'issue': 'sorry, failure mesages cannot currently be seen here'
                                                                        }
                                                                     ]
                                                },
                                    'FakTwo': { '_ERROR': None, 'received': 4, 'completed': 6, 'success': 5, 'failed': 1,
                                                'fail_messages': [   {  'lane': 'fake_lane_id_3 (sample fake_sample_id_1)', 'stage': 'sequencing',
                                                                        'issue': 'sorry, failure mesages cannot currently be seen here'
                                                                        }
                                                                     ]
                                                }
                                    }
   expected_pipeline_summary  = {   'FakOne': {'_ERROR': None, 'running': 6, 'completed': 0, 'success': 0, 'failed': 0, 'fail_messages': []},
                                    'FakTwo': {'_ERROR': None, 'running': 6, 'completed': 0, 'success': 0, 'failed': 0, 'fail_messages': []}
                                    }

   expected_metadata          = '''"Public_Name","Sanger_Sample_ID","Something_Made_Up","Also_Made_Up","Lane_ID","In_Silico_Thing","Another_In_Silico_Thing","Download_Link"
"fake_public_name_1","fake_sample_id_1","","","fake_lane_id_1 fake_lane_id_2","","","'''+mock_download_url+'''/fake_public_name_1"
"fake public name 2","fake_sample_id_2","","whatevs","fake_lane_id_4","","","'''+mock_download_url+'''/fake%20public%20name%202"
'''

   expected_metadata_when_no_in_silico_data = '''"Public_Name","Sanger_Sample_ID","Something_Made_Up","Also_Made_Up","Lane_ID","Download_Link"
"fake_public_name_1","fake_sample_id_1","","","fake_lane_id_1 fake_lane_id_2","'''+mock_download_url+'''/fake_public_name_1"
"fake public name 2","fake_sample_id_2","","whatevs","fake_lane_id_4","'''+mock_download_url+'''/fake%20public%20name%202"
'''

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
   monocle_data.data_source_config_name = test_config

   @patch.dict(environ, mock_environment, clear=True)
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
   def get_mock_data(self,
         mock_seq_samples_query,
         mock_db_sample_query,
         mock_institution_query
      ):
      self.monocle_data.sequencing_status_data = None
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

   def test_get_institution_names(self):
      institution_names = self.monocle_data.get_institution_names()

      self.assertEqual(self.mock_institutions, institution_names)

   def test_get_institution_names_returns_cached_response(self):
      expected = 'some data'
      self.monocle_data.institution_names = expected

      institution_names = self.monocle_data.get_institution_names()

      self.assertEqual(expected, institution_names)
      # Teardown: clear cache.
      self.monocle_data.institution_names = None

   def test_get_institution_names_returns_names_from_user_membership(self):
      expected_institution_name = 'Center of Paradise Engineering'
      user_record = { 'memberOf': [{ 'inst_name': expected_institution_name }] }
      self.monocle_data.user_record = user_record

      institution_names = self.monocle_data.get_institution_names()

      self.assertEqual([expected_institution_name], institution_names)
      # Teardown: clear user record.
      self.monocle_data.user_record = None
      
   def test_get_samples(self):
      sample_data = self.monocle_data.get_samples()

      self.assertEqual(self.expected_sample_data, sample_data)
      
   def test_get_sequencing_status(self):
      seq_status_data = self.monocle_data.get_sequencing_status()

      self.assertEqual(self.expected_seq_status, seq_status_data)

   @patch.object(SampleMetadata, 'get_institution_names')
   @patch.object(SampleMetadata, 'get_samples')
   @patch.object(SequencingStatus, 'get_multiple_samples')
   def test_get_sequencing_status_droppout(self, get_multiple_samples_mock, mock_db_sample_query, mock_institution_query):
       mock_institution_query.return_value = self.mock_institutions
       mock_db_sample_query.return_value = self.mock_samples
       get_multiple_samples_mock.side_effect = urllib.error.HTTPError('/nowhere', '404', 'page could not be found', 'yes', 'no')
       self.monocle_data.sequencing_status_data = None

       httpdropout = self.monocle_data.get_sequencing_status()

       self.assertEqual(self.expected_dropout_data, httpdropout)

   def test_get_batches(self):
      batches_data = self.monocle_data.get_batches()

      self.assertEqual(self.expected_batches, batches_data)

   @patch.object(SequencingStatus, 'get_multiple_samples')
   def test_get_batches_dropouts(self, get_multiple_samples_mock):
      get_multiple_samples_mock.side_effect = urllib.error.HTTPError('/nowhere', '404', 'page could not be found',
                                                                      'yes', 'no')
      self.monocle_data.sequencing_status_data = None
      self.monocle_data.get_sequencing_status()

      batches_data = self.monocle_data.get_batches()

      self.assertEqual(self.expected_dropout_data, batches_data)

   def test_sequencing_status_summary(self):
      seq_status_summary = self.monocle_data.sequencing_status_summary()
      # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.expected_seq_summary, seq_status_summary))

      self.assertEqual(self.expected_seq_summary, seq_status_summary)

   def test_sequencing_status_summary_dropout(self):
      self.monocle_data.sequencing_status_data = self.expected_dropout_data

      seq_status_summary = self.monocle_data.sequencing_status_summary()

      # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.expected_seq_summary, seq_status_summary))
      self.assertEqual(self.expected_dropout_data, seq_status_summary)
     
   def test_pipeline_status_summary(self):
      pipeline_summary = self.monocle_data.pipeline_status_summary()
      # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.expected_pipeline_summary, pipeline_summary))

      self.assertEqual(self.expected_pipeline_summary, pipeline_summary)

   def test_pipeline_status_summary_dropout(self):
      self.monocle_data.sequencing_status_data = self.expected_dropout_data

      pipeline_summary = self.monocle_data.pipeline_status_summary()

      # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.expected_pipeline_summary, pipeline_summary))
      self.assertEqual(self.expected_dropout_data, pipeline_summary)

   @patch.object(Path,           'exists', return_value=True)
   @patch.object(MonocleData,    '_get_file_size')
   @patch.object(SampleMetadata, 'get_samples')
   @patch.dict(environ, mock_environment, clear=True)
   def test_get_bulk_download_info(self, get_sample_metadata_mock, get_file_size_mock, _path_exists_mock):
      get_sample_metadata_mock.return_value = self.mock_samples
      file_size = 420024
      get_file_size_mock.return_value = file_size

      bulk_download_info = self.monocle_data.get_bulk_download_info(
         {'batches': self.inst_key_batch_date_pairs}, assemblies=True, annotations=False)

      expected_num_samples = len(self.inst_key_batch_date_pairs)
      num_lanes = 5
      expected_byte_size = file_size * num_lanes
      self.assertEqual({
         'num_samples': expected_num_samples,
         'size': format_file_size(expected_byte_size),
         'size_zipped': format_file_size(expected_byte_size / ZIP_COMPRESSION_FACTOR_ASSEMBLIES_ANNOTATIONS)
      }, bulk_download_info)
      
   @patch.object(Monocle_Download_Client,  'metadata')
   def test_get_metadata(self, mock_metadata_fetch):
      """
      data_services.MonocleData.get_metadata should return sample metadta in expected format,
      without in silico data when `include_in_silico=False` is passed; and should default to
      the same if `include_in_silico` is not defined
      """
      mock_metadata_fetch.return_value = self.mock_metadata
      filtered_samples_metadata = self.monocle_data.get_metadata({'batches': self.inst_key_batch_date_pairs},include_in_silico=False)
      #logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata, filtered_samples_metadata))
      self.assertEqual(self.mock_combined_metadata, filtered_samples_metadata)
      filtered_samples_metadata = self.monocle_data.get_metadata({'batches': self.inst_key_batch_date_pairs})
      #logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata, filtered_samples_metadata))
      self.assertEqual(self.mock_combined_metadata, filtered_samples_metadata)

   @patch.object(Monocle_Download_Client,  'in_silico_data')
   @patch.object(Monocle_Download_Client,  'metadata')
   def test_get_metadata_plus_in_silico(self, mock_metadata_fetch, mock_in_silico_data_fetch):
      """
      data_services.MonocleData.get_metadata should return sample metadta in expected format,
      with added in silico data when `include_in_silico=True` is passed
      """
      mock_metadata_fetch.return_value       = self.mock_metadata
      mock_in_silico_data_fetch.return_value = self.mock_in_silico_data
      filtered_samples_metadata = self.monocle_data.get_metadata({'batches': self.inst_key_batch_date_pairs},include_in_silico=True)
      #logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata_plus_in_silico, filtered_samples_metadata))
      self.assertEqual(self.mock_combined_metadata_plus_in_silico, filtered_samples_metadata)
      
   @patch.object(Monocle_Download_Client,  'metadata')
   def test_get_metadata_filtered_columns(self, mock_metadata_fetch):
      """
      data_services.MonocleData.get_metadata should filter the response to include
      only the requested columns
      """
      mock_metadata_fetch.return_value = deepcopy(self.mock_metadata) # work on a copy, as metadata will be modified
      filtered_samples_metadata = self.monocle_data.get_metadata( {'batches': self.inst_key_batch_date_pairs},
                                                                  metadata_columns=['public_name'])
      #logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata_filtered, filtered_samples_metadata))
      self.assertEqual(self.mock_combined_metadata_filtered, filtered_samples_metadata)
      
   @patch.object(MonocleData, 'get_filtered_samples')
   def test_get_metadata_no_matching_samples(self, mock_get_filtered_samples):
      """
      data_services.MonocleData.get_metadata should gracefully handle a case of the filters
      matching zero samples, by just returning an empty response
      """
      mock_get_filtered_samples.return_value = []
      filtered_samples_metadata = self.monocle_data.get_metadata({'batches': self.inst_key_batch_date_pairs})
      #logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata, filtered_samples_metadata))
      self.assertEqual({'last':0, 'total':0, 'samples':{'metadata':[]}}, filtered_samples_metadata)
      filtered_samples_metadata_plus_in_silico = self.monocle_data.get_metadata({'batches': self.inst_key_batch_date_pairs},include_in_silico=True)
      #logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata, filtered_samples_metadata))
      self.assertEqual({'last':0, 'total':0, 'samples':{'metadata':[], 'in silico':[]}}, filtered_samples_metadata_plus_in_silico)

   @patch.object(Monocle_Download_Client,  'in_silico_data')
   @patch.object(Monocle_Download_Client,  'metadata')
   def test_get_metadata_start_row_out_of_range_ok(self, mock_metadata_fetch, mock_in_silico_data_fetch):
      """
      data_services.MonocleData.get_metadata should gracefully handle a start_row parameter that
      "points" to a row beyond the total number of rows, by just returning an empty response
      """
      mock_metadata_fetch.return_value       = self.mock_metadata
      mock_in_silico_data_fetch.return_value = self.mock_in_silico_data
      filtered_samples_metadata = self.monocle_data.get_metadata({'batches': self.inst_key_batch_date_pairs}, start_row=9999, num_rows=1)
      #logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata, filtered_samples_metadata))
      self.assertEqual({'last':0, 'total':0, 'samples':{'metadata':[]}}, filtered_samples_metadata)
      filtered_samples_metadata_plus_in_silico = self.monocle_data.get_metadata({'batches': self.inst_key_batch_date_pairs},include_in_silico=True, start_row=9999, num_rows=1)
      #logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata, filtered_samples_metadata))
      self.assertEqual({'last':0, 'total':0, 'samples':{'metadata':[], 'in silico':[]}}, filtered_samples_metadata_plus_in_silico)
         
   @patch.object(Monocle_Download_Client,  'metadata')
   def test_get_metadata_num_rows_out_of_range_ok(self, mock_metadata_fetch):
      """
      data_services.MonocleData.get_metadata should gracefully handle num_rows parameter that
      "points" to a row beyond the total number of rows, by just returning all available rows
      """
      mock_metadata_fetch.return_value = self.mock_metadata
      filtered_samples_metadata = self.monocle_data.get_metadata({'batches': self.inst_key_batch_date_pairs}, start_row=1, num_rows=9999)
      #logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata, filtered_samples_metadata))
      self.assertEqual(self.mock_combined_metadata, filtered_samples_metadata)

   def test_get_metadata_pagination_reject_missing_num_rows(self):
      """
      data_services.MonocleData.get_metadata should raise AssertionError if only
      one pagination param start_row is passwd with a num_rows param
      (note if start_row is not defined, num_rows is simply ignored)
      """
      with self.assertRaises(AssertionError):
         filtered_samples_metadata = self.monocle_data.get_metadata( {'batches': self.inst_key_batch_date_pairs},
                                                                     metadata_columns=['public_name'],
                                                                     start_row=2)
         
   @patch.object(Monocle_Download_Client,  'in_silico_data')
   @patch.object(Monocle_Download_Client,  'metadata')
   def test_get_metadata_plus_in_silico_filtered_columns(self, mock_metadata_fetch, mock_in_silico_data_fetch):
      mock_metadata_fetch.return_value       = deepcopy(self.mock_metadata) # work on a copy, as metadata will be modified
      mock_in_silico_data_fetch.return_value = deepcopy(self.mock_in_silico_data) # work on a copy, as metadata will be modified
      filtered_samples_metadata = self.monocle_data.get_metadata( {'batches': self.inst_key_batch_date_pairs},
                                                                  metadata_columns=['public_name'],
                                                                  in_silico_columns=["some_in_silico_thing"],
                                                                  include_in_silico=True)
      #logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.mock_combined_metadata_in_silico_filtered, filtered_samples_metadata))
      self.assertEqual(self.mock_combined_metadata_in_silico_filtered, filtered_samples_metadata)

   @patch.object(SampleMetadata, 'get_samples')
   def test_get_filtered_samples(self, get_sample_metadata_mock):
      get_sample_metadata_mock.return_value = self.mock_samples

      actual_samples = self.monocle_data.get_filtered_samples({'batches': self.inst_key_batch_date_pairs})

      expected_samples = self.mock_filtered_samples
      #logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(expected_samples, actual_samples))
      self.assertEqual(expected_samples, actual_samples)

   def test_get_filtered_samples_accepts_empty_list(self):
      samples = self.monocle_data.get_filtered_samples({'batches':[]})

      self.assertEqual([], samples)

   @patch.object(SampleMetadata, 'get_samples')
   def test_get_filtered_samples_ignores_institution_keys_that_are_not_in_seq_status_data(self, get_sample_metadata_mock):
      get_sample_metadata_mock.return_value = self.mock_samples
      inst_key_batch_date_pairs = deepcopy(self.inst_key_batch_date_pairs)
      inst_key_batch_date_pairs.append({'institution key': 'nonExistentInst', 'batch date': '2021-01-27'})

      actual_samples = self.monocle_data.get_filtered_samples({'batches': inst_key_batch_date_pairs})

      expected_samples = self.mock_filtered_samples
      self.assertEqual(expected_samples, actual_samples)

   @patch.object(Path, 'exists', return_value=True)
   @patch.dict(environ, mock_environment, clear=True)
   def test_get_public_name_to_lane_files_dict(self, _path_exists_mock):
      samples = self.mock_seq_status.values()
      for sample in samples:
         if not sample:
            continue
         sample['inst_key'] = INSTITUTION_KEY
         sample['public_name'] = PUBLIC_NAME

      public_name_to_lane_files = self.monocle_data.get_public_name_to_lane_files_dict(
         samples, assemblies=True, annotations=False)

      expected_lane_files = [
         PurePath(self.mock_inst_view_dir, INSTITUTION_KEY, PUBLIC_NAME, f'{lane}.contigs_spades.fa')
         for sample in samples if sample
         for lane in sample['lanes']]
      expected = {PUBLIC_NAME: expected_lane_files}
      self.assertEqual(expected, public_name_to_lane_files)

   @patch.object(Path, 'exists', return_value=False)
   @patch.dict(environ, mock_environment, clear=True)
   def test_get_public_name_to_lane_files_dict_ignores_non_existent_files(self, _path_exists_mock):
      samples = self.mock_seq_status.values()
      for sample in samples:
         if not sample:
            continue
         sample['inst_key'] = INSTITUTION_KEY
         sample['public_name'] = PUBLIC_NAME

      public_name_to_lane_files = self.monocle_data.get_public_name_to_lane_files_dict(
         samples, assemblies=True, annotations=False)

      self.assertEqual({}, public_name_to_lane_files)

   def test_get_public_name_to_lane_files_dict_rejects_if_data_institution_view_env_var_is_not_set(self):
      samples = list( self.mock_seq_status.values() )

      with self.assertRaises(DataSourceConfigError):
         self.monocle_data.get_public_name_to_lane_files_dict(
            samples, assemblies=True, annotations=False)

   @patch.dict(environ, mock_environment, clear=True)
   def test_get_zip_download_location(self):
      download_location = self.monocle_data.get_zip_download_location()

      self.assertEqual(PurePath(self.mock_inst_view_dir, 'downloads'), download_location)

   @patch.dict(environ, mock_environment, clear=True)
   def test_get_zip_download_location_raises_if_data_inst_view_is_not_in_environ(self):
      del environ['DATA_INSTITUTION_VIEW']

      with self.assertRaises(DataSourceConfigError):
         self.monocle_data.get_zip_download_location()

   def test_get_zip_download_location_raises_if_data_config_is_corrupt(self):
      monocle_data_with_bad_config = MonocleData(set_up=False)
      monocle_data_with_bad_config.data_source_config_name = self.test_config_bad

      with self.assertRaises(DataSourceConfigError):
         monocle_data_with_bad_config.get_zip_download_location()

   @patch.object(MonocleData,              'make_download_symlink')
   @patch.object(Monocle_Download_Client,  'in_silico_data')
   @patch.object(Monocle_Download_Client,  'metadata')
   def test_get_metadata_for_download(self, mock_metadata_fetch, mock_in_silico_data_fetch, mock_make_symlink):
      mock_metadata_fetch.return_value       = self.mock_metadata
      mock_in_silico_data_fetch.return_value = self.mock_in_silico_data
      mock_make_symlink.return_value         = self.mock_download_path

      metadata_download = self.monocle_data.get_metadata_for_download(self.mock_download_host, self.mock_institutions[0], 'sequencing', 'successful')

      # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.expected_metadata_download, metadata_download))
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

   @patch.object(Monocle_Download_Client, 'in_silico_data')
   @patch.object(Monocle_Download_Client, 'metadata')
   def test_metadata_as_csv(self, mock_metadata_fetch, mock_in_silico_data_fetch):
       mock_metadata_fetch.return_value = self.mock_metadata
       mock_in_silico_data_fetch.return_value = self.mock_in_silico_data

       metadata_as_csv = self.monocle_data.metadata_as_csv(self.mock_institutions[0], 'sequencing', 'successful',
                                                           self.mock_download_url)

       self.assertEqual(self.expected_metadata, metadata_as_csv)

   @patch.object(Monocle_Download_Client,  'in_silico_data')
   @patch.object(Monocle_Download_Client,  'metadata')
   def test_metadata_as_csv_when_no_in_silico_data_available(self, mock_metadata_fetch, mock_in_silico_data_fetch):
      mock_metadata_fetch.return_value       = self.mock_metadata
      mock_in_silico_data_fetch.return_value = self.in_silico_data_available_not_available

      metadata_as_csv = self.monocle_data.metadata_as_csv(self.mock_institutions[0], 'sequencing', 'successful', self.mock_download_url)

      self.assertEqual(self.expected_metadata_when_no_in_silico_data, metadata_as_csv)

   @patch.object(Monocle_Download_Client,  'in_silico_data')
   @patch.object(Monocle_Download_Client,  'metadata')
   def test_metadata_as_csv_when_in_silico_data_has_bad_lane_id(self, mock_metadata_fetch, mock_in_silico_data_fetch):
      mock_metadata_fetch.return_value       = self.mock_metadata
      mock_in_silico_data_fetch.return_value = self.mock_in_silico_data_bad_lane_id

      metadata_as_csv = self.monocle_data.metadata_as_csv(self.mock_institutions[0], 'sequencing', 'successful', self.mock_download_url)
      #logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.expected_metadata, metadata_as_csv))

      self.assertEqual(self.expected_metadata, metadata_as_csv)

   @patch.object(Monocle_Download_Client,  'in_silico_data')
   @patch.object(Monocle_Download_Client,  'metadata')
   def test_metadata_as_csv_invalid_metadata_merge_fails(self, mock_metadata_fetch, mock_in_silico_data_fetch):
      mock_metadata_fetch.return_value       = self.mock_invalid_metadata
      mock_in_silico_data_fetch.return_value = self.mock_in_silico_data

      with self.assertRaises(MergeError):
         self.monocle_data.metadata_as_csv(self.mock_institutions[0], 'sequencing', 'successful', self.mock_download_url)

   @patch.object(Monocle_Download_Client,  'in_silico_data')
   @patch.object(Monocle_Download_Client,  'metadata')
   def test_metadata_as_csv_invalid_in_silico_merge_fails(self, mock_metadata_fetch, mock_in_silico_data_fetch):
      mock_metadata_fetch.return_value       = self.mock_metadata
      mock_in_silico_data_fetch.return_value = self.mock_invalid_in_silico_data

      with self.assertRaises(MergeError):
         self.monocle_data.metadata_as_csv(self.mock_institutions[0], 'sequencing', 'successful', self.mock_download_url)

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

   @patch.dict(environ, mock_environment, clear=True)
   def test_make_download_symlink_cross_institution(self):
      cross_institution_dir = 'downloads'
      self._symlink_test_setup(cross_institution_dir)

      symlink_url_path  = self.monocle_data.make_download_symlink(cross_institution=True)

      symlink_disk_path = symlink_url_path.replace(self.mock_url_path, self.mock_web_dir, 1)
      # test the symlink is actually a symlink, and that it points at the intended target
      self.assertTrue( Path(symlink_disk_path).is_symlink() )
      self.assertEqual( Path(self.mock_inst_view_dir, cross_institution_dir).absolute(),
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
