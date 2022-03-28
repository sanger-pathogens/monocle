import unittest

from dash.api.error_handlers import *
from dash.api.exceptions import NotAuthorisedException


class TestErrorHandlers(unittest.TestCase):
    """Unit test class for the error_handlers module"""

    def test_handle_unauthorised(self):
        resp = handle_unauthorised(NotAuthorisedException())
        self.assertEqual(resp.status_code, 403)

    def test_handle_user_data_error(self):
        # TODO The package for this exception needs sorting out
        # resp = handle_user_data_error()
        # self.assertEqual(resp.status_code, 403)
        pass
