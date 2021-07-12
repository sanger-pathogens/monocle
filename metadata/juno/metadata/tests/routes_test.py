import unittest
from unittest.mock import patch, MagicMock
from flask import Config
import metadata.api.routes as mar


class TestRoutes(unittest.TestCase):
    """ Test class for the routes module """

    def test_update_sample_metadata(self):
        # TODO Add this test
        pass

    @patch('metadata.api.download_handler.DownloadHandler')
    def test_get_download_metadata(self, download_handler_mock):
        # TODO Add this test
        pass

    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_samples')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_samples_jsonified(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ''
        mocked_jsoncall.return_value = ''
        mocked_jsoncall.assert_called_once()
        under_test = mar.get_samples()
        self.assertEqual(under_test, 'MAKE_THIS_FAIL_SO_WE_KNOW_IT_IS_WIP')

    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_institutions')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_samples_jsonified(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ''
        mocked_jsoncall.return_value = ''
        mocked_jsoncall.assert_called_once()
        under_test = mar.get_samples()
        self.assertEqual(under_test, 'MAKE_THIS_FAIL_SO_WE_KNOW_IT_IS_WIP')

    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_institution_names')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_samples_jsonified(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ''
        mocked_jsoncall.return_value = ''
        mocked_jsoncall.assert_called_once()
        under_test = mar.get_samples()
        self.assertEqual(under_test, 'MAKE_THIS_FAIL_SO_WE_KNOW_IT_IS_WIP')
