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
    TEST_USER = 'fbloggs'

    EXPECTED_PROGRESS_RESULTS = {
        'progress_graph': {
            'title': 'Project Progress',
            'data': SERVICE_CALL_RETURN_DATA,
            'x_col_key': 'date',
            'x_label': '',
            'y_cols_keys': ['samples received', 'samples sequenced'],
            'y_label': 'number of samples'
        }
    }

    def setUp(self) -> None:
        ServiceFactory.TEST_MODE = True

    @patch('dash.api.routes.call_jsonify')
    @patch('dash.api.routes.get_authenticated_username')
    @patch.object(ServiceFactory, 'user_service')
    def test_get_user_details(self, user_service_mock, username_mock, resp_mock):
        # Given
        user_service_mock.return_value.get_user_details.return_value = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        # When
        result = get_user_details()
        # Then
        user_service_mock.assert_called_once_with(self.TEST_USER)
        user_service_mock.return_value.get_user_details.assert_called_once()
        resp_mock.assert_called_once_with(
            {
                'user_details': self.SERVICE_CALL_RETURN_DATA
            }
        )
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 1)
        self.assertEqual(result[1], 200)

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
        self.assertEqual(result[1], 200)

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
        self.assertEqual(result[1], 200)

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
        self.assertEqual(result[1], 200)

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
        self.assertEqual(result[1], 200)

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
        self.assertEqual(result[1], 200)

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
