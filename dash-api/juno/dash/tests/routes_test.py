import unittest
from unittest.mock import patch, Mock
from dash.api.service.service_factory import ServiceFactory
from dash.api.routes import *


class TestRoutes(unittest.TestCase):
    """ Test class for the routes module """

    GET_BATCHES_RETURN_DATA = {'field1': 'value1'}

    def setUp(self) -> None:
        ServiceFactory.TEST_MODE = True

    @patch('dash.api.routes.call_jsonify')
    @patch.object(ServiceFactory, 'user_service')
    @patch.object(ServiceFactory, 'data_service')
    def test_get_batches(self, data_service_mock, user_service_mock, resp_mock):
        # TODO finish these tests
        #data_service_mock.return_value = Mock()get_batches.return_value = self.GET_BATCHES_RETURN_DATA
        #result = get_batches()
        #data_service_mock.get_batches.assert_called_once()
        #resp_mock.assert_called_once_with(result)
        pass


