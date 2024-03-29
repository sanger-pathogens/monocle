import json
import unittest
import urllib
from http import HTTPStatus
from os import environ
from pathlib import Path
from unittest.mock import Mock, call, patch

from dash.api import exceptions, routes
from dash.api.service.service_factory import ServiceFactory
from flask import Response


class TestRoutes(unittest.TestCase):
    """Test class for the routes module"""

    # this has mock values for the environment variables set by docker-compose
    MOCK_ENVIRONMENT = {
        "JUNO_DATA_INSTITUTION_VIEW": "dash/tests/mock_data/s3",
        "AUTH_COOKIE_NAME": "mock_auth_cookie_name",
    }

    MOCK_PROJECT_ID = "juno"

    # For the purposes of testing it doesn't matter what the service call return dictionary looks like
    # so we'll make the contents abstract and simple
    SERVICE_CALL_RETURN_DATA = {"field1": "value1"}
    SERVICE_CALL_RETURN_CSV_FILENAME = "myfile.csv"
    SERVICE_CALL_RETURN_CSV_DATA = {
        "success": True,
        "filename": SERVICE_CALL_RETURN_CSV_FILENAME,
        "content": "a,csv,string",
    }
    SERVICE_CALL_RETURN_CSV_NOT_FOUND = {"success": False, "error": "not found"}
    TEST_USER = "fbloggs"
    TEST_HOST_NAME = "mock.host"
    TEST_AUTH_TOKEN = "ZmJsb2dnczpmb29iYXI="  # base64 encoded 'fbloggs:foobar'

    EXPECTED_PROGRESS_RESULTS = {"progress_graph": {"data": SERVICE_CALL_RETURN_DATA}}

    EXPECTED_CSV_CONTENT_TYPE = "text/csv; charset=UTF-8"
    EXPECTED_CONTENT_DISPOSITION = 'attachment; filename="{}"'.format(SERVICE_CALL_RETURN_CSV_FILENAME)

    def setUp(self) -> None:
        ServiceFactory.TEST_MODE = True

    @patch.dict(environ, MOCK_ENVIRONMENT, clear=True)
    @patch("flask.Response.set_cookie")
    @patch("dash.api.routes.call_request_headers")
    @patch.object(ServiceFactory, "authentication_service")
    def test_set_auth_cookie_route(self, auth_service_mock, request_headers_mock, set_cookie_mock):
        # Given
        mock_auth_token = "abcde1234"
        mock_redirect_url = "/mock/redirect/url"
        request_headers_mock.return_value = {"X-Target": mock_redirect_url}
        auth_service_mock.return_value.get_auth_token.return_value = mock_auth_token
        # When
        result = routes.set_auth_cookie_route({"username": "any name", "password": "anything"})
        # Then
        set_cookie_mock.assert_called_once_with(
            self.MOCK_ENVIRONMENT["AUTH_COOKIE_NAME"], value=mock_auth_token.encode("utf8"), max_age=None
        )
        self.assertIsInstance(result, Response)
        self.assertEqual(result.content_type, "application/json; charset=UTF-8")
        self.assertEqual(result.status_code, HTTPStatus.TEMPORARY_REDIRECT)
        self.assertIsNotNone(result.headers.get("Location"))
        self.assertEqual(result.headers.get("Location"), mock_redirect_url)

    def test_set_auth_cookie_route_reject_missing_param(self):
        with self.assertRaises(KeyError):
            routes.set_auth_cookie_route({"this is a bad key": "any name", "password": "anything"})

    @patch.dict(environ, MOCK_ENVIRONMENT, clear=True)
    @patch("flask.Response.set_cookie")
    @patch("dash.api.routes.call_request_headers")
    def test_delete_auth_cookie_route(self, request_headers_mock, set_cookie_mock):
        # Given
        mock_redirect_url = "/mock/redirect/url"
        request_headers_mock.return_value = {"X-Target": mock_redirect_url}
        # When
        result = routes.delete_auth_cookie_route()
        # Then
        set_cookie_mock.assert_called_once_with(self.MOCK_ENVIRONMENT["AUTH_COOKIE_NAME"], value="", expires=0)
        self.assertIsInstance(result, Response)
        self.assertEqual(result.content_type, "application/json; charset=UTF-8")
        self.assertEqual(result.status_code, HTTPStatus.TEMPORARY_REDIRECT)
        self.assertIsNotNone(result.headers.get("Location"))
        self.assertEqual(result.headers.get("Location"), mock_redirect_url)

    @patch("dash.api.routes.call_jsonify")
    @patch("dash.api.routes.get_authenticated_username")
    @patch.object(ServiceFactory, "user_service")
    def test_get_user_details_route(self, user_service_mock, username_mock, resp_mock):
        # Given
        user_service_mock.return_value.user_details = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        # When
        result = routes.get_user_details_route()
        # Then
        user_service_mock.assert_called_once_with(self.TEST_USER)
        resp_mock.assert_called_once_with({"user_details": self.SERVICE_CALL_RETURN_DATA})
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 1)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch("dash.api.routes.call_jsonify")
    @patch("dash.api.routes.get_authenticated_username")
    @patch.object(ServiceFactory, "sample_tracking_service")
    def test_get_batches_route(self, sample_tracking_service_mock, username_mock, resp_mock):
        # Given
        sample_tracking_service_mock.return_value.get_batches.return_value = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        # When
        result = routes.get_batches_route()
        # Then
        sample_tracking_service_mock.assert_called_once_with(self.TEST_USER)
        sample_tracking_service_mock.return_value.get_batches.assert_called_once()
        resp_mock.assert_called_once_with({"batches": self.SERVICE_CALL_RETURN_DATA})
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch("dash.api.routes.call_jsonify")
    @patch("dash.api.routes.get_authenticated_username")
    @patch.object(ServiceFactory, "sample_tracking_service")
    def test_get_institutions_route(self, sample_tracking_service_mock, username_mock, resp_mock):
        # Given
        sample_tracking_service_mock.return_value.get_institutions.return_value = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        # When
        result = routes.get_institutions_route()
        # Then
        sample_tracking_service_mock.assert_called_once_with(self.TEST_USER)
        sample_tracking_service_mock.return_value.get_institutions.assert_called_once()
        resp_mock.assert_called_once_with({"institutions": self.SERVICE_CALL_RETURN_DATA})
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch("dash.api.routes.call_jsonify")
    @patch("dash.api.routes.get_authenticated_username")
    @patch.object(ServiceFactory, "sample_tracking_service")
    def test_get_progress_route(self, sample_tracking_service_mock, username_mock, resp_mock):
        # Given
        sample_tracking_service_mock.return_value.get_progress.return_value = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        # When
        result = routes.get_progress_route()
        # Then
        sample_tracking_service_mock.assert_called_once_with(self.TEST_USER)
        sample_tracking_service_mock.return_value.get_progress.assert_called_once()
        resp_mock.assert_called_once_with(self.EXPECTED_PROGRESS_RESULTS)
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch("dash.api.routes.call_jsonify")
    @patch("dash.api.routes.get_authenticated_username")
    @patch.object(ServiceFactory, "sample_tracking_service")
    def test_sequencing_status_summary_route(self, sample_tracking_service_mock, username_mock, resp_mock):
        # Given
        sample_tracking_service_mock.return_value.sequencing_status_summary.return_value = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        # When
        result = routes.sequencing_status_summary_route()
        # Then
        sample_tracking_service_mock.assert_called_once_with(self.TEST_USER)
        sample_tracking_service_mock.return_value.sequencing_status_summary.assert_called_once()
        resp_mock.assert_called_once_with({"sequencing_status": self.SERVICE_CALL_RETURN_DATA})
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch("dash.api.routes.call_jsonify")
    @patch("dash.api.routes.get_authenticated_username")
    @patch.object(ServiceFactory, "sample_tracking_service")
    def test_project_route(self, sample_tracking_service_mock, username_mock, resp_mock):
        expected_project_data = "some project data"
        sample_tracking_service_mock.return_value.project_information.return_value = expected_project_data
        username_mock.return_value = self.TEST_USER

        result = routes.project_route()

        sample_tracking_service_mock.assert_called_once_with(self.TEST_USER)
        sample_tracking_service_mock.return_value.project_information.assert_called_once()
        resp_mock.assert_called_once_with({"project": expected_project_data})
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch("dash.api.routes.call_jsonify")
    @patch("dash.api.routes.get_authenticated_username")
    @patch.object(ServiceFactory, "sample_tracking_service")
    def test_pipeline_status_summary_route(self, sample_tracking_service_mock, username_mock, resp_mock):
        # Given
        sample_tracking_service_mock.return_value.pipeline_status_summary.return_value = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        # When
        result = routes.pipeline_status_summary_route()
        # Then
        sample_tracking_service_mock.assert_called_once_with(self.TEST_USER)
        sample_tracking_service_mock.return_value.pipeline_status_summary.assert_called_once()
        resp_mock.assert_called_once_with({"pipeline_status": self.SERVICE_CALL_RETURN_DATA})
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch("dash.api.routes.call_jsonify")
    @patch("dash.api.routes.get_authenticated_username")
    @patch("dash.api.routes.get_authenticated_project")
    @patch.object(ServiceFactory, "sample_data_service")
    def test_get_bulk_download_info_route(self, sample_data_service_mock, project_mock, username_mock, resp_mock):
        # Given
        batches = self.SERVICE_CALL_RETURN_DATA
        assemblies = False
        annotations = True
        expected_payload = "paylod"
        sample_data_service_mock.return_value.get_bulk_download_info.return_value = expected_payload
        username_mock.return_value = self.TEST_USER
        project_mock.return_value = self.MOCK_PROJECT_ID
        # When
        result = routes.bulk_download_info_route(
            {"sample filters": {"batches": batches}, "assemblies": assemblies, "annotations": annotations}
        )
        # Then
        sample_data_service_mock.assert_called_once_with(self.TEST_USER)
        sample_data_service_mock.return_value.get_bulk_download_info.assert_called_once_with(
            {"batches": batches}, assemblies=assemblies, annotations=annotations, reads=False
        )
        resp_mock.assert_called_once_with(expected_payload)
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch("dash.api.routes.get_authenticated_username")
    @patch.object(ServiceFactory, "sample_data_service")
    def test_get_bulk_download_info_route_return_404(self, sample_data_service_mock, username_mock):
        # Given
        batches = self.SERVICE_CALL_RETURN_DATA
        sample_filters = {"batches": batches}
        username_mock.return_value = self.TEST_USER
        sample_data_service_mock.return_value.get_bulk_download_info.return_value = None
        # When
        result = routes.bulk_download_info_route({"sample filters": sample_filters})
        # Then
        sample_data_service_mock.assert_called_with(self.TEST_USER)
        self.assertIsInstance(result, Response)
        self.assertIn(str(HTTPStatus.NOT_FOUND.value), result.status)

    @patch("dash.api.routes.get_authenticated_username")
    @patch.object(ServiceFactory, "sample_data_service")
    def test_get_bulk_download_info_route_return_404_no_assemblies(self, sample_data_service_mock, username_mock):
        # Given
        batches = self.SERVICE_CALL_RETURN_DATA
        assemblies = False
        annotations = True
        sample_data_service_mock.return_value.get_bulk_download_info.return_value = None
        username_mock.return_value = self.TEST_USER
        # When
        result = routes.bulk_download_info_route(
            {"sample filters": {"batches": batches}, "assemblies": assemblies, "annotations": annotations}
        )
        # Then
        sample_data_service_mock.assert_called_once_with(self.TEST_USER)
        self.assertIsInstance(result, Response)
        self.assertIn(str(HTTPStatus.NOT_FOUND.value), result.status)

    @patch("dash.api.routes.get_authenticated_username")
    @patch.object(ServiceFactory, "sample_data_service")
    def test_get_bulk_download_info_route_return_400(self, sample_data_service_mock, username_mock):
        # Given
        batches = self.SERVICE_CALL_RETURN_DATA
        sample_filters = {"batches": batches}
        username_mock.return_value = self.TEST_USER
        sample_data_service_mock.return_value.get_bulk_download_info.side_effect = urllib.error.HTTPError(
            "/nowhere", "400", "blah blah Invalid field blah blah", "yes", "no"
        )
        # When
        result = routes.bulk_download_info_route({"sample filters": sample_filters})
        # Then
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.BAD_REQUEST)

    @patch.dict(environ, MOCK_ENVIRONMENT, clear=True)
    @patch("dash.api.routes.call_jsonify")
    @patch("dash.api.routes.get_authenticated_username")
    @patch("dash.api.routes.get_authenticated_project")
    @patch("dash.api.routes.uuid4")
    @patch.object(ServiceFactory, "sample_data_service")
    @patch("pathlib.Path.is_dir")
    @patch("dash.api.routes.write_text_file")
    def test_get_bulk_download_urls_route(
        self,
        write_text_file_mock,
        is_dir_mock,
        sample_data_service_mock,
        uuid4_mock,
        project_mock,
        username_mock,
        resp_mock,
    ):
        # Given
        batches = ["2020-09-04", "2021-01-30"]
        assemblies = False
        annotations = True
        samples = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        project_mock.return_value = self.MOCK_PROJECT_ID
        sample_data_service_mock.return_value.get_filtered_samples.return_value = samples
        is_dir_mock.return_value = True
        uuid_hex = "123"
        uuid4_mock.return_value.hex = uuid_hex
        download_param_filename = "{}.params.json".format(uuid_hex)
        write_text_file_mock.return_value = download_param_filename
        download_param_location = "some/dir"
        download_route = "/data_download_route"
        download_max_samples_per_zip = 100  # any number exceeding items in lane_files is OK
        sample_data_service_mock.return_value.get_bulk_download_location.return_value = download_param_location
        sample_data_service_mock.return_value.get_bulk_download_route.return_value = download_route
        sample_data_service_mock.return_value.get_bulk_download_max_samples_per_zip.return_value = (
            download_max_samples_per_zip
        )
        sample_data_service_mock.return_value.get_bulk_download_max_samples_per_download.return_value = 2000
        lane_files = {
            "pubname": [
                "/".join([environ["JUNO_DATA_INSTITUTION_VIEW"], "lane file"]),
                "/".join([environ["JUNO_DATA_INSTITUTION_VIEW"], "another lane file"]),
            ]
        }
        sample_data_service_mock.return_value.get_public_name_to_lane_files_dict.return_value = lane_files
        expected_payload = {"download_urls": [f"{download_route}/{uuid_hex}"], "num_samples_restricted_to": None}
        # When
        result = routes.bulk_download_urls_route(
            {"sample filters": {"batches": batches}, "assemblies": assemblies, "annotations": annotations}
        )
        # Then
        sample_data_service_mock.assert_called_once_with(self.TEST_USER)
        sample_data_service_mock.return_value.get_bulk_download_route.assert_called_once()
        resp_mock.assert_called_once_with(expected_payload)
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch.dict(environ, MOCK_ENVIRONMENT, clear=True)
    @patch("dash.api.routes.call_jsonify")
    @patch("dash.api.routes.get_authenticated_username")
    @patch("dash.api.routes.get_authenticated_project")
    @patch("dash.api.routes.uuid4")
    @patch.object(ServiceFactory, "sample_data_service")
    @patch("pathlib.Path.is_dir")
    @patch("dash.api.routes.write_text_file")
    def test_get_bulk_download_urls_route_multiple_urls(
        self,
        write_text_file_mock,
        is_dir_mock,
        sample_data_service_mock,
        uuid4_mock,
        project_mock,
        username_mock,
        resp_mock,
    ):
        # Given
        batches = ["2020-09-04", "2021-01-30"]
        assemblies = False
        annotations = True
        samples = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        project_mock.return_value = self.MOCK_PROJECT_ID
        sample_data_service_mock.return_value.get_filtered_samples.return_value = samples
        is_dir_mock.return_value = True
        uuid_hex = "123"
        uuid4_mock.return_value.hex = uuid_hex
        download_param_filename = "{}.params.json".format(uuid_hex)
        write_text_file_mock.return_value = download_param_filename
        download_param_location = "some/dir"
        download_route = "/data_download_route"
        download_max_samples_per_zip = 3
        sample_data_service_mock.return_value.get_bulk_download_location.return_value = download_param_location
        sample_data_service_mock.return_value.get_bulk_download_route.return_value = download_route
        sample_data_service_mock.return_value.get_bulk_download_max_samples_per_zip.return_value = (
            download_max_samples_per_zip
        )
        sample_data_service_mock.return_value.get_bulk_download_max_samples_per_download.return_value = 2000
        lane_files = {}
        for i in range((download_max_samples_per_zip * 2) + 1):  # will create enough items to require 3 download URLs
            lane_files["pubname_{}".format(i)] = [
                "/".join([self.MOCK_ENVIRONMENT["JUNO_DATA_INSTITUTION_VIEW"], "lane file for pubname_{}".format(i)]),
                "/".join(
                    [self.MOCK_ENVIRONMENT["JUNO_DATA_INSTITUTION_VIEW"], "another lane file for pubname_{}".format(i)]
                ),
            ]
        sample_data_service_mock.return_value.get_public_name_to_lane_files_dict.return_value = lane_files
        expected_payload = {
            # this should have 3 values in array
            "download_urls": [
                f"{download_route}/{uuid_hex}",
                f"{download_route}/{uuid_hex}",
                f"{download_route}/{uuid_hex}",
            ],
            "num_samples_restricted_to": None,
        }
        # When
        result = routes.bulk_download_urls_route(
            {"sample filters": {"batches": batches}, "assemblies": assemblies, "annotations": annotations}
        )
        # Then
        sample_data_service_mock.assert_called_once_with(self.TEST_USER)
        # should be called 3 times
        sample_data_service_mock.return_value.get_bulk_download_route.assert_has_calls([call(), call(), call()])
        resp_mock.assert_called_once_with(expected_payload)
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch.dict(environ, MOCK_ENVIRONMENT, clear=True)
    @patch("dash.api.routes.call_jsonify")
    @patch("dash.api.routes.get_authenticated_username")
    @patch("dash.api.routes.get_authenticated_project")
    @patch("dash.api.routes.uuid4")
    @patch.object(ServiceFactory, "sample_data_service")
    @patch("pathlib.Path.is_dir")
    @patch("dash.api.routes.write_text_file")
    def test_get_bulk_download_urls_route_multiple_urls_restricted_sample_num(
        self,
        write_text_file_mock,
        is_dir_mock,
        sample_data_service_mock,
        uuid4_mock,
        project_mock,
        username_mock,
        resp_mock,
    ):
        # Given
        batches = ["2020-09-04", "2021-01-30"]
        assemblies = False
        annotations = True
        samples = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        project_mock.return_value = self.MOCK_PROJECT_ID
        sample_data_service_mock.return_value.get_filtered_samples.return_value = [samples, samples]
        is_dir_mock.return_value = True
        uuid_hex = "123"
        uuid4_mock.return_value.hex = uuid_hex
        download_param_filename = "{}.params.json".format(uuid_hex)
        write_text_file_mock.return_value = download_param_filename
        download_param_location = "some/dir"
        download_route = "/data_download_route"
        download_max_samples_per_download = 1
        download_max_samples_per_zip = 3
        sample_data_service_mock.return_value.get_bulk_download_location.return_value = download_param_location
        sample_data_service_mock.return_value.get_bulk_download_route.return_value = download_route
        sample_data_service_mock.return_value.get_bulk_download_max_samples_per_zip.return_value = (
            download_max_samples_per_zip
        )
        sample_data_service_mock.return_value.get_bulk_download_max_samples_per_download.return_value = (
            download_max_samples_per_download
        )
        lane_files = {}
        for i in range((download_max_samples_per_zip * 2) + 1):  # will create enough items to require 3 download URLs
            lane_files["pubname_{}".format(i)] = [
                "/".join([self.MOCK_ENVIRONMENT["JUNO_DATA_INSTITUTION_VIEW"], "lane file for pubname_{}".format(i)]),
                "/".join(
                    [self.MOCK_ENVIRONMENT["JUNO_DATA_INSTITUTION_VIEW"], "another lane file for pubname_{}".format(i)]
                ),
            ]
        sample_data_service_mock.return_value.get_public_name_to_lane_files_dict.return_value = lane_files
        expected_payload = {
            # this should have 3 values in array
            "download_urls": [
                f"{download_route}/{uuid_hex}",
                f"{download_route}/{uuid_hex}",
                f"{download_route}/{uuid_hex}",
            ],
            "num_samples_restricted_to": download_max_samples_per_download,
        }
        # When
        result = routes.bulk_download_urls_route(
            {"sample filters": {"batches": batches}, "assemblies": assemblies, "annotations": annotations}
        )
        # Then
        sample_data_service_mock.assert_called_once_with(self.TEST_USER)
        # should be called 3 times
        sample_data_service_mock.return_value.get_bulk_download_route.assert_has_calls([call(), call(), call()])
        resp_mock.assert_called_once_with(expected_payload)
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch.dict(environ, MOCK_ENVIRONMENT, clear=True)
    @patch("dash.api.routes.call_jsonify")
    @patch("dash.api.routes.get_authenticated_username")
    @patch("dash.api.routes.get_authenticated_project")
    @patch("dash.api.routes.uuid4")
    @patch.object(ServiceFactory, "sample_data_service")
    @patch("pathlib.Path.is_dir")
    @patch("dash.api.routes.write_text_file")
    def test_get_bulk_download_urls_route_api_property_defines_number_urls(
        self,
        write_text_file_mock,
        is_dir_mock,
        sample_data_service_mock,
        uuid4_mock,
        project_mock,
        username_mock,
        resp_mock,
    ):
        # Given
        batches = ["2020-09-04", "2021-01-30"]
        assemblies = False
        annotations = True
        samples = self.SERVICE_CALL_RETURN_DATA
        username_mock.return_value = self.TEST_USER
        project_mock.return_value = self.MOCK_PROJECT_ID
        sample_data_service_mock.return_value.get_filtered_samples.return_value = samples
        is_dir_mock.return_value = True
        uuid_hex = "123"
        uuid4_mock.return_value.hex = uuid_hex
        download_param_filename = "{}.params.json".format(uuid_hex)
        write_text_file_mock.return_value = download_param_filename
        download_param_location = "some/dir"
        download_route = "/data_download_route"
        download_max_samples_per_zip = 3
        sample_data_service_mock.return_value.get_bulk_download_location.return_value = download_param_location
        sample_data_service_mock.return_value.get_bulk_download_route.return_value = download_route
        sample_data_service_mock.return_value.get_bulk_download_max_samples_per_download.return_value = 2000
        lane_files = {}
        for i in range((download_max_samples_per_zip * 2) + 1):  # will create enough items to require 3 download URLs
            lane_files["pubname_{}".format(i)] = [
                "/".join([self.MOCK_ENVIRONMENT["JUNO_DATA_INSTITUTION_VIEW"], "lane file for pubname_{}".format(i)]),
                "/".join(
                    [self.MOCK_ENVIRONMENT["JUNO_DATA_INSTITUTION_VIEW"], "another lane file for pubname_{}".format(i)]
                ),
            ]
        sample_data_service_mock.return_value.get_public_name_to_lane_files_dict.return_value = lane_files
        expected_payload = {
            # this should have 3 values in array
            "download_urls": [
                f"{download_route}/{uuid_hex}",
                f"{download_route}/{uuid_hex}",
                f"{download_route}/{uuid_hex}",
            ],
            "num_samples_restricted_to": None,
        }
        # When
        result = routes.bulk_download_urls_route(
            {
                "sample filters": {"batches": batches},
                "assemblies": assemblies,
                "annotations": annotations,
                "max samples per zip": download_max_samples_per_zip,
            }
        )
        # Then
        sample_data_service_mock.assert_called_once_with(self.TEST_USER)
        # should be called 3 times
        sample_data_service_mock.return_value.get_bulk_download_route.assert_has_calls([call(), call(), call()])
        resp_mock.assert_called_once_with(expected_payload)
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch("dash.api.routes.get_authenticated_username")
    @patch.object(ServiceFactory, "sample_data_service")
    def test_get_bulk_download_urls_route_return_400(self, sample_data_service_mock, username_mock):
        # Given
        batches = self.SERVICE_CALL_RETURN_DATA
        sample_filters = {"batches": batches}
        username_mock.return_value = self.TEST_USER
        sample_data_service_mock.side_effect = urllib.error.HTTPError(
            "/nowhere", "400", "blah blah Invalid field blah blah", "yes", "no"
        )
        # When
        result = routes.bulk_download_urls_route({"sample filters": sample_filters})
        # Then
        self.assertIsNotNone(result)
        self.assertTrue(len(result), 2)
        self.assertEqual(result[1], HTTPStatus.BAD_REQUEST)

    @patch.dict(environ, MOCK_ENVIRONMENT, clear=True)
    @patch("dash.api.routes.get_authenticated_username")
    @patch("dash.api.routes.get_authenticated_project")
    @patch("dash.api.routes.zip_files")
    @patch.object(ServiceFactory, "sample_data_service")
    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.is_file")
    @patch("dash.api.routes.read_text_file")
    @patch("dash.api.routes.call_request_headers")
    @patch("dash.api.routes.call_request_args")
    def test_data_download_route(
        self,
        request_args_mock,
        request_headers_mock,
        read_text_file_mock,
        is_file_mock,
        is_dir_mock,
        sample_data_service_mock,
        zip_files_mock,
        project_mock,
        username_mock,
    ):
        # Given
        mock_host = "mock_host.sanger.ac.uk"
        request_args_mock.return_value = {}
        request_headers_mock.return_value = {"X-Forwarded-Host": mock_host, "X-Forwarded-Port": "443"}
        username_mock.return_value = self.TEST_USER
        project_mock.return_value = self.MOCK_PROJECT_ID
        is_dir_mock.return_value = True
        # assigning list to side_effect returns next value each time mocked function is called
        # => mocks non-existence of the ZIP archive, followed by existence of JSON file with params
        is_file_mock.side_effect = [False, True]
        lane_files = {"pubname": ["/lane file", "/another lane file"]}
        files_to_zip = {
            "pubname": [
                Path(self.MOCK_ENVIRONMENT["JUNO_DATA_INSTITUTION_VIEW"], "lane file"),
                Path(self.MOCK_ENVIRONMENT["JUNO_DATA_INSTITUTION_VIEW"], "another lane file"),
            ]
        }
        read_text_file_mock.return_value = json.dumps(lane_files)
        mock_token = "123"
        zip_file_basename = mock_token
        zip_file_location = "some/dir"
        sample_data_service_mock.return_value.get_bulk_download_location.return_value = zip_file_location
        download_host = mock_host
        download_symlink = "downloads/"
        sample_data_service_mock.return_value.make_download_symlink.return_value = download_symlink
        # When
        result = routes.data_download_route(mock_token)
        # Then
        sample_data_service_mock.assert_called_once_with(self.TEST_USER)
        zip_files_mock.assert_called_once_with(files_to_zip, basename=zip_file_basename, location=zip_file_location)
        sample_data_service_mock.return_value.make_download_symlink.assert_called_once_with(cross_institution=True)
        self.assertIsInstance(result, Response)
        self.assertIn(str(HTTPStatus.SEE_OTHER.value), result.status)
        self.assertEqual(
            "https://{}/{}{}.zip".format(download_host, download_symlink, mock_token), result.headers["Location"]
        )

    @patch.dict(environ, MOCK_ENVIRONMENT, clear=True)
    @patch("dash.api.routes.get_authenticated_username")
    @patch("dash.api.routes.get_authenticated_project")
    @patch("dash.api.routes.zip_files")
    @patch.object(ServiceFactory, "sample_data_service")
    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.is_file")
    @patch("dash.api.routes.read_text_file")
    @patch("dash.api.routes.call_request_headers")
    @patch("dash.api.routes.call_request_args")
    @patch("dash.api.routes.call_jsonify")
    def test_data_download_route_no_redirect(
        self,
        resp_mock,
        request_args_mock,
        request_headers_mock,
        read_text_file_mock,
        is_file_mock,
        is_dir_mock,
        sample_data_service_mock,
        zip_files_mock,
        project_mock,
        username_mock,
    ):
        # Given
        mock_host = "mock_host.sanger.ac.uk"
        request_args_mock.return_value = {"redirect": "false"}
        request_headers_mock.return_value = {"X-Forwarded-Host": mock_host, "X-Forwarded-Port": "443"}
        username_mock.return_value = self.TEST_USER
        project_mock.return_value = self.MOCK_PROJECT_ID
        is_dir_mock.return_value = True
        # assigning list to side_effect returns next value each time mocked function is called
        # => mocks non-existence of the ZIP archivet, followed by existence of JSON file with params
        is_file_mock.side_effect = [False, True]
        lane_files = {"pubname": ["/lane file", "/another lane file"]}
        files_to_zip = {
            "pubname": [
                Path(self.MOCK_ENVIRONMENT["JUNO_DATA_INSTITUTION_VIEW"], "lane file"),
                Path(self.MOCK_ENVIRONMENT["JUNO_DATA_INSTITUTION_VIEW"], "another lane file"),
            ]
        }
        read_text_file_mock.return_value = json.dumps(lane_files)
        mock_token = "123"
        zip_file_basename = mock_token
        zip_file_location = "some/dir"
        sample_data_service_mock.return_value.get_bulk_download_location.return_value = zip_file_location
        download_host = mock_host
        download_symlink = "downloads/"
        sample_data_service_mock.return_value.make_download_symlink.return_value = download_symlink
        # When
        result = routes.data_download_route(mock_token)
        # Then
        sample_data_service_mock.assert_called_once_with(self.TEST_USER)
        zip_files_mock.assert_called_once_with(files_to_zip, basename=zip_file_basename, location=zip_file_location)
        sample_data_service_mock.return_value.make_download_symlink.assert_called_once_with(cross_institution=True)
        resp_mock.assert_called_once_with(
            {"download location": "https://{}/{}{}.zip".format(download_host, download_symlink, mock_token)}
        )
        self.assertIsNotNone(result)
        self.assertEqual(result[1], HTTPStatus.OK)

    @patch.dict(environ, MOCK_ENVIRONMENT, clear=True)
    @patch("dash.api.routes.get_authenticated_username")
    @patch("dash.api.routes.get_authenticated_project")
    @patch("dash.api.routes.zip_files")
    @patch.object(ServiceFactory, "sample_data_service")
    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.is_file")
    @patch("dash.api.routes.read_text_file")
    @patch("dash.api.routes.call_request_headers")
    @patch("dash.api.routes.call_request_args")
    def test_data_download_route_no_proxy(
        self,
        request_args_mock,
        request_headers_mock,
        read_text_file_mock,
        is_file_mock,
        is_dir_mock,
        sample_data_service_mock,
        zip_files_mock,
        project_mock,
        username_mock,
    ):
        # Given
        request_args_mock.return_value = {}
        request_headers_mock.return_value = {}

        username_mock.return_value = self.TEST_USER
        project_mock.return_value = self.MOCK_PROJECT_ID
        is_dir_mock.return_value = True
        # assigning list to side_effect returns next value each time mocked function is called
        # => mocks non-existence of the ZIP archivet, followed by existence of JSON file with params
        is_file_mock.side_effect = [False, True]
        lane_files = {"pubname": ["/lane file", "/another lane file"]}
        files_to_zip = {
            "pubname": [
                Path(self.MOCK_ENVIRONMENT["JUNO_DATA_INSTITUTION_VIEW"], "lane file"),
                Path(self.MOCK_ENVIRONMENT["JUNO_DATA_INSTITUTION_VIEW"], "another lane file"),
            ]
        }
        read_text_file_mock.return_value = json.dumps(lane_files)
        mock_token = "123"
        zip_file_basename = mock_token
        zip_file_location = "some/dir"
        sample_data_service_mock.return_value.get_bulk_download_location.return_value = zip_file_location
        download_host = ""
        download_symlink = "downloads/"
        sample_data_service_mock.return_value.make_download_symlink.return_value = download_symlink
        # When
        result = routes.data_download_route(mock_token)
        # Then
        sample_data_service_mock.assert_called_once_with(self.TEST_USER)
        zip_files_mock.assert_called_once_with(files_to_zip, basename=zip_file_basename, location=zip_file_location)
        sample_data_service_mock.return_value.make_download_symlink.assert_called_once_with(cross_institution=True)
        self.assertIsInstance(result, Response)
        self.assertIn(str(HTTPStatus.SEE_OTHER.value), result.status)
        self.assertEqual("{}/{}{}.zip".format(download_host, download_symlink, mock_token), result.headers["Location"])

    @patch.dict(environ, MOCK_ENVIRONMENT, clear=True)
    @patch("dash.api.routes.get_authenticated_username")
    @patch("dash.api.routes.zip_files")
    @patch("dash.api.routes.wait_for_zipfile_ready")
    @patch.object(ServiceFactory, "sample_data_service")
    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.is_file")
    @patch("dash.api.routes.read_text_file")
    @patch("dash.api.routes.call_request_headers")
    @patch("dash.api.routes.call_request_args")
    def test_data_download_route_reuse_existing_zip_file(
        self,
        request_args_mock,
        request_headers_mock,
        read_text_file_mock,
        is_file_mock,
        is_dir_mock,
        sample_data_service_mock,
        wait_for_zipfile_ready_mock,
        zip_files_mock,
        username_mock,
    ):
        # Given
        mock_host = "mock_host.sanger.ac.uk"
        request_args_mock.return_value = {}
        request_headers_mock.return_value = {"X-Forwarded-Host": mock_host, "X-Forwarded-Port": "443"}

        username_mock.return_value = self.TEST_USER
        is_dir_mock.return_value = True
        # mock existence of ZIP archive (JSON file not checked)
        is_file_mock.return_value = True
        wait_for_zipfile_ready_mock.return_value = True
        lane_files = {"pubname": ["/lane file", "/another lane file"]}
        read_text_file_mock.return_value = json.dumps(lane_files)
        mock_token = "123"
        zip_file_location = "some/dir"
        sample_data_service_mock.return_value.get_bulk_download_location.return_value = zip_file_location
        download_host = mock_host
        download_symlink = "downloads/"
        sample_data_service_mock.return_value.make_download_symlink.return_value = download_symlink
        # When
        result = routes.data_download_route(mock_token)
        # Then
        sample_data_service_mock.assert_called_once_with(self.TEST_USER)
        zip_files_mock.assert_not_called()
        sample_data_service_mock.return_value.make_download_symlink.assert_called_once_with(cross_institution=True)
        self.assertIsInstance(result, Response)
        self.assertIn(str(HTTPStatus.SEE_OTHER.value), result.status)
        self.assertEqual(
            "https://{}/{}{}.zip".format(download_host, download_symlink, mock_token), result.headers["Location"]
        )

    @patch.dict(environ, MOCK_ENVIRONMENT, clear=True)
    @patch("dash.api.routes.get_authenticated_username")
    @patch("dash.api.routes.wait_for_zipfile_ready")
    @patch.object(ServiceFactory, "sample_data_service")
    @patch("pathlib.Path.is_file")
    @patch("dash.api.routes.call_request_args")
    def test_data_download_route_reuse_existing_zip_file_timeout(
        self, request_args_mock, is_file_mock, sample_data_service_mock, wait_for_zipfile_ready_mock, username_mock
    ):
        # Given
        request_args_mock.return_value = {}
        username_mock.return_value = self.TEST_USER
        # mock existence of ZIP archive (JSON file not checked)
        is_file_mock.return_value = True
        wait_for_zipfile_ready_mock.return_value = False
        mock_token = "123"
        zip_file_location = "some/dir"
        sample_data_service_mock.return_value.get_bulk_download_location.return_value = zip_file_location
        with self.assertRaises(RuntimeError):
            routes.data_download_route(mock_token)

    @patch.dict(environ, MOCK_ENVIRONMENT, clear=True)
    @patch("dash.api.routes.get_authenticated_username")
    @patch.object(ServiceFactory, "sample_data_service")
    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.is_file")
    @patch("dash.api.routes.call_request_headers")
    @patch("dash.api.routes.call_request_args")
    def test_data_download_route_return_404(
        self,
        request_args_mock,
        request_headers_mock,
        is_file_mock,
        is_dir_mock,
        sample_data_service_mock,
        username_mock,
    ):
        # Given
        request_args_mock.return_value = {}
        request_headers_mock.return_value = {"X-Forwarded-Host": "mock_host.sanger.ac.uk", "X-Forwarded-Port": "443"}
        username_mock.return_value = self.TEST_USER
        is_dir_mock.return_value = True
        # mock non-existence of the ZIP archive and the JSON file with params
        is_file_mock.return_value = False
        mock_token = "123"
        zip_file_location = "some/dir"
        sample_data_service_mock.return_value.get_bulk_download_location.return_value = zip_file_location
        # When
        result = routes.data_download_route(mock_token)
        # Then
        sample_data_service_mock.assert_called_once_with(self.TEST_USER)
        self.assertIsInstance(result, Response)
        self.assertIn(str(HTTPStatus.NOT_FOUND.value), result.status)

    @patch("dash.api.routes.get_authenticated_username")
    @patch.object(ServiceFactory, "sample_data_service")
    def test_get_metadata_route_return_csv(self, sample_data_service_mock, username_mock):
        # Given
        batches = self.SERVICE_CALL_RETURN_DATA
        sample_filters = {"batches": batches}
        username_mock.return_value = self.TEST_USER
        sample_data_service_mock.return_value.get_csv_download.return_value = self.SERVICE_CALL_RETURN_CSV_DATA
        # When
        result = routes.get_metadata_route(
            {"sample filters": sample_filters, "csv filename": self.SERVICE_CALL_RETURN_CSV_FILENAME}
        )
        # Then
        sample_data_service_mock.assert_called_with(self.TEST_USER)
        sample_data_service_mock.return_value.get_csv_download.assert_called_once_with(
            self.SERVICE_CALL_RETURN_CSV_FILENAME, sample_filters
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, type(Response("any content will do")))
        self.assertEqual(result.status_code, HTTPStatus.OK)
        self.assertEqual(result.content_type, self.EXPECTED_CSV_CONTENT_TYPE)
        self.assertEqual(result.headers["Content-Disposition"], self.EXPECTED_CONTENT_DISPOSITION)

    @patch("dash.api.routes.get_authenticated_username")
    @patch.object(ServiceFactory, "sample_data_service")
    def test_get_metadata_route_return_csv_404(self, sample_data_service_mock, username_mock):
        # Given
        batches = self.SERVICE_CALL_RETURN_DATA
        sample_filters = {"batches": batches}
        username_mock.return_value = self.TEST_USER
        sample_data_service_mock.return_value.get_csv_download.return_value = self.SERVICE_CALL_RETURN_CSV_NOT_FOUND
        # When
        result = routes.get_metadata_route(
            {"sample filters": sample_filters, "csv filename": self.SERVICE_CALL_RETURN_CSV_FILENAME}
        )
        # Then
        sample_data_service_mock.assert_called_with(self.TEST_USER)
        sample_data_service_mock.return_value.get_csv_download.assert_called_once_with(
            self.SERVICE_CALL_RETURN_CSV_FILENAME, sample_filters
        )
        self.assertIsInstance(result, Response)
        self.assertIn(str(HTTPStatus.NOT_FOUND.value), result.status)

    @patch("dash.api.routes.get_authenticated_username")
    @patch("dash.api.routes.get_host_name")
    @patch.object(ServiceFactory, "sample_data_service")
    def test_get_metadata_for_download_route(self, sample_data_service_mock, host_name_mock, username_mock):
        # Given
        sample_data_service_mock.return_value.get_metadata_for_download.return_value = self.SERVICE_CALL_RETURN_CSV_DATA
        username_mock.return_value = self.TEST_USER
        host_name_mock.return_value = self.TEST_HOST_NAME
        # When
        result = routes.get_metadata_for_download_route("fake institution key", "pipeline", "successful")
        # Then
        sample_data_service_mock.assert_called_once_with(self.TEST_USER)
        sample_data_service_mock.return_value.get_metadata_for_download.assert_called_once()
        self.assertIsInstance(result, type(Response("any content will do")))
        self.assertEqual(result.status_code, HTTPStatus.OK)
        self.assertEqual(result.content_type, self.EXPECTED_CSV_CONTENT_TYPE)
        self.assertEqual(result.headers["Content-Disposition"], self.EXPECTED_CONTENT_DISPOSITION)

    def test_get_host_name(self):
        request_mock = Mock()
        request_mock.host = self.TEST_HOST_NAME
        hostname = routes.get_host_name(request_mock)
        self.assertEqual(hostname, self.TEST_HOST_NAME)

    @patch.dict(environ, MOCK_ENVIRONMENT, clear=True)
    @patch("dash.api.routes.call_request_cookies")
    def test_get_authenticated_username_nontest_mode(self, mock_cookies):
        # Given
        mock_cookies.return_value = {environ["AUTH_COOKIE_NAME"]: self.TEST_AUTH_TOKEN}
        ServiceFactory.TEST_MODE = False

        # When
        username = routes.get_authenticated_username()
        # Then
        self.assertEqual(username, self.TEST_USER)

    @patch("dash.api.routes.call_request_cookies")
    def test_get_authenticated_username_nontest_mode_with_no_cookie(self, mock_cookies):
        # Given
        mock_cookies.return_value = {}
        ServiceFactory.TEST_MODE = False
        # When/Then
        with self.assertRaises(exceptions.NotAuthorisedException):
            routes.get_authenticated_username()

    @patch.dict(environ, MOCK_ENVIRONMENT, clear=True)
    @patch("dash.api.routes.call_request_cookies")
    def test_get_authenticated_username_nontest_mode_with_empty_cookie(self, mock_cookies):
        # Given
        mock_cookies.return_value = {environ["AUTH_COOKIE_NAME"]: ""}
        ServiceFactory.TEST_MODE = False
        # When/Then
        with self.assertRaises(exceptions.NotAuthorisedException):
            routes.get_authenticated_username()

    @patch.dict(environ, MOCK_ENVIRONMENT, clear=True)
    @patch("dash.api.routes.call_request_cookies")
    def test_get_authenticated_username_test_mode(self, mock_cookies):
        # Given
        mock_cookies.return_value = {environ["AUTH_COOKIE_NAME"]: ""}
        ServiceFactory.TEST_MODE = True
        # When
        username = routes.get_authenticated_username()
        # Then
        self.assertIsNone(username)
