import unittest
from unittest.mock import patch
from flask import Config
from metadata.api.routes import *
import connexion


class TestRoutes(unittest.TestCase):
    """ Test class for the routes module """

    @patch('metadata.api.routes.os')
    @patch('connexion.request')
    @patch('metadata.lib.upload_handler.UploadHandler')
    def test_update_sample_metadata(self, mock_upload_handler, mock_connexion_request, mock_os):
        http_status = update_sample_metadata([], mock_upload_handler)
        self.assertEqual(http_status, 200)

    @patch('metadata.api.routes.os')
    @patch('connexion.request')
    @patch('metadata.lib.upload_handler.UploadHandler')
    def test_update_in_silico_data(self, mock_upload_handler, mock_connexion_request, mock_os):
        http_status = update_in_silico_data([], mock_upload_handler)
        self.assertEqual(http_status, 200)

    @patch('metadata.api.download_handler.DownloadHandler')
    def test_get_download_metadata(self, download_handler_mock):
        # TODO Add this test
        pass
