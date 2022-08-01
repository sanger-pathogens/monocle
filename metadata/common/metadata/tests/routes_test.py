import unittest
from unittest.mock import MagicMock, patch

import metadata.api.routes as mar
from metadata.api.routes import update_in_silico_data_route, update_qc_data_route, update_sample_metadata_route
from metadata.tests.test_data import TEST_LANE_IN_SILICO_1, TEST_LANE_QC_DATA_1, TEST_SAMPLE_1


class TestRoutes(unittest.TestCase):
    """Test class for the routes module"""

    @patch("metadata.api.routes.os")
    @patch("connexion.request")
    @patch("metadata.api.upload_handlers.UploadMetadataHandler")
    def test_update_sample_metadata_route(self, mock_upload_handler, mock_connexion_request, mock_os):
        http_status = update_sample_metadata_route([], mock_upload_handler)
        self.assertEqual(http_status, 200)

    @patch("metadata.api.routes.os")
    @patch("connexion.request")
    @patch("metadata.api.upload_handlers.UploadMetadataHandler")
    def test_update_sample_metadata_route_reject_missing_file(
        self, mock_upload_handler, mock_connexion_request, mock_os
    ):
        mock_connexion_request.files = {}
        http_status = update_sample_metadata_route([], mock_upload_handler)
        self.assertEqual(http_status, ("Missing spreadsheet file", 400))

    @patch("metadata.api.routes.os")
    @patch("connexion.request")
    @patch("metadata.api.upload_handlers.UploadMetadataHandler")
    def test_update_sample_metadata_route_reject_bad_file_extension(
        self, mock_upload_handler, mock_connexion_request, mock_os
    ):
        mock_upload_handler.is_valid_file_type.return_value = False
        http_status = update_sample_metadata_route([], mock_upload_handler)
        self.assertIn("must be one of the following formats", http_status[0])
        self.assertEqual(http_status[1], 400)

    @patch("metadata.api.routes.os")
    @patch("connexion.request")
    @patch("metadata.api.upload_handlers.UploadMetadataHandler")
    @patch("metadata.api.routes.convert_to_json")
    def test_update_sample_metadata_route_reject_invalid(
        self, mock_jsonify, mock_upload_handler, mock_connexion_request, mock_os
    ):
        mock_upload_handler.load.return_value = ["any non empty list"]
        mock_jsonify.return_value = '["mock error message", "another mock error message"]'
        http_status = update_sample_metadata_route([], mock_upload_handler)
        self.assertIsInstance(http_status[0], str)
        self.assertEqual(http_status[1], 400)

    @patch("metadata.api.routes.os")
    @patch("connexion.request")
    @patch("metadata.api.upload_handlers.UploadInSilicoHandler")
    def test_update_in_silico_data_route(self, mock_upload_handler, mock_connexion_request, mock_os):
        http_status = update_in_silico_data_route([], mock_upload_handler)
        self.assertEqual(http_status, 200)

    @patch("metadata.api.routes.os")
    @patch("connexion.request")
    @patch("metadata.api.upload_handlers.UploadMetadataHandler")
    def test_update_in_silico_route_reject_missing_file(self, mock_upload_handler, mock_connexion_request, mock_os):
        mock_connexion_request.files = {}
        http_status = update_in_silico_data_route([], mock_upload_handler)
        self.assertEqual(http_status, ("Missing spreadsheet file", 400))

    @patch("metadata.api.routes.os")
    @patch("connexion.request")
    @patch("metadata.api.upload_handlers.UploadMetadataHandler")
    def test_update_in_silico_route_reject_bad_file_extension(
        self, mock_upload_handler, mock_connexion_request, mock_os
    ):
        mock_upload_handler.is_valid_file_type.return_value = False
        http_status = update_in_silico_data_route([], mock_upload_handler)
        self.assertIn("must be one of the following formats", http_status[0])
        self.assertEqual(http_status[1], 400)

    @patch("metadata.api.routes.os")
    @patch("connexion.request")
    @patch("metadata.api.upload_handlers.UploadMetadataHandler")
    @patch("metadata.api.routes.convert_to_json")
    def test_update_in_silico_route_reject_invalid(
        self, mock_jsonify, mock_upload_handler, mock_connexion_request, mock_os
    ):
        mock_upload_handler.load.return_value = ["any non empty list"]
        mock_jsonify.return_value = '["mock error message", "another mock error message"]'
        http_status = update_in_silico_data_route([], mock_upload_handler)
        self.assertIsInstance(http_status[0], str)
        self.assertEqual(http_status[1], 400)

    @patch("metadata.api.routes.os")
    @patch("connexion.request")
    @patch("metadata.api.upload_handlers.UploadInSilicoHandler")
    def test_update_qc_data_route(self, mock_upload_handler, mock_connexion_request, mock_os):
        http_status = update_qc_data_route([], mock_upload_handler)
        self.assertEqual(http_status, 200)

    @patch("metadata.api.routes.os")
    @patch("connexion.request")
    @patch("metadata.api.upload_handlers.UploadMetadataHandler")
    def test_update_qc_data_route_reject_missing_file(self, mock_upload_handler, mock_connexion_request, mock_os):
        mock_connexion_request.files = {}
        http_status = update_qc_data_route([], mock_upload_handler)
        self.assertEqual(http_status, ("Missing spreadsheet file", 400))

    @patch("metadata.api.routes.os")
    @patch("connexion.request")
    @patch("metadata.api.upload_handlers.UploadMetadataHandler")
    def test_update_qc_data_route_reject_bad_file_extension(self, mock_upload_handler, mock_connexion_request, mock_os):
        mock_upload_handler.is_valid_file_type.return_value = False
        http_status = update_qc_data_route([], mock_upload_handler)
        self.assertIn("must be one of the following formats", http_status[0])
        self.assertEqual(http_status[1], 400)

    @patch("metadata.api.routes.os")
    @patch("connexion.request")
    @patch("metadata.api.upload_handlers.UploadMetadataHandler")
    @patch("metadata.api.routes.convert_to_json")
    def test_update_qc_data_route_reject_invalid(
        self, mock_jsonify, mock_upload_handler, mock_connexion_request, mock_os
    ):
        mock_upload_handler.load.return_value = ["any non empty list"]
        mock_jsonify.return_value = '["mock error message", "another mock error message"]'
        http_status = update_qc_data_route([], mock_upload_handler)
        self.assertIsInstance(http_status[0], str)
        self.assertEqual(http_status[1], 400)

    @patch("metadata.api.download_handlers.DownloadMetadataHandler")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_download_metadata_route(self, mocked_jsoncall, download_handler_mock):
        mocked_jsoncall.return_value = "expected"
        mock_lane_id = "50000_2#282"
        mock_metadata = TEST_SAMPLE_1
        download_handler_mock.read_download_metadata.return_value = [mock_metadata]
        download_handler_mock.create_download_response.return_value = [mock_metadata]
        under_test = mar.get_download_metadata_route([mock_lane_id], download_handler_mock)
        mocked_jsoncall.assert_called_once_with({"download": [mock_metadata]})
        self.assertEqual(under_test, ("expected", 200))

    @patch("metadata.api.download_handlers.DownloadMetadataHandler")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_download_metadata_route_no_return(self, mocked_jsoncall, download_handler_mock):
        mocked_jsoncall.return_value = "expected"
        mock_lane_id = "50000_2#282"
        download_handler_mock.read_download_metadata.return_value = []
        download_handler_mock.create_download_response.return_value = []
        under_test = mar.get_download_metadata_route([mock_lane_id], download_handler_mock)
        mocked_jsoncall.assert_called_once_with({"download": []})
        self.assertEqual(under_test, ("expected", 404))

    @patch("metadata.api.download_handlers.DownloadInSilicoHandler")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_download_in_silico_data_route(self, mocked_jsoncall, download_handler_mock):
        mocked_jsoncall.return_value = "expected"
        mock_lane_id = "50000_2#282"
        mock_in_silico_data = TEST_LANE_IN_SILICO_1
        download_handler_mock.read_download_in_silico_data.return_value = [mock_in_silico_data]
        download_handler_mock.create_download_response.return_value = [mock_in_silico_data]
        under_test = mar.get_download_in_silico_data_route([mock_lane_id], download_handler_mock)
        mocked_jsoncall.assert_called_once_with({"download": [mock_in_silico_data]})
        self.assertEqual(under_test, ("expected", 200))

    @patch("metadata.api.download_handlers.DownloadInSilicoHandler.create_download_response")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_download_in_silico_data_route_no_return(self, mocked_jsoncall, download_handler_mock):
        mocked_jsoncall.return_value = "expected"
        mock_lane_id = "50000_2#282"
        download_handler_mock.read_download_in_silico_data.return_value = []
        download_handler_mock.create_download_response.return_value = []
        under_test = mar.get_download_in_silico_data_route([mock_lane_id], download_handler_mock)
        mocked_jsoncall.assert_called_once_with({"download": []})
        self.assertEqual(under_test, ("expected", 404))

    @patch("metadata.api.download_handlers.DownloadQCDataHandler.create_download_response")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_download_qc_data_route(self, mocked_jsoncall, download_handler_mock):
        mocked_jsoncall.return_value = "expected"
        mock_lane_id = "50000_2#282"
        mock_qc_data = TEST_LANE_QC_DATA_1
        download_handler_mock.read_download_qc_data.return_value = [mock_qc_data]
        download_handler_mock.create_download_response.return_value = [mock_qc_data]
        under_test = mar.get_download_qc_data_route([mock_lane_id], download_handler_mock)
        mocked_jsoncall.assert_called_once_with({"download": [mock_qc_data]})
        self.assertEqual(under_test, ("expected", 200))

    @patch("metadata.api.download_handlers.DownloadQCDataHandler.create_download_response")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_download_qc_data_route_no_return(self, mocked_jsoncall, download_handler_mock):
        mocked_jsoncall.return_value = "expected"
        mock_lane_id = "50000_2#282"
        download_handler_mock.read_download_qc_data.return_value = []
        download_handler_mock.create_download_response.return_value = []
        under_test = mar.get_download_qc_data_route([mock_lane_id], download_handler_mock)
        mocked_jsoncall.assert_called_once_with({"download": []})
        self.assertEqual(under_test, ("expected", 404))

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService")
    def test_delete_all_qc_data_route(self, mocked_dao):
        mocked_dao.delete_all_qc_data.return_value = None
        under_test = mar.delete_all_qc_data_route(mocked_dao)
        mocked_dao.delete_all_qc_data.assert_called_once_with()
        self.assertEqual(under_test, 200)

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService.get_samples")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_samples_route_jsonified(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ["sample1", "sample2"]
        mocked_jsoncall.return_value = "expected"
        fakeDB = MagicMock()
        fakeDB.get_samples = MagicMock(return_value=["sample1", "sample2"])
        under_test = mar.get_samples_route(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ("expected", 200))

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService.get_samples")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_samples_route_no_return(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = []
        mocked_jsoncall.return_value = ""
        fakeDB = MagicMock()
        fakeDB.get_samples = MagicMock(return_value=[])
        under_test = mar.get_samples_route(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ("", 404))

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService.get_samples_filtered_by_metadata")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_samples_filtered_by_metadata_route_jsonified(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ["sample1", "sample2"]
        mocked_jsoncall.return_value = "expected"
        fakeDB = MagicMock()
        fakeDB.get_samples_filtered_by_metadata = MagicMock(return_value=["sample1", "sample2"])
        under_test = mar.get_samples_filtered_by_metadata_route([{"name": "serotype", "values": ["IA"]}], fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ("expected", 200))

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService.get_samples_filtered_by_metadata")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_samples_filtered_by_metadata_route_no_return(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = []
        mocked_jsoncall.return_value = ""
        fakeDB = MagicMock()
        fakeDB.get_samples_filtered_by_metadata = MagicMock(return_value=[])
        under_test = mar.get_samples_filtered_by_metadata_route([{"name": "serotype", "values": ["None"]}], fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ("", 404))

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_samples_filtered_by_metadata_route_bad_field_name(self, mocked_jsoncall, dao_mock):
        mock_field_name = "bad_field_name"
        mock_values = ["anything"]
        mock_json = ""
        mocked_jsoncall.return_value = mock_json
        dao_mock.get_samples_filtered_by_metadata.return_value = None
        filtered_samples, http_status = mar.get_samples_filtered_by_metadata_route(
            [{"name": mock_field_name, "values": mock_values}], dao_mock
        )
        dao_mock.get_samples_filtered_by_metadata.assert_called_once_with({mock_field_name: mock_values})
        self.assertEqual(filtered_samples, "Invalid field name provided")
        self.assertEqual(http_status, 400)

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService.get_samples_filtered_by_metadata")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_samples_filtered_by_metadata_route_stop_injection(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ["sample1", "sample2"]
        mocked_jsoncall.return_value = ""
        fakeDB = MagicMock()
        fakeDB.get_samples_filtered_by_metadata = MagicMock(return_value=[])
        for looks_iffy_to_me_guv in [
            'serotype="Ia"; DO something NASTY; --',
            "actually anything with -- in it",
            "no semi; colons either",
            "wildcards % are right out",
        ]:
            under_test = mar.get_samples_filtered_by_metadata_route(
                [{"name": looks_iffy_to_me_guv, "values": ["any search term"]}], fakeDB
            )
            self.assertEqual(under_test[1], 400)

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService.get_lanes_filtered_by_in_silico_data")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_lanes_filtered_by_in_silico_data_route_jsonified(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ["lane1", "lane2"]
        mocked_jsoncall.return_value = "expected"
        fakeDB = MagicMock()
        fakeDB.get_lanes_filtered_by_in_silico_data = MagicMock(return_value=["lane1", "lane2"])
        under_test = mar.get_lanes_filtered_by_in_silico_data_route([{"name": "ST", "values": ["14"]}], fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ("expected", 200))

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService.get_lanes_filtered_by_in_silico_data")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_lanes_filtered_by_in_silico_data_route_no_return(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = []
        mocked_jsoncall.return_value = ""
        fakeDB = MagicMock()
        fakeDB.get_lanes_filtered_by_in_silico_data = MagicMock(return_value=[])
        under_test = mar.get_lanes_filtered_by_in_silico_data_route([{"name": "ST", "values": ["None"]}], fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ("", 404))

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_lanes_filtered_by_in_silico_data_route_bad_field_name(self, mocked_jsoncall, dao_mock):
        mock_field_name = "bad_field_name"
        mock_values = ["anything"]
        mock_json = ""
        mocked_jsoncall.return_value = mock_json
        dao_mock.get_lanes_filtered_by_in_silico_data.return_value = None
        filtered_samples, http_status = mar.get_lanes_filtered_by_in_silico_data_route(
            [{"name": mock_field_name, "values": mock_values}], dao_mock
        )
        dao_mock.get_lanes_filtered_by_in_silico_data.assert_called_once_with({mock_field_name: mock_values})
        self.assertEqual(filtered_samples, "Invalid field name provided")
        self.assertEqual(http_status, 400)

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService.get_lanes_filtered_by_in_silico_data")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_lanes_filtered_by_in_silico_data_route_stop_injection(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ["lane1", "lane2"]
        mocked_jsoncall.return_value = ""
        fakeDB = MagicMock()
        fakeDB.get_lanes_filtered_by_in_silico_data = MagicMock(return_value=[])
        for looks_iffy_to_me_guv in [
            'ST="Ia"; DO something NASTY; --',
            "actually anything with -- in it",
            "no semi; colons either",
            "wildcards % are right out",
        ]:
            under_test = mar.get_lanes_filtered_by_in_silico_data_route(
                [{"name": looks_iffy_to_me_guv, "values": ["any search term"]}], fakeDB
            )
            self.assertEqual(under_test[1], 400)

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_distinct_values_route(self, mocked_jsoncall, dao_mock):
        mock_query = {"fields": ["field1", "field2"], "institutions": ["institutionA"]}
        mock_response = {}
        mock_json = "expected"
        mocked_jsoncall.return_value = mock_json
        dao_mock.get_distinct_values.return_value = mock_response
        distinct_values, http_status = mar.get_distinct_values_route(mock_query, dao_mock)
        dao_mock.get_distinct_values.assert_called_once_with(
            "metadata", mock_query["fields"], mock_query["institutions"]
        )
        self.assertEqual(distinct_values, mock_json)
        self.assertEqual(http_status, 200)

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_distinct_values_route_no_return(self, mocked_jsoncall, dao_mock):
        mock_query = {"fields": ["field1", "field2"], "institutions": ["institutionA"]}
        mock_response = {}
        mock_json = ""
        mocked_jsoncall.return_value = mock_json
        dao_mock.get_distinct_values.return_value = mock_response
        distinct_values, http_status = mar.get_distinct_values_route(mock_query, dao_mock)
        dao_mock.get_distinct_values.assert_called_once_with(
            "metadata", mock_query["fields"], mock_query["institutions"]
        )
        self.assertEqual(distinct_values, mock_json)
        self.assertEqual(http_status, 200)

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_distinct_values_route_bad_field(self, mocked_jsoncall, dao_mock):
        mock_query = {"fields": ["anything"], "institutions": ["anything"]}
        mock_json = ""
        mocked_jsoncall.return_value = mock_json
        dao_mock.get_distinct_values.return_value = None
        distinct_values, http_status = mar.get_distinct_values_route(mock_query, dao_mock)
        dao_mock.get_distinct_values.assert_called_once_with(
            "metadata", mock_query["fields"], mock_query["institutions"]
        )
        self.assertEqual(distinct_values, "Invalid field name provided")
        self.assertEqual(http_status, 404)

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService")
    def test_get_distinct_values_route_stop_injection(self, dao_mock):
        mock_response = {}
        dao_mock.get_distinct_values.return_value = mock_response
        for looks_iffy_to_me_guv in [
            'serotype="Ia"; DO something NASTY; --',
            "actually anything with -- in it",
            "no semi; colons either",
            "wildcards % are right out",
        ]:
            under_test = mar.get_distinct_values_route(
                {"fields": [looks_iffy_to_me_guv], "institutions": ["institutionA"]}, dao_mock
            )
            self.assertEqual(under_test, ("Invalid arguments provided", 400))

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_distinct_in_silico_values_route(self, mocked_jsoncall, dao_mock):
        mock_query = {"fields": ["field1", "field2"], "institutions": ["institutionA"]}
        mock_response = {}
        mock_json = "expected"
        mocked_jsoncall.return_value = mock_json
        dao_mock.get_distinct_values.return_value = mock_response
        distinct_values, http_status = mar.get_distinct_in_silico_values_route(mock_query, dao_mock)
        dao_mock.get_distinct_values.assert_called_once_with(
            "in silico", mock_query["fields"], mock_query["institutions"]
        )
        self.assertEqual(distinct_values, mock_json)
        self.assertEqual(http_status, 200)

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_distinct_in_silico_values_route_no_return(self, mocked_jsoncall, dao_mock):
        mock_query = {"fields": ["field1", "field2"], "institutions": ["institutionA"]}
        mock_response = {}
        mock_json = ""
        mocked_jsoncall.return_value = mock_json
        dao_mock.get_distinct_values.return_value = mock_response
        distinct_values, http_status = mar.get_distinct_in_silico_values_route(mock_query, dao_mock)
        dao_mock.get_distinct_values.assert_called_once_with(
            "in silico", mock_query["fields"], mock_query["institutions"]
        )
        self.assertEqual(distinct_values, mock_json)
        self.assertEqual(http_status, 200)

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_distinct_in_silico_values_route_bad_field(self, mocked_jsoncall, dao_mock):
        mock_query = {"fields": ["anything"], "institutions": ["anything"]}
        mock_json = ""
        mocked_jsoncall.return_value = mock_json
        dao_mock.get_distinct_values.return_value = None
        distinct_values, http_status = mar.get_distinct_in_silico_values_route(mock_query, dao_mock)
        dao_mock.get_distinct_values.assert_called_once_with(
            "in silico", mock_query["fields"], mock_query["institutions"]
        )
        self.assertEqual(distinct_values, "Invalid field name provided")
        self.assertEqual(http_status, 404)

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService")
    def test_get_distinct_in_silico_values_route_stop_injection(self, dao_mock):
        mock_response = {}
        dao_mock.get_distinct_values.return_value = mock_response
        for looks_iffy_to_me_guv in [
            'serotype="Ia"; DO something NASTY; --',
            "actually anything with -- in it",
            "no semi; colons either",
            "wildcards % are right out",
        ]:
            under_test = mar.get_distinct_in_silico_values_route(
                {"fields": [looks_iffy_to_me_guv], "institutions": ["institutionA"]}, dao_mock
            )
            self.assertEqual(under_test, ("Invalid arguments provided", 400))

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_distinct_qc_data_values_route(self, mocked_jsoncall, dao_mock):
        mock_query = {"fields": ["field1", "field2"], "institutions": ["institutionA"]}
        mock_response = {}
        mock_json = "expected"
        mocked_jsoncall.return_value = mock_json
        dao_mock.get_distinct_values.return_value = mock_response
        distinct_values, http_status = mar.get_distinct_qc_data_values_route(mock_query, dao_mock)
        dao_mock.get_distinct_values.assert_called_once_with(
            "qc data", mock_query["fields"], mock_query["institutions"]
        )
        self.assertEqual(distinct_values, mock_json)
        self.assertEqual(http_status, 200)

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_distinct_qc_data_values_route_no_return(self, mocked_jsoncall, dao_mock):
        mock_query = {"fields": ["field1", "field2"], "institutions": ["institutionA"]}
        mock_response = {}
        mock_json = ""
        mocked_jsoncall.return_value = mock_json
        dao_mock.get_distinct_values.return_value = mock_response
        distinct_values, http_status = mar.get_distinct_qc_data_values_route(mock_query, dao_mock)
        dao_mock.get_distinct_values.assert_called_once_with(
            "qc data", mock_query["fields"], mock_query["institutions"]
        )
        self.assertEqual(distinct_values, mock_json)
        self.assertEqual(http_status, 200)

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_distinct_qc_data_values_route_bad_field(self, mocked_jsoncall, dao_mock):
        mock_query = {"fields": ["anything"], "institutions": ["anything"]}
        mock_json = ""
        mocked_jsoncall.return_value = mock_json
        dao_mock.get_distinct_values.return_value = None
        distinct_values, http_status = mar.get_distinct_qc_data_values_route(mock_query, dao_mock)
        dao_mock.get_distinct_values.assert_called_once_with(
            "qc data", mock_query["fields"], mock_query["institutions"]
        )
        self.assertEqual(distinct_values, "Invalid field name provided")
        self.assertEqual(http_status, 404)

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService")
    def test_get_distinct_qc_data_values_route_stop_injection(self, dao_mock):
        mock_response = {}
        dao_mock.get_distinct_values.return_value = mock_response
        for looks_iffy_to_me_guv in [
            'serotype="Ia"; DO something NASTY; --',
            "actually anything with -- in it",
            "no semi; colons either",
            "wildcards % are right out",
        ]:
            under_test = mar.get_distinct_qc_data_values_route(
                {"fields": [looks_iffy_to_me_guv], "institutions": ["institutionA"]}, dao_mock
            )
            self.assertEqual(under_test, ("Invalid arguments provided", 400))

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService.get_institutions")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_institutions_jsonified(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ["ints1", "inst2"]
        mocked_jsoncall.return_value = "expected"
        fakeDB = MagicMock()
        fakeDB.get_institutions = MagicMock(return_value=["inst1", "inst2"])
        under_test = mar.get_institutions(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ("expected", 200))

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService.get_institutions")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_institutions_not_returned(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = []
        mocked_jsoncall.return_value = ""
        fakeDB = MagicMock()
        fakeDB.get_institutions = MagicMock(return_value=[])
        under_test = mar.get_institutions(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ("", 404))

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService.get_institution_names")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_institution_names_route_jsonified(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = ["ints1", "inst2"]
        mocked_jsoncall.return_value = "expected"
        fakeDB = MagicMock()
        fakeDB.get_institution_names = MagicMock(return_value=["ints1", "inst2"])
        under_test = mar.get_institution_names_route(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ("expected", 200))

    @patch("metadata.api.database.monocle_database_service.MonocleDatabaseService.get_institution_names")
    @patch("metadata.api.routes.convert_to_json")
    def test_get_institution_names_route_not_returned(self, mocked_jsoncall, mocked_query):
        mocked_query.return_value = []
        mocked_jsoncall.return_value = ""
        fakeDB = MagicMock()
        fakeDB.get_institution_names = MagicMock(return_value=[])
        under_test = mar.get_institution_names_route(fakeDB)
        mocked_jsoncall.assert_called_once()
        self.assertEqual(under_test, ("", 404))
