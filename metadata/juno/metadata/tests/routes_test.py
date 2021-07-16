import unittest
from unittest.mock import patch, MagicMock
from flask import Config
import metadata.api.routes as mar
from metadata.api.database.monocle_database_service import MonocleDatabaseService


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
        mocked_query.return_value = ['sample1', 'sample2']
        mocked_jsoncall.return_value = 'expected'
        fakeDB = MagicMock()
        fakeDB.get_samples = MagicMock(return_value=['sample1', 'sample2'])
        under_test = mar.get_samples(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ('expected', 200))

    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_samples')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_samples_no_return(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = []
        mocked_jsoncall.return_value = ''
        fakeDB = MagicMock()
        fakeDB.get_samples = MagicMock(return_value=[''])
        under_test = mar.get_samples(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ('', 404))

    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_institutions')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_institutions_jsonified(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ['ints1', 'inst2']
        mocked_jsoncall.return_value = 'expected'
        fakeDB = MagicMock()
        fakeDB.get_institutions = MagicMock(return_value=['inst1', 'inst2'])
        under_test = mar.get_institutions(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ('expected', 200))

    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_institutions')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_institutions_not_returned(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = []
        mocked_jsoncall.return_value = ''
        fakeDB = MagicMock()
        fakeDB.get_institutions = MagicMock(return_value=[''])
        under_test = mar.get_institutions(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ('', 404))

    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_institution_names')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_institution_names_jsonified(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ['ints1', 'inst2']
        mocked_jsoncall.return_value = 'expected'
        fakeDB = MagicMock()
        fakeDB.get_institution_names = MagicMock(return_value=['ints1', 'inst2'])
        under_test = mar.get_institution_names(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ('expected', 200))

    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_institution_names')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_institution_names_not_returned(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = []
        mocked_jsoncall.return_value = ''
        fakeDB = MagicMock()
        fakeDB.get_institution_names = MagicMock(return_value=[''])
        under_test = mar.get_institution_names(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ('', 404))
