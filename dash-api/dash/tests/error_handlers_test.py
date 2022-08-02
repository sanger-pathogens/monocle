import unittest

from dash.api.error_handlers import handle_ldap_data_error, handle_unauthorised
from dash.api.exceptions import LdapDataError, NotAuthorisedException


class TestErrorHandlers(unittest.TestCase):
    """Unit test class for the error_handlers module"""

    def test_handle_unauthorised(self):
        resp = handle_unauthorised(NotAuthorisedException())
        self.assertEqual(resp.status_code, 403)

    def test_handle_ldap_data_error(self):
        resp = handle_ldap_data_error(LdapDataError())
        self.assertEqual(resp.status_code, 403)
