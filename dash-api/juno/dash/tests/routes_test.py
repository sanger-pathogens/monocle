import unittest
from dash.api.routes import *


class TestRoutes(unittest.TestCase):
    """ Test class for the routes module """

    def test_hello_world(self):
        self.assertEqual(hello_world(), 200)

