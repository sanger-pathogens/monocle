import unittest
import flask
from unittest.mock import patch, MagicMock, Mock
from flask import Config
import metadata.api.routes as mar
from metadata.api.database.monocle_database_service import MonocleDatabaseService
from metadata.api.routes import *
import connexion


class TestRoutes(unittest.TestCase):
    """ Test class for the routes module """

    @patch('metadata.api.routes.os')
    @patch('connexion.request')
    @patch('metadata.api.upload_handlers.UploadMetadataHandler')
    def test_update_sample_metadata_route(self, mock_upload_handler, mock_connexion_request, mock_os):
        http_status = update_sample_metadata_route([], mock_upload_handler)
        self.assertEqual(http_status, 200)

    @patch('metadata.api.routes.os')
    @patch('connexion.request')
    @patch('metadata.api.upload_handlers.UploadInSilicoHandler')
    def test_update_in_silico_data_route(self, mock_upload_handler, mock_connexion_request, mock_os):
        http_status = update_in_silico_data_route([], mock_upload_handler)
        self.assertEqual(http_status, 200)

    @patch('metadata.api.download_handlers.DownloadMetadataHandler')
    def test_get_download_metadata_route(self, download_handler_mock):
        # TODO Add this test
        pass

    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_samples')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_samples_route_jsonified(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ['sample1', 'sample2']
        mocked_jsoncall.return_value = 'expected'
        fakeDB = MagicMock()
        fakeDB.get_samples = MagicMock(return_value=['sample1', 'sample2'])
        under_test = mar.get_samples_route(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ('expected', 200))

    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_samples')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_samples_route_no_return(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = []
        mocked_jsoncall.return_value = ''
        fakeDB = MagicMock()
        fakeDB.get_samples = MagicMock(return_value=[])
        under_test = mar.get_samples_route(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ('', 404))

    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_filtered_samples')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_filtered_samples_route_jsonified(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ['sample1', 'sample2']
        mocked_jsoncall.return_value = 'expected'
        fakeDB = MagicMock()
        fakeDB.get_filtered_samples = MagicMock(return_value=['sample1', 'sample2'])
        under_test = mar.get_filtered_samples_route({'serotype': 'IA'}, fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ('expected', 200))

    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_filtered_samples')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_filtered_samples_route_no_return(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = []
        mocked_jsoncall.return_value = ''
        fakeDB = MagicMock()
        fakeDB.get_filtered_samples = MagicMock(return_value=[])
        under_test = mar.get_filtered_samples_route({'serotype': 'None'}, fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ('', 404))


    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_filtered_samples')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_filtered_samples_route_stop_injection(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ['sample1', 'sample2']
        mocked_jsoncall.return_value = ''
        fakeDB = MagicMock()
        fakeDB.get_filtered_samples = MagicMock(return_value=[])
        for looks_iffy_to_me_guv in [  'serotype="Ia"; DO something NASTY; --',
                                       'actually anything with -- in it',
                                       'no semi; colons either',
                                       'wildcards % are right out'
                                       ]:
          under_test = mar.get_filtered_samples_route({looks_iffy_to_me_guv: 'any search term'}, fakeDB)
          self.assertEqual(under_test, ('Invalid arguments provided', 400))


    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_authenticated_username')
    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_institutions')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_institutions_jsonified(self, mocked_jsoncall, mocked_query, mocked_username):
        mocked_username.return_value = 'mock_user'
        mocked_query.return_value = ['ints1', 'inst2']
        mocked_jsoncall.return_value = 'expected'
        fakeDB = MagicMock()
        fakeDB.get_institutions = MagicMock(return_value=['inst1', 'inst2'])
        under_test = mar.get_institutions(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ('expected', 200))

    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_authenticated_username')
    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_institutions')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_institutions_not_returned(self, mocked_jsoncall, mocked_query, mocked_username):
        mocked_username.return_value = 'mock_user'
        mocked_query.return_value = []
        mocked_jsoncall.return_value = ''
        fakeDB = MagicMock()
        fakeDB.get_institutions = MagicMock(return_value=[])
        under_test = mar.get_institutions(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ('', 404))

    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_institution_names')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_institution_names_route_jsonified(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ['ints1', 'inst2']
        mocked_jsoncall.return_value = 'expected'
        fakeDB = MagicMock()
        fakeDB.get_institution_names = MagicMock(return_value=['ints1', 'inst2'])
        under_test = mar.get_institution_names_route(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ('expected', 200))

    @patch('metadata.api.database.monocle_database_service.MonocleDatabaseService.get_institution_names')
    @patch('metadata.api.routes.convert_to_json')
    def test_get_institution_names_route_not_returned(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = []
        mocked_jsoncall.return_value = ''
        fakeDB = MagicMock()
        fakeDB.get_institution_names = MagicMock(return_value=[])
        under_test = mar.get_institution_names_route(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ('', 404))
