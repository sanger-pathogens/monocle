import unittest
from unittest.mock import patch
from flask import Config
from metadata.api.routes import *


class TestRoutes(unittest.TestCase):
    """ Test class for the routes module """

    def test_update_sample_metadata(self):
        # TODO Add this test
        pass

    @patch('metadata.api.download_handler.DownloadHandler')
    def test_get_download_metadata(self, download_handler_mock):
        # TODO Add this test
        pass
