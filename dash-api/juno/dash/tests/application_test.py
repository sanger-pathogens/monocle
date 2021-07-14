import unittest
from unittest.mock import patch
from dash.api import application as app


class TestApplication(unittest.TestCase):
    """ Unit test class for the application module """

    @patch.object(app, 'create_application')
    def test_app_creation(self, create_application):
        from dash.wsgi import application
        self.assertIsNotNone(application)
        create_application.assert_called_once()
