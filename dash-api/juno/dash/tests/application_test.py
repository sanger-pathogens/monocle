import unittest
from unittest.mock import patch
from dash.api.dependencies import DashboardApiModule


class TestApplication(unittest.TestCase):
    """ Unit test class for the application module """

    @patch('dash.api.application.create_application')
    def test_app_creation(self, create_application):
        from dash.wsgi import application

        self.assertIsNotNone(application)
        create_application.assert_called_once()
        config, dependencies = create_application.call_args[0]
        self.assertEqual(config, 'config.json')
        self.assertIsInstance(dependencies, DashboardApiModule)
