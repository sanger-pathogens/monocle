import unittest
from unittest.mock import patch
from dash.api.service.service_factory import ServiceFactory, DataService, UserService, TestDataService


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

