import unittest
from unittest.mock import patch, Mock
from dash.api.user.user_service import UserService
from dash.api.routes import *


class TestRoutes(unittest.TestCase):
    """ Test class for the routes module """

    TEST_USER_NAME = 'fbloggs'
    TEST_USER_DETAILS = {
        "username": TEST_USER_NAME,
        "memberOf": [
            {
                "inst_id": "inst_id1",
                "inst_name": "inst_name1"
            }
        ]
    }

    def setUp(self) -> None:
        self.user_service_mock = Mock(spec=UserService)

    @patch('dash.api.routes.call_jsonify')
    def test_get_user_details(self, resp_mock):
        self.user_service_mock.get_user_details.return_value = self.TEST_USER_DETAILS
        result = get_user_details(self.TEST_USER_NAME, self.user_service_mock)
        self.user_service_mock.get_user_details.assert_called_once_with(self.TEST_USER_NAME)
        resp_mock.assert_called_once_with(self.TEST_USER_DETAILS)


