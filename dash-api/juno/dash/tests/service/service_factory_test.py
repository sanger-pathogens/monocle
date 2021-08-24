import unittest
from unittest import TestCase
from unittest.mock import patch
from datetime import datetime

from DataSources.sample_metadata import SampleMetadata, Monocle_Client
from DataSources.sequencing_status import SequencingStatus, MLWH_Client
from DataSources.pipeline_status import PipelineStatus
from DataSources.metadata_download import MetadataDownload, Monocle_Download_Client
from DataSources.user_data import UserData

from dash.api.service.service_factory import ServiceFactory, DataService, UserService, TestDataService


class MonocleUserTest(TestCase):
    test_config = 'dash/tests/mock_data/data_sources.yml'
    mock_ldap_result_user = ('cn=mock_user_sanger_ac_uk,ou=users,dc=monocle,dc=pam,dc=sanger,dc=ac,dc=uk',
                             {'cn': [b'mock_user_sanger_ac_uk'],
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
    mock_ldap_result_group = ('cn=WelSanIns,ou=groups,dc=monocle,dc=dev,dc=pam,dc=sanger,dc=ac,dc=uk',
                              {'cn': [b'WelSanIns'],
                               'description': [b'Wellcome Sanger Institute'],
                               'gidNumber': [b'501'],
                               'objectClass': [b'posixGroup', b'top']
                               }
                              )

    def setUp(self):
        self.user = UserService(set_up=False)
        self.user.user_data.set_up(self.test_config)

    def test_init(self):
        self.assertIsInstance(self.user, UserService)

    @patch.object(UserData, 'ldap_search_group_by_gid')
    @patch.object(UserData, 'ldap_search_user_by_username')
    def test_load_user_record(self, mock_user_query, mock_group_query):
        mock_user_query.return_value = self.mock_ldap_result_user
        mock_group_query.return_value = self.mock_ldap_result_group
        user_record = self.user.load_user_record('mock_user')
        self.assertIsInstance(user_record, type({'a': 'dict'}))
        self.assertIsInstance(user_record, type({'a': 'dict'}))
        self.assertIsInstance(user_record['username'], type('a string'))
        self.assertIsInstance(user_record['memberOf'], type(['a', 'list']))
        self.assertIsInstance(user_record['memberOf'][0], type({'a': 'dict'}))
        self.assertIsInstance(user_record['memberOf'][0]['inst_id'], type('a string'))
        self.assertIsInstance(user_record['memberOf'][0]['inst_name'], type('a string'))
        # data values
        self.assertEqual('mock_user', user_record['username'])
        self.assertEqual('WelSanIns', user_record['memberOf'][0]['inst_id'])
        self.assertEqual('Wellcome Sanger Institute', user_record['memberOf'][0]['inst_name'])


class MonocleDataTest(TestCase):
    test_config = 'dash/tests/mock_data/data_sources.yml'

    # this is the mock date for the instantiation of DataService; it must match the latest month used in `expected_progress_data`
    # (because get_progeress() always returns date values up to "now")
    mock_data_updated = datetime(2021, 5, 15)

    # mock values for patching queries in DataSources modules
    mock_institutions = ['Fake institution One',
                         'Fake institution Two'
                         ]
    mock_samples = [{'sample_id': 'fake_sample_id_1', 'submitting_institution_id': 'Fake institution One'},
                    {'sample_id': 'fake_sample_id_2', 'submitting_institution_id': 'Fake institution One'},
                    {'sample_id': 'fake_sample_id_3', 'submitting_institution_id': 'Fake institution Two'},
                    {'sample_id': 'fake_sample_id_4', 'submitting_institution_id': 'Fake institution Two'}
                    ]
    mock_seq_status = {'fake_sample_id_1': {'mock data': 'anything', 'creation_datetime': '2019-09-13T08:11:23Z',
                                            'lanes': [{'id': 'fake_lane_id_1',
                                                       'qc_lib': 1,
                                                       'qc_seq': 1,
                                                       'run_status': 'qc complete',
                                                       'qc_started': 1,
                                                       'qc_complete_datetime': 'any string will do',
                                                       }
                                                      ]
                                            },
                       'fake_sample_id_2': {'mock data': 'anything', 'creation_datetime': '2020-04-29T11:03:35Z',
                                            'lanes': [{'id': 'fake_lane_id_2',
                                                       'qc_lib': 1,
                                                       'qc_seq': 1,
                                                       'run_status': 'qc complete',
                                                       'qc_started': 1,
                                                       'qc_complete_datetime': 'any string will do',
                                                       },
                                                      {'id': 'fake_lane_id_3',
                                                       'qc_lib': 1,
                                                       'qc_seq': 0,
                                                       'run_status': 'qc complete',
                                                       'qc_started': 1,
                                                       'qc_complete_datetime': 'any string will do',
                                                       }
                                                      ]
                                            },
                       'fake_sample_id_3': {'mock data': 'anything', 'creation_datetime': '2020-11-16T16:43:04Z',
                                            'lanes': [{'id': 'fake_lane_id_4',
                                                       'qc_lib': 1,
                                                       'qc_seq': 1,
                                                       'run_status': 'qc complete',
                                                       'qc_started': 1,
                                                       'qc_complete_datetime': 'any string will do',
                                                       }
                                                      ]
                                            },
                       'fake_sample_id_4': {'mock data': 'anything', 'creation_datetime': '2021-05-02T10:31:49Z',
                                            'lanes': [{'id': 'fake_lane_id_5',
                                                       'qc_lib': 1,
                                                       'qc_seq': 1,
                                                       'run_status': 'qc complete',
                                                       'qc_started': 1,
                                                       'qc_complete_datetime': 'any string will do',
                                                       }
                                                      ]
                                            },
                       }
    mock_metadata = [{'sanger_sample_id': {'order': 1, 'name': 'Sanger_Sample_ID', 'value': 'fake_sample_id_1'},
                      'some_other_column': {'order': 2, 'name': 'Something_Made_Up', 'value': ''},
                      'another_fake_column': {'order': 3, 'name': 'Also_Made_Up', 'value': 'whatevs'},
                      'lane_id': {'order': 4, 'name': 'Lane_ID', 'value': 'fake_lane_id_1'},
                      }
                     ]

    # data we expect DataService method to return, given patched queries with the value above
    # the latest month included here must match the date provided by `mock_data_updated`
    expected_progress_data = {
        'date': ['Sep 2019', 'Oct 2019', 'Nov 2019', 'Dec 2019', 'Jan 2020', 'Feb 2020', 'Mar 2020',
                 'Apr 2020', 'May 2020', 'Jun 2020', 'Jul 2020', 'Aug 2020', 'Sep 2020', 'Oct 2020',
                 'Nov 2020', 'Dec 2020', 'Jan 2021', 'Feb 2021', 'Mar 2021', 'Apr 2021', 'May 2021'],
        'samples received': [2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 8],
        'samples sequenced': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }

    expected_institution_data = {'FakOne': {'name': 'Fake institution One', 'db_key': 'Fake institution One'},
                                 'FakTwo': {'name': 'Fake institution Two', 'db_key': 'Fake institution Two'},
                                 }
    expected_sample_data = {'FakOne': [{'sample_id': 'fake_sample_id_1'}, {'sample_id': 'fake_sample_id_2'}],
                            'FakTwo': [{'sample_id': 'fake_sample_id_3'}, {'sample_id': 'fake_sample_id_4'}]
                            }
    expected_seq_status = {'FakOne': mock_seq_status,
                           'FakTwo': mock_seq_status
                           }
    expected_batches = {
        'FakOne': {'expected': 2, 'received': 4, 'deliveries': [{'name': 'Batch 1', 'date': '2019-09-13', 'number': 1},
                                                                {'name': 'Batch 2', 'date': '2020-04-29', 'number': 1},
                                                                {'name': 'Batch 3', 'date': '2020-11-16', 'number': 1},
                                                                {'name': 'Batch 4', 'date': '2021-05-02', 'number': 1}
                                                                ]
                   },
        'FakTwo': {'expected': 2, 'received': 4, 'deliveries': [{'name': 'Batch 1', 'date': '2019-09-13', 'number': 1},
                                                                {'name': 'Batch 2', 'date': '2020-04-29', 'number': 1},
                                                                {'name': 'Batch 3', 'date': '2020-11-16', 'number': 1},
                                                                {'name': 'Batch 4', 'date': '2021-05-02', 'number': 1}
                                                                ]
                   }
        }
    expected_seq_summary = {'FakOne': {'received': 4, 'completed': 5, 'success': 4, 'failed': 1,
                                       'fail_messages': [
                                           {'lane': 'fake_lane_id_3 (sample fake_sample_id_2)', 'stage': 'sequencing',
                                            'issue': 'sorry, failure mesages cannot currently be seen here'
                                            }
                                           ]
                                       },
                            'FakTwo': {'received': 4, 'completed': 5, 'success': 4, 'failed': 1,
                                       'fail_messages': [
                                           {'lane': 'fake_lane_id_3 (sample fake_sample_id_2)', 'stage': 'sequencing',
                                            'issue': 'sorry, failure mesages cannot currently be seen here'
                                            }
                                           ]
                                       }
                            }
    expected_pipeline_summary = {
        'FakOne': {'running': 5, 'completed': 0, 'success': 0, 'failed': 0, 'fail_messages': []},
        'FakTwo': {'running': 5, 'completed': 0, 'success': 0, 'failed': 0, 'fail_messages': []}
        }

    expected_metadata = '''"Sanger_Sample_ID","Something_Made_Up","Also_Made_Up","Lane_ID","Download link"
"fake_sample_id_1","","whatevs","fake_lane_id_1","https://fake.host/any/path/fake_lane_id_1/"'''

    # create DataService object outside setUp() to avoid creating multipe instances
    # this means we use cahced data rather than making multiple patched queries to SampleMetadata etc.
    monocle_data = DataService(set_up=False, structure_call=True)

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
        self.assertIsInstance(self.monocle_data, DataService)

    @patch.object(SampleMetadata, 'get_institution_names')
    @patch.object(SampleMetadata, 'get_samples')
    @patch.object(SequencingStatus, 'get_multiple_samples')
    def get_mock_data(self, mock_seq_samples_query, mock_db_sample_query, mock_institution_query):
        mock_institution_query.return_value = self.mock_institutions
        mock_db_sample_query.return_value = self.mock_samples
        mock_seq_samples_query.return_value = self.mock_seq_status
        # these calls will cache data in the object, so the mocked
        # data can be retrieved by test case calls to these methods without
        # neeeding to patch the underlying queries throughout the test code
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

    @patch.object(MetadataDownload, 'get_metadata')
    def test_get_metadata(self, mock_metadata_fetch):
        mock_metadata_fetch.return_value = self.mock_metadata
        metadata = self.monocle_data.get_metadata(self.mock_institutions[0], 'pipeline', 'successful',
                                                  'https://fake.host/any/path')
        self.assertEqual(self.expected_metadata, metadata)


class TestServiceFactory(unittest.TestCase):
    """ Unit test class for the service_factory module """

    TEST_USER = 'test_user'

    @patch('dash.api.service.service_factory.UserService', autospec=True)
    def test_service_factory_user_service(self, user_mock):
        self.assertIsInstance(ServiceFactory.user_service('test_user'), UserService)
        user_mock.assert_called_once()

    @patch('dash.api.service.service_factory.TestDataService', autospec=True)
    def test_service_factory_data_service_test_mode(self, data_mock):
        ServiceFactory.TEST_MODE = True
        res = ServiceFactory.data_service(self.TEST_USER)
        self.assertIsInstance(res, TestDataService)
        data_mock.assert_called_once()

    @patch('dash.api.service.service_factory.DataService', autospec=True)
    def test_service_factory_data_service(self, data_mock):
        ServiceFactory.TEST_MODE = False
        self.assertIsInstance(ServiceFactory.data_service(self.TEST_USER), DataService)
        data_mock.assert_called_once_with(self.TEST_USER)

