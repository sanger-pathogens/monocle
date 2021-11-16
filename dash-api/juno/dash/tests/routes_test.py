from flask import Response
from http import HTTPStatus
import pathlib
import json
import unittest
from unittest.mock import patch, Mock
from dash.api.service.service_factory import ServiceFactory
from dash.api.exceptions import NotAuthorisedException
from dash.api.routes import *


class TestRoutes(unittest.TestCase):
    """ Test class for the routes module """

    # For the purposes of testing it doesn't matter what the service call return dictionary looks like
    # so we'll make the contents abstract and simple
    SERVICE_CALL_RETURN_DATA = {'field1': 'value1'}
    SERVICE_CALL_RETURN_CSV_DATA = {'success': True, 'filename':'myfile.csv', 'content' : 'a,csv,string'}
    TEST_USER = 'fbloggs'
    TEST_HOST_NAME = 'mock.host'

    EXPECTED_PROGRESS_RESULTS = {
        'progress_graph': {
            'data': SERVICE_CALL_RETURN_DATA
        }
    }
        
    EXPECTED_CSV_CONTENT_TYPE    = 'text/csv; charset=UTF-8'
    EXPECTED_CONTENT_DISPOSITION = 'attachment; filename="{}"'.format(SERVICE_CALL_RETURN_CSV_DATA['filename'])

    def setUp(self) -> None:
        ServiceFactory.TEST_MODE = True

    @patch('dash.api.routes.call_jsonify')
    @patch('dash.api.routes.get_authenticated_username')
    @patch.object(ServiceFactory, 'user_service')
    def test_get_user_details(self, user_service_mock, username_mock, resp_mock):
        # Given
        user_service_mock.return_value.user_details = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        # When
        result = get_user_details()
        # Then
        user_service_mock.assert_called_once_with(self.TEST_USER)
        resp_mock.assert_called_once_with(
            {
                'user_details': self.SERVICE_CALL_RETURN_DATA
            }
        )
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 1)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch('dash.api.routes.call_jsonify')
    @patch('dash.api.routes.get_authenticated_username')
    @patch.object(ServiceFactory, 'data_service')
    def test_get_batches(self, data_service_mock, username_mock, resp_mock):
        # Given
        data_service_mock.return_value.get_batches.return_value = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        # When
        result = get_batches()
        # Then
        data_service_mock.assert_called_once_with(self.TEST_USER)
        data_service_mock.return_value.get_batches.assert_called_once()
        resp_mock.assert_called_once_with(
            {
                'batches': self.SERVICE_CALL_RETURN_DATA
            }
        )
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch('dash.api.routes.call_jsonify')
    @patch('dash.api.routes.get_authenticated_username')
    @patch.object(ServiceFactory, 'data_service')
    def test_get_institutions(self, data_service_mock, username_mock, resp_mock):
        # Given
        data_service_mock.return_value.get_institutions.return_value = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        # When
        result = get_institutions()
        # Then
        data_service_mock.assert_called_once_with(self.TEST_USER)
        data_service_mock.return_value.get_institutions.assert_called_once()
        resp_mock.assert_called_once_with(
            {
                'institutions': self.SERVICE_CALL_RETURN_DATA
            }
        )
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch('dash.api.routes.call_jsonify')
    @patch('dash.api.routes.get_authenticated_username')
    @patch.object(ServiceFactory, 'data_service')
    def test_get_progress(self, data_service_mock, username_mock, resp_mock):
        # Given
        data_service_mock.return_value.get_progress.return_value = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        # When
        result = get_progress()
        # Then
        data_service_mock.assert_called_once_with(self.TEST_USER)
        data_service_mock.return_value.get_progress.assert_called_once()
        resp_mock.assert_called_once_with(self.EXPECTED_PROGRESS_RESULTS)
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch('dash.api.routes.call_jsonify')
    @patch('dash.api.routes.get_authenticated_username')
    @patch.object(ServiceFactory, 'data_service')
    def test_sequencing_status_summary(self, data_service_mock, username_mock, resp_mock):
        # Given
        data_service_mock.return_value.sequencing_status_summary.return_value = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        # When
        result = sequencing_status_summary()
        # Then
        data_service_mock.assert_called_once_with(self.TEST_USER)
        data_service_mock.return_value.sequencing_status_summary.assert_called_once()
        resp_mock.assert_called_once_with(
            {
                'sequencing_status': self.SERVICE_CALL_RETURN_DATA
            }
        )
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch('dash.api.routes.call_jsonify')
    @patch('dash.api.routes.get_authenticated_username')
    @patch.object(ServiceFactory, 'data_service')
    def test_pipeline_status_summary(self, data_service_mock, username_mock, resp_mock):
        # Given
        data_service_mock.return_value.pipeline_status_summary.return_value = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        # When
        result = pipeline_status_summary()
        # Then
        data_service_mock.assert_called_once_with(self.TEST_USER)
        data_service_mock.return_value.pipeline_status_summary.assert_called_once()
        resp_mock.assert_called_once_with(
            {
                'pipeline_status': self.SERVICE_CALL_RETURN_DATA
            }
        )
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch('dash.api.routes.call_jsonify')
    @patch('dash.api.routes.get_authenticated_username')
    @patch.object(ServiceFactory, 'data_service')
    def test_get_bulk_download_info(self, data_service_mock, username_mock, resp_mock):
        # Given
        batches = self.SERVICE_CALL_RETURN_DATA
        assemblies = False
        annotations = True
        expected_payload = 'paylod'
        data_service_mock.return_value.get_bulk_download_info.return_value = expected_payload
        username_mock.return_value = self.TEST_USER
        # When
        result = bulk_download_info({'sample filters':{'batches':batches}, 'assemblies':assemblies, 'annotations':annotations})
        # Then
        data_service_mock.assert_called_once_with(self.TEST_USER)
        data_service_mock.return_value.get_bulk_download_info.assert_called_once_with(
            {'batches':batches}, assemblies=assemblies, annotations=annotations, reads=False)
        resp_mock.assert_called_once_with(expected_payload)
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch('dash.api.routes.call_jsonify')
    @patch('dash.api.routes.get_authenticated_username')
    @patch('dash.api.routes.zip_files')
    @patch('dash.api.routes.uuid4')
    @patch.object(ServiceFactory, 'data_service')
    @patch('pathlib.Path.is_dir')
    def test_get_bulk_download_urls(self,
            is_dir_mock,
            data_service_mock,
            uuid4_mock,
            zip_files_mock,
            username_mock,
            resp_mock
        ):
        # Given
        batches = ['2020-09-04', '2021-01-30']
        assemblies = False
        annotations = True
        samples = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        data_service_mock.return_value.get_filtered_samples.return_value = samples
        is_dir_mock.return_value = True
        uuid_hex = '123'
        uuid4_mock.return_value.hex = uuid_hex
        zip_file_basename = uuid_hex
        zip_file_location = 'some/dir'
        data_service_mock.return_value.get_zip_download_location.return_value = zip_file_location
        download_symlink = 'downloads/'
        data_service_mock.return_value.make_download_symlink.return_value = download_symlink
        lane_files = {'pubname': ['lane file', 'another lane file']}
        data_service_mock.return_value.get_public_name_to_lane_files_dict.return_value = lane_files
        expected_payload = {
            'download_urls': [f'{download_symlink}{zip_file_basename}.zip']
        }
        # When
        result = bulk_download_urls({'sample filters':{'batches':batches}, 'assemblies':assemblies, 'annotations':annotations})
        # Then
        data_service_mock.assert_called_once_with(self.TEST_USER)
        zip_files_mock.assert_called_once_with(
            lane_files,
            basename=zip_file_basename,
            location=zip_file_location
            )
        data_service_mock.return_value.make_download_symlink.assert_called_once_with(cross_institution=True)
        resp_mock.assert_called_once_with(expected_payload)
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch('dash.api.routes.call_jsonify')
    @patch('dash.api.routes.get_authenticated_username')
    @patch.object(ServiceFactory, 'data_service')
    def test_get_metadata_with_default_params(self, data_service_mock, username_mock, resp_mock):
        # Given
        batches = self.SERVICE_CALL_RETURN_DATA
        sample_filters     = {'batches':batches}
        expected_payload   = 'payload'
        data_service_mock.return_value.get_metadata.return_value = expected_payload
        username_mock.return_value = self.TEST_USER
        # When
        result = get_metadata({'sample filters': sample_filters})
        # Then
        data_service_mock.assert_called_once_with(self.TEST_USER)
        data_service_mock.return_value.get_metadata.assert_called_once_with(  sample_filters,
                                                                              start_row         = None,
                                                                              num_rows          = GetMetadataInputDefaults['num rows'],
                                                                              include_in_silico = GetMetadataInputDefaults['in silico'],
                                                                              metadata_columns  = GetMetadataInputDefaults['metadata columns'],
                                                                              in_silico_columns = GetMetadataInputDefaults['in silico columns'])
        resp_mock.assert_called_once_with(expected_payload)
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch('dash.api.routes.call_jsonify')
    @patch('dash.api.routes.get_authenticated_username')
    @patch.object(ServiceFactory, 'data_service')
    def test_get_metadata_all_columns(self, data_service_mock, username_mock, resp_mock):
        # Given
        batches = self.SERVICE_CALL_RETURN_DATA
        sample_filters     = {'batches':batches}
        metadata_columns   = ['_ALL']
        in_silico_columns  = ['_ALL']
        expected_payload   = 'payload'
        data_service_mock.return_value.get_metadata.return_value = expected_payload
        username_mock.return_value = self.TEST_USER
        # When
        result = get_metadata({'sample filters': sample_filters, 'metadata columns': metadata_columns, 'in silico columns':in_silico_columns})
        # Then
        data_service_mock.assert_called_once_with(self.TEST_USER)
        data_service_mock.return_value.get_metadata.assert_called_once_with(  sample_filters,
                                                                              start_row         = None,
                                                                              num_rows          = GetMetadataInputDefaults['num rows'],
                                                                              include_in_silico = GetMetadataInputDefaults['in silico'],
                                                                              metadata_columns  = None,
                                                                              in_silico_columns = None)
        resp_mock.assert_called_once_with(expected_payload)
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch('dash.api.routes.call_jsonify')
    @patch('dash.api.routes.get_authenticated_username')
    @patch.object(ServiceFactory, 'data_service')
    def test_get_metadata_with_optional_params(self, data_service_mock, username_mock, resp_mock):
        # Given
        batches = self.SERVICE_CALL_RETURN_DATA
        sample_filters     = {'batches':batches}
        start_row          = 21
        num_rows           = 20
        include_in_silico  = True
        metadata_columns   = ['submitting_institution', 'public_name']
        in_silico_columns  = ['ST']
        expected_payload   = 'payload'
        data_service_mock.return_value.get_metadata.return_value = expected_payload
        username_mock.return_value = self.TEST_USER
        # When
        result = get_metadata({  'sample filters'     : sample_filters,
                                 'start row'          : start_row,
                                 'num rows'           : num_rows,
                                 'in silico'          : include_in_silico,
                                 'metadata columns'   : metadata_columns,
                                 'in silico columns'  : in_silico_columns
                                 }
                              )
        # Then
        data_service_mock.assert_called_once_with(self.TEST_USER)
        data_service_mock.return_value.get_metadata.assert_called_once_with(  sample_filters,
                                                                              start_row         = start_row,
                                                                              num_rows          = num_rows,
                                                                              include_in_silico = include_in_silico,
                                                                              metadata_columns  = metadata_columns,
                                                                              in_silico_columns = in_silico_columns)
        resp_mock.assert_called_once_with(expected_payload)
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch('dash.api.routes.get_authenticated_username')
    @patch('dash.api.routes.get_host_name')
    @patch.object(ServiceFactory, 'data_service')
    def test_get_metadata_for_download(self, data_service_mock, host_name_mock, username_mock):
        # Given
        data_service_mock.return_value.get_metadata_for_download.return_value = self.SERVICE_CALL_RETURN_CSV_DATA
        username_mock.return_value = self.TEST_USER
        host_name_mock.return_value = self.TEST_HOST_NAME
        # When
        result = get_metadata_for_download('Fake Institution', 'pipeline', 'successful')
        # Then
        data_service_mock.assert_called_once_with(self.TEST_USER)
        data_service_mock.return_value.get_metadata_for_download.assert_called_once()
        self.assertIsInstance(result, type(Response('any content will do')))
        self.assertEqual(result.status_code,                    HTTPStatus.OK)
        self.assertEqual(result.content_type,                   self.EXPECTED_CSV_CONTENT_TYPE)
        self.assertEqual(result.headers['Content-Disposition'], self.EXPECTED_CONTENT_DISPOSITION)
        
    def test_get_host_name(self):
        request_mock = Mock()
        request_mock.host = self.TEST_HOST_NAME
        hostname = get_host_name(request_mock)
        self.assertEqual(hostname, self.TEST_HOST_NAME)

    def test_get_authenticated_username_nontest_mode(self):
        # Given
        ServiceFactory.TEST_MODE = False
        request_mock = Mock()
        headers = dict()
        headers['X-Remote-User'] = self.TEST_USER
        headers['another-hdr'] = 'something'
        request_mock.headers = headers
        # When
        username = get_authenticated_username(request_mock)
        # Then
        self.assertEqual(username, self.TEST_USER)

    def test_get_authenticated_username_nontest_mode_with_no_hdr(self):
        # Given
        ServiceFactory.TEST_MODE = False
        request_mock = Mock()
        headers = dict()
        headers['another-hdr'] = 'something'
        request_mock.headers = headers
        # When/Then
        with self.assertRaises(NotAuthorisedException):
            username = get_authenticated_username(request_mock)

    def test_get_authenticated_username_nontest_mode_with_empty_hdr(self):
        # Given
        ServiceFactory.TEST_MODE = False
        request_mock = Mock()
        headers = dict()
        headers['X-Remote-User'] = ''
        headers['another-hdr'] = 'something'
        request_mock.headers = headers
        # When/Then
        with self.assertRaises(NotAuthorisedException):
            username = get_authenticated_username(request_mock)

    def test_get_authenticated_username_test_mode(self):
        # Given
        ServiceFactory.TEST_MODE = True
        request_mock = Mock()
        headers = dict()
        headers['X-Remote-User'] = self.TEST_USER
        headers['another-hdr'] = 'something'
        request_mock.headers = headers
        # When
        username = get_authenticated_username(request_mock)
        # Then
        self.assertIsNone(username)
