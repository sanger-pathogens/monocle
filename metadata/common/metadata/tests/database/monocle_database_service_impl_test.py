import unittest
from unittest.mock import Mock, call, patch

from metadata.api.database.monocle_database_service_impl import MonocleDatabaseServiceImpl
from metadata.tests.test_data import (
    TEST_LANE_IN_SILICO_1,
    TEST_LANE_IN_SILICO_1_DICT,
    TEST_LANE_IN_SILICO_2,
    TEST_LANE_IN_SILICO_2_DICT,
    TEST_LANE_QC_DATA_1,
    TEST_LANE_QC_DATA_1_DICT,
    TEST_LANE_QC_DATA_2,
    TEST_LANE_QC_DATA_2_DICT,
    TEST_SAMPLE_1,
    TEST_SAMPLE_1_DICT,
    TEST_SAMPLE_2,
    TEST_SAMPLE_2_DICT,
)
from sqlalchemy.exc import OperationalError


class TestMonocleDatabaseServiceImpl(unittest.TestCase):
    """Unit test class for MonocleDatabaseServiceImpl"""

    def setUp(self) -> None:
        with patch("metadata.api.database.monocle_database_service_impl.Connector", autospec=True) as connector_mock:
            import json

            from metadata.wsgi import application

            self.assertIsNotNone(application)
            with open("config.json") as config_file:
                connector_mock.application = application
                connector_mock.application.config = json.load(config_file)

            self.connector = connector_mock
            self.connection = Mock()
            self.transactional_connection = Mock()
            self.connection.__enter__ = lambda x: self.connection
            self.connection.__exit__ = Mock()
            self.transactional_connection.__enter__ = lambda x: self.transactional_connection
            self.transactional_connection.__exit__ = Mock()
            self.connector.get_transactional_connection.return_value = self.transactional_connection
            self.connector.get_connection.return_value = self.connection
            self.under_test = MonocleDatabaseServiceImpl(self.connector)

        self.response_as_string = '{"user_details": {"username": "mock_user", \
        "memberOf": [{"inst_id": "mock_id", "inst_name": "mock_name", "country_names": ["name1", "name2"]}, \
        {"inst_id": "LabCenEstPar", "inst_name": "Laboratório Central do Estado do Paraná", "country_names": ["Brazil"]}]}}'

        self.response_as_dict = {
            "user_details": {
                "username": "mock_user",
                "memberOf": [
                    {"inst_id": "mock_id", "inst_name": "mock_name", "country_names": ["name1", "name2"]},
                    {
                        "inst_id": "LabCenEstPar",
                        "inst_name": "Laboratório Central do Estado do Paraná",
                        "country_names": ["Brazil"],
                    },
                ],
            }
        }

    # basically the same as test_get_download_metadata except query is SELECT_ALL_SAMPLES_SQL
    def test_get_samples(self) -> None:
        # Fake a returned result set...
        self.connection.execute.return_value = [
            TEST_SAMPLE_1_DICT,
            TEST_SAMPLE_2_DICT,
        ]

        samples = self.under_test.get_samples()

        self.assertIsNotNone(samples)
        self.assertEqual(len(samples), 2)
        self.assertEqual(samples[0], TEST_SAMPLE_1)
        self.assertEqual(samples[1], TEST_SAMPLE_2)
        self.connection.execute.assert_called_with(self.under_test.SELECT_ALL_SAMPLES_SQL)

    def test_get_samples_noresults(self) -> None:
        self.connection.execute.return_value = []
        samples = self.under_test.get_samples()
        self.connection.execute.assert_called_with(self.under_test.SELECT_ALL_SAMPLES_SQL)
        self.assertIsNotNone(samples)
        self.assertEqual(len(samples), 0)

    def test_get_samples_filtered_by_metadata(self) -> None:
        self.connection.execute.return_value = [dict(sanger_sample_id="9999STDY8113123")]
        samples_ids = self.under_test.get_samples_filtered_by_metadata({"serotype": ["IV"]})
        execute_args = list(self.connection.execute.call_args)
        execute_sql = str(execute_args[0][0])
        execute_values = execute_args[1]
        self.assertEqual(2, len(execute_args), "expected 2 arguments to be passed to self.connection.execute")
        self.assertEqual(
            1,
            len(execute_args[0]),
            "expected 1 SQL query to be passed as first positional argument to self.connection.execute",
        )
        self.assertEqual(
            execute_sql,
            MonocleDatabaseServiceImpl.FILTER_SAMPLES_IN_SQL.format("serotype"),
            "not the expected SQL query",
        )
        self.assertEqual(
            execute_values,
            {"values": ("IV",)},
            "not what was expected for :values in {}".format(MonocleDatabaseServiceImpl.FILTER_SAMPLES_IN_SQL),
        )
        self.assertEqual(samples_ids, ["9999STDY8113123"])

    def test_get_samples_filtered_by_metadata_incl_null(self) -> None:
        self.connection.execute.return_value = [dict(sanger_sample_id="9999STDY8113123")]
        # passing `None` is values list should result in SQL query that includes records with NULL serotype
        samples_ids = self.under_test.get_samples_filtered_by_metadata({"serotype": ["IV", None]})
        execute_args = list(self.connection.execute.call_args)
        execute_sql = str(execute_args[0][0])
        execute_values = execute_args[1]
        self.assertEqual(2, len(execute_args), "expected 2 arguments to be passed to self.connection.execute")
        self.assertEqual(
            1,
            len(execute_args[0]),
            "expected 1 SQL query to be passed as first positional argument to self.connection.execute",
        )
        self.assertEqual(
            execute_sql,
            MonocleDatabaseServiceImpl.FILTER_SAMPLES_IN_SQL_INCL_NULL.format("serotype", "serotype"),
            "not the expected SQL query",
        )
        self.assertEqual(
            execute_values,
            {"values": ("IV", None)},
            "not what was expected for :values in {}".format(
                MonocleDatabaseServiceImpl.FILTER_SAMPLES_IN_SQL_INCL_NULL
            ),
        )
        self.assertEqual(samples_ids, ["9999STDY8113123"])

    def test_get_samples_filtered_by_metadata_noresults(self) -> None:
        self.connection.execute.return_value = []
        samples_ids = self.under_test.get_samples_filtered_by_metadata({"serotype": ["None"]})
        self.assertEqual(samples_ids, [])

    def test_get_samples_filtered_by_metadata_reject_request_if_bad_field_name(self) -> None:
        self.connection.execute.side_effect = OperationalError(
            "mock params", "mock orig", "mock message including the substring Unknown column"
        )
        expected = None
        samples_ids = self.under_test.get_samples_filtered_by_metadata({"bad_field_name": ["anything"]})
        self.assertEqual(self.connection.execute.call_count, 1)
        self.assertEqual(samples_ids, expected)

    def test_get_lanes_filtered_by_in_silico_data(self) -> None:
        self.connection.execute.return_value = [{"lane_id": "2000_2#10"}]
        # passing `None` is values list should result in SQL query that includes records with NULL ST
        lanes_ids = self.under_test.get_lanes_filtered_by_in_silico_data({"ST": [None, "14"]})
        execute_args = list(self.connection.execute.call_args)
        execute_sql = str(execute_args[0][0])
        execute_values = execute_args[1]
        self.assertEqual(2, len(execute_args), "expected 2 arguments to be passed to self.connection.execute")
        self.assertEqual(
            1,
            len(execute_args[0]),
            "expected 1 SQL query to be passed as first positional argument to self.connection.execute",
        )
        self.assertEqual(
            execute_sql,
            MonocleDatabaseServiceImpl.IN_SILICO_FILTER_LANES_IN_SQL_INCL_NULL.format("ST", "ST"),
            "not the expected SQL query",
        )
        self.assertEqual(
            execute_values,
            {"values": (None, "14")},
            "not what was expected for :values in {}".format(
                MonocleDatabaseServiceImpl.IN_SILICO_FILTER_LANES_IN_SQL_INCL_NULL
            ),
        )
        self.assertEqual(lanes_ids, ["2000_2#10"])

    def test_get_lanes_filtered_by_in_silico_data_incl_null(self) -> None:
        self.connection.execute.return_value = [{"lane_id": "2000_2#10"}]
        lanes_ids = self.under_test.get_lanes_filtered_by_in_silico_data({"ST": ["14"]})
        execute_args = list(self.connection.execute.call_args)
        execute_sql = str(execute_args[0][0])
        execute_values = execute_args[1]
        self.assertEqual(2, len(execute_args), "expected 2 arguments to be passed to self.connection.execute")
        self.assertEqual(
            1,
            len(execute_args[0]),
            "expected 1 SQL query to be passed as first positional argument to self.connection.execute",
        )
        self.assertEqual(
            execute_sql,
            MonocleDatabaseServiceImpl.IN_SILICO_FILTER_LANES_IN_SQL.format("ST"),
            "not the expected SQL query",
        )
        self.assertEqual(
            execute_values,
            {"values": ("14",)},
            "not what was expected for :values in {}".format(MonocleDatabaseServiceImpl.IN_SILICO_FILTER_LANES_IN_SQL),
        )
        self.assertEqual(lanes_ids, ["2000_2#10"])

    def test_get_lanes_filtered_by_in_silico_data_noresults(self) -> None:
        self.connection.execute.return_value = []
        samples_ids = self.under_test.get_samples_filtered_by_metadata({"ST": ["None"]})
        self.assertEqual(samples_ids, [])

    def test_get_lanes_filtered_by_in_silico_data_reject_request_if_bad_field_name(self) -> None:
        self.connection.execute.side_effect = OperationalError(
            "mock params", "mock orig", "mock message including the substring Unknown column"
        )
        expected = None
        samples_ids = self.under_test.get_samples_filtered_by_metadata({"bad_field_name": ["anything"]})
        self.assertEqual(self.connection.execute.call_count, 1)
        self.assertEqual(samples_ids, expected)

    def test_get_lanes_filtered_by_qc_data(self) -> None:
        self.connection.execute.return_value = [{"lane_id": "2000_2#10"}]
        # passing `None` in values list should result in SQL query that includes records with NULL status
        lanes_ids = self.under_test.get_lanes_filtered_by_qc_data({"status": [None, "PASS"]})
        execute_args = list(self.connection.execute.call_args)
        execute_sql = str(execute_args[0][0])
        execute_values = execute_args[1]
        self.assertEqual(2, len(execute_args), "expected 2 arguments to be passed to self.connection.execute")
        self.assertEqual(
            1,
            len(execute_args[0]),
            "expected 1 SQL query to be passed as first positional argument to self.connection.execute",
        )
        self.assertEqual(
            execute_sql,
            MonocleDatabaseServiceImpl.QC_DATA_FILTER_LANES_IN_SQL_INCL_NULL.format("status", "status"),
            "not the expected SQL query",
        )
        self.assertEqual(
            execute_values,
            {"values": (None, "PASS")},
            "not what was expected for :values in {}".format(
                MonocleDatabaseServiceImpl.QC_DATA_FILTER_LANES_IN_SQL_INCL_NULL
            ),
        )
        self.assertEqual(lanes_ids, ["2000_2#10"])

    def test_get_lanes_filtered_by_qc_data_incl_null(self) -> None:
        self.connection.execute.return_value = [{"lane_id": "2000_2#10"}]
        lanes_ids = self.under_test.get_lanes_filtered_by_qc_data({"status": ["PASS"]})
        execute_args = list(self.connection.execute.call_args)
        execute_sql = str(execute_args[0][0])
        execute_values = execute_args[1]
        self.assertEqual(2, len(execute_args), "expected 2 arguments to be passed to self.connection.execute")
        self.assertEqual(
            1,
            len(execute_args[0]),
            "expected 1 SQL query to be passed as first positional argument to self.connection.execute",
        )
        self.assertEqual(
            execute_sql,
            MonocleDatabaseServiceImpl.QC_DATA_FILTER_LANES_IN_SQL.format("status"),
            "not the expected SQL query",
        )
        self.assertEqual(
            execute_values,
            {"values": ("PASS",)},
            "not what was expected for :values in {}".format(MonocleDatabaseServiceImpl.QC_DATA_FILTER_LANES_IN_SQL),
        )
        self.assertEqual(lanes_ids, ["2000_2#10"])

    def test_get_lanes_filtered_by_qc_data_noresults(self) -> None:
        self.connection.execute.return_value = []
        samples_ids = self.under_test.get_samples_filtered_by_metadata({"status": ["None"]})
        self.assertEqual(samples_ids, [])

    def test_get_lanes_filtered_by_qc_data_reject_request_if_bad_field_name(self) -> None:
        self.connection.execute.side_effect = OperationalError(
            "mock params", "mock orig", "mock message including the substring Unknown column"
        )
        expected = None
        samples_ids = self.under_test.get_samples_filtered_by_metadata({"bad_field_name": ["anything"]})
        self.assertEqual(self.connection.execute.call_count, 1)
        self.assertEqual(samples_ids, expected)

    def test_get_samples_filtered_by_metadata_nofilters(self) -> None:
        self.connection.execute.return_value = [
            dict(sanger_sample_id="9999STDY8113123"),
            dict(sanger_sample_id="9999STDY8113124"),
        ]
        samples_ids = self.under_test.get_samples_filtered_by_metadata({})
        self.assertEqual(samples_ids, ["9999STDY8113123", "9999STDY8113124"])

    def test_update_sample_metadata(self) -> None:
        metadata_list = [TEST_SAMPLE_1, TEST_SAMPLE_2]
        self.under_test.update_sample_metadata(metadata_list)
        calls = [call(self.under_test.INSERT_OR_UPDATE_SAMPLE_SQL, **TEST_SAMPLE_1_DICT)]

        self.transactional_connection.execute.assert_has_calls(calls, any_order=True)

    def dict_change_empty_value_to_none(self, d):
        ret = {}
        for k, v in d.items():
            if v == "":
                ret[k] = None
            else:
                ret[k] = v
        return ret

    def test_update_lane_in_silico_data(self) -> None:
        in_silico_data_list = [TEST_LANE_IN_SILICO_1, TEST_LANE_IN_SILICO_2]
        self.under_test.update_lane_in_silico_data(in_silico_data_list)
        lis1 = self.dict_change_empty_value_to_none(TEST_LANE_IN_SILICO_1_DICT)
        lis2 = self.dict_change_empty_value_to_none(TEST_LANE_IN_SILICO_2_DICT)
        calls = [
            call(self.under_test.INSERT_OR_UPDATE_IN_SILICO_SQL, **lis1),
            call(self.under_test.INSERT_OR_UPDATE_IN_SILICO_SQL, **lis2),
        ]

        self.transactional_connection.execute.assert_has_calls(calls, any_order=True)

    def test_update_lane_qc_data(self) -> None:
        qc_data_list = [TEST_LANE_QC_DATA_1, TEST_LANE_QC_DATA_2]
        self.under_test.update_lane_qc_data(qc_data_list)
        calls = [
            call(
                self.under_test.INSERT_OR_UPDATE_QC_DATA_SQL,
                lane_id=TEST_LANE_QC_DATA_1.lane_id,
                status=TEST_LANE_QC_DATA_1.status,
                rel_abundance_status=TEST_LANE_QC_DATA_1.rel_abundance_status,
                contig_no_status=TEST_LANE_QC_DATA_1.contig_no_status,
                gc_content_status=TEST_LANE_QC_DATA_1.gc_content_status,
                genome_len_status=TEST_LANE_QC_DATA_1.gc_content_status,
                cov_depth_status=TEST_LANE_QC_DATA_1.cov_depth_status,
                cov_breadth_status=TEST_LANE_QC_DATA_1.cov_breadth_status,
                HET_SNPs_status=TEST_LANE_QC_DATA_1.HET_SNPs_status,
                QC_pipeline_version=TEST_LANE_QC_DATA_1.QC_pipeline_version,
            ),
            call(
                self.under_test.INSERT_OR_UPDATE_QC_DATA_SQL,
                lane_id=TEST_LANE_QC_DATA_2.lane_id,
                status=TEST_LANE_QC_DATA_2.status,
                rel_abundance_status=TEST_LANE_QC_DATA_2.rel_abundance_status,
                contig_no_status=TEST_LANE_QC_DATA_2.contig_no_status,
                gc_content_status=TEST_LANE_QC_DATA_2.gc_content_status,
                genome_len_status=TEST_LANE_QC_DATA_2.gc_content_status,
                cov_depth_status=TEST_LANE_QC_DATA_2.cov_depth_status,
                cov_breadth_status=TEST_LANE_QC_DATA_2.cov_breadth_status,
                HET_SNPs_status=TEST_LANE_QC_DATA_2.HET_SNPs_status,
                QC_pipeline_version=TEST_LANE_QC_DATA_2.QC_pipeline_version,
            ),
        ]
        self.transactional_connection.execute.assert_has_calls(calls, any_order=True)

    def test_update_sample_metadata_noinput(self) -> None:
        metadata_list = []
        self.under_test.update_sample_metadata(metadata_list)
        self.transactional_connection.get_connection.assert_not_called()
        metadata_list = None
        self.under_test.update_sample_metadata(metadata_list)
        self.transactional_connection.get_connection.assert_not_called()

    def test_update_lane_in_silico_data_noinput(self) -> None:
        in_silico_data_list = []
        self.under_test.update_sample_metadata(in_silico_data_list)
        self.transactional_connection.get_connection.assert_not_called()
        in_silico_data_list = None
        self.under_test.update_sample_metadata(in_silico_data_list)
        self.transactional_connection.get_connection.assert_not_called()

    def test_update_lane_qc_data_noinput(self) -> None:
        qc_data_list = []
        self.under_test.update_sample_metadata(qc_data_list)
        self.transactional_connection.get_connection.assert_not_called()
        qc_data_list = None
        self.under_test.update_sample_metadata(qc_data_list)
        self.transactional_connection.get_connection.assert_not_called()

    def test_get_download_metadata(self) -> None:

        input_list = ["9999STDY8113123", "9999STDY8113124"]
        # Fake a returned result set...
        self.connection.execute.return_value = [
            TEST_SAMPLE_1_DICT,
            TEST_SAMPLE_2_DICT,
        ]

        metadata = self.under_test.get_download_metadata(input_list)

        self.assertIsNotNone(metadata)
        self.assertEqual(len(metadata), 2)
        self.assertEqual(metadata[0], TEST_SAMPLE_1)
        self.assertEqual(metadata[1], TEST_SAMPLE_2)
        self.connection.execute.assert_called_with(
            self.under_test.SELECT_SAMPLES_SQL, samples=("9999STDY8113123", "9999STDY8113124")
        )

    def test_get_download_metadata_noresults(self) -> None:
        input_list = ["9999STDY8113123", "9999STDY8113124"]
        self.connection.execute.return_value = []

        metadata = self.under_test.get_download_metadata(input_list)
        self.assertIsNotNone(metadata)
        self.assertIsInstance(metadata, list)
        self.connection.execute.assert_called_with(
            self.under_test.SELECT_SAMPLES_SQL, samples=("9999STDY8113123", "9999STDY8113124")
        )
        self.assertEqual(len(metadata), 0)

    def test_convert_string(self) -> None:
        self.assertIsNone(self.under_test.convert_string(""))
        self.assertIsNone(self.under_test.convert_string(None))
        self.assertIsNotNone(self.under_test.convert_string("hello"))

    def test_convert_int(self) -> None:
        self.assertIsNone(self.under_test.convert_int(""))
        self.assertIsNone(self.under_test.convert_int(None))
        self.assertEqual(self.under_test.convert_int("12"), 12)
        self.assertEqual(self.under_test.convert_int("0"), 0)
        with self.assertRaises(ValueError):
            self.under_test.convert_int("hello")

    def test_get_download_in_silico_data(self) -> None:

        input_list = ["50000_2#282", "50000_2#287"]
        # Fake a returned result set...
        self.connection.execute.return_value = [
            TEST_LANE_IN_SILICO_1_DICT,
            TEST_LANE_IN_SILICO_2_DICT,
        ]

        in_silico_data = self.under_test.get_download_in_silico_data(input_list)
        self.assertIsNotNone(in_silico_data)
        self.assertEqual(len(in_silico_data), 2)
        self.assertEqual(in_silico_data[0], TEST_LANE_IN_SILICO_1)
        self.assertEqual(in_silico_data[1], TEST_LANE_IN_SILICO_2)
        self.connection.execute.assert_called_with(
            self.under_test.SELECT_LANES_IN_SILICO_SQL, lanes=("50000_2#282", "50000_2#287")
        )

    def test_get_download_qc_data(self) -> None:

        input_list = ["50000_2#282", "50000_2#287"]
        # Fake a returned result set...
        self.connection.execute.return_value = [
            TEST_LANE_QC_DATA_1_DICT,
            TEST_LANE_QC_DATA_2_DICT,
        ]

        qc_data = self.under_test.get_download_qc_data(input_list)
        self.assertIsNotNone(qc_data)
        self.assertEqual(len(qc_data), 2)
        self.assertEqual(qc_data[0], TEST_LANE_QC_DATA_1)
        self.assertEqual(qc_data[1], TEST_LANE_QC_DATA_2)
        self.connection.execute.assert_called_with(
            self.under_test.SELECT_LANES_QC_DATA_SQL, lanes=("50000_2#282", "50000_2#287")
        )
