import logging
from unittest import TestCase
from unittest.mock import patch
from urllib.error import URLError

from DataSources.sample_metadata import Monocle_Client, ProtocolError, SampleMetadata

logging.basicConfig(format="%(asctime)-15s %(levelname)s:  %(message)s", level="CRITICAL")


class SampleMetadataTest(TestCase):

    test_config = "dash/tests/mock_data/data_sources.yml"  # ADD TEST PATH BEFORE DEPLOYMENT
    bad_config = "dash/tests/mock_data/data_sources_bad.yml"
    bad_db_cnf = "dash/tests/mock_data/bad.cnf"
    bad_api_host = "http://no.such.host/"
    bad_api_endpoint = "/no/such/endpoint"
    genuine_api_host = "http://metadata_api.dev.pam.sanger.ac.uk/"

    mock_project = "juno"
    mock_bad_get_sample = """{  "wrong key":
                                       {  "does": "not matter what appears here"
                                       }
                                    }"""

    mock_get_samples = """{   "samples":  [  {  "lane_id": "fake_lane_1#123", "sanger_sample_id":"fake_sample_id_1", "public_name":"fake_name",
                                                "disease_name":"fake disease", "serotype": "fake_serotype", "host_status": "unknown",
                                                "submitting_institution": "Ministry of Health, Central laboratories", "id": "an_id"},
                                             {  "lane_id": "fake_lane_1#124", "sanger_sample_id":"fake_sample_id_2", "public_name":"fake_name",
                                                "disease_name":"fake disease", "serotype": "fake_serotype", "host_status": "unknown",
                                                "submitting_institution": "National Reference Laboratories", "id": "an_id"},
                                             {  "lane_id": "fake_lane_1#125", "sanger_sample_id":"fake_sample_id_3", "public_name":"fake_name",
                                                "disease_name":"fake disease", "serotype": "fake_serotype", "host_status": "unknown",
                                                "submitting_institution": "The Chinese University of Hong Kong", "id": "an_id"}
                                             ]
                              }"""

    mock_get_samples_matching_metadata_filters = """[  "fake_sample_id_1", "fake_sample_id_2", "fake_sample_id_3" ]"""

    mock_distinct_values = [{"name": "field1", "values": ["a", "b"]}, {"name": "field2", "values": ["d", "e"]}]

    mock_distinct_in_silico_values = [{"name": "field3", "values": ["f", "g", "h"]}]

    mock_distinct_qc_data_values = [{"name": "field4", "values": ["i"]}]

    mock_institution_names = """{ "institutions":   [  "Ministry of Health, Central laboratories",
                                                      "National Reference Laboratories",
                                                      "The Chinese University of Hong Kong"
                                                      ]
                                 }"""

    mock_metadata_field = "any_filter_field"
    mock_in_silico_field = "any_in_silico_field"
    mock_metadata_values = ["any", "metadata", "values"]
    mock_in_silico_values = ["any", "in", "silico", "values"]

    expected_sanger_sample_ids = ["5903STDY8059053", "5903STDY8059055"]
    expected_institution_names = [
        "Ministry of Health, Central laboratories",
        "National Reference Laboratories",
        "The Chinese University of Hong Kong",
    ]
    required_sample_dict_keys = ["sanger_sample_id", "public_name", "submitting_institution"]

    expected_distinct_values = [
        {"field type": "metadata", "fields": mock_distinct_values},
        {"field type": "in silico", "fields": mock_distinct_in_silico_values},
        {"field type": "qc data", "fields": mock_distinct_qc_data_values},
    ]

    def setUp(self):
        self.sample_metadata = SampleMetadata(set_up=False)
        self.sample_metadata.monocle_client = Monocle_Client(set_up=False)
        self.sample_metadata.monocle_client.set_up(self.test_config)

    def test_init(self):
        self.assertIsInstance(self.sample_metadata, SampleMetadata)

    def test_reject_bad_config(self):
        with self.assertRaises(KeyError):
            doomed = Monocle_Client(set_up=False)
            doomed.set_up(self.bad_config)

    def test_missing_config(self):
        with self.assertRaises(FileNotFoundError):
            doomed = Monocle_Client(set_up=False)
            doomed.set_up("no_such_config.yml")

    def test_reject_bad_url(self):
        with self.assertRaises(URLError):
            doomed = Monocle_Client(set_up=False)
            doomed.set_up(self.test_config)
            doomed.config[self.mock_project]["base_url"] = self.bad_api_host
            endpoint = doomed.config[self.mock_project]["samples"] + self.expected_sanger_sample_ids[0]
            doomed.make_request("http://fake-container" + endpoint)

    def test_reject_bad_endpoint(self):
        with self.assertRaises(URLError):
            doomed = Monocle_Client(set_up=False)
            doomed.set_up(self.test_config)
            doomed.config[self.mock_project]["base_url"] = self.genuine_api_host
            endpoint = self.bad_api_endpoint + self.expected_sanger_sample_ids[0]
            doomed.make_request("http://fake-container" + endpoint)

    @patch("DataSources.sample_metadata.Monocle_Client.make_request")
    def test_get_institution_names(self, mock_query):
        mock_query.return_value = self.mock_institution_names
        names = self.sample_metadata.get_institution_names(self.mock_project)
        self.assertIsInstance(names, list)
        self.assertEqual(self.expected_institution_names, names)

    @patch("DataSources.sample_metadata.Monocle_Client.make_request")
    def test_get_samples(self, mock_query):
        mock_query.return_value = self.mock_get_samples
        samples = self.sample_metadata.get_samples(self.mock_project, self.mock_project)
        self.assertIsInstance(samples, list)
        for this_sample in samples:
            for required in self.required_sample_dict_keys:
                self.assertTrue(
                    required in this_sample, msg="required key '{}' not found in sample dict".format(required)
                )
                self.assertIsInstance(
                    this_sample[required], str, msg="sample item {} should be a string".format(required)
                )

    @patch("DataSources.sample_metadata.Monocle_Client.filters")
    def test_get_samples_matching_metadata_filters(self, mock_filters):
        mock_filters.return_value = []
        self.sample_metadata.get_samples_matching_metadata_filters(
            self.mock_project, {self.mock_metadata_field: self.mock_metadata_values}
        )
        mock_filters.assert_called_once_with(
            self.mock_project, [{"name": self.mock_metadata_field, "values": self.mock_metadata_values}]
        )

    @patch("DataSources.sample_metadata.Monocle_Client.filters_in_silico")
    def test_get_lanes_matching_in_silico_filters(self, mock_filters_in_silico):
        mock_filters_in_silico.return_value = []
        self.sample_metadata.get_lanes_matching_in_silico_filters(
            self.mock_project, {self.mock_in_silico_field: self.mock_in_silico_values}
        )
        mock_filters_in_silico.assert_called_once_with(
            self.mock_project, [{"name": self.mock_in_silico_field, "values": self.mock_in_silico_values}]
        )

    @patch("DataSources.sample_metadata.Monocle_Client.make_request")
    def test_filters(self, mock_query):
        mock_query.return_value = "[]"
        mock_payload = [{"name": self.mock_metadata_field, "values": self.mock_metadata_values}]
        self.sample_metadata.monocle_client.filters(self.mock_project, mock_payload)
        mock_query.assert_called_once_with(
            "http://fake-container/metadata/juno/sample_ids_matching_metadata", post_data=mock_payload
        )

    @patch("DataSources.sample_metadata.Monocle_Client.make_request")
    def test_filters_in_silico(self, mock_query):
        mock_query.return_value = "[]"
        mock_payload = [{"name": self.mock_in_silico_field, "values": self.mock_in_silico_values}]
        self.sample_metadata.monocle_client.filters_in_silico(self.mock_project, mock_payload)
        mock_query.assert_called_once_with(
            "http://fake-container/metadata/juno/lane_ids_matching_in_silico_data", post_data=mock_payload
        )

    @patch("DataSources.sample_metadata.Monocle_Client.distinct_values")
    @patch("DataSources.sample_metadata.Monocle_Client.distinct_in_silico_values")
    @patch("DataSources.sample_metadata.Monocle_Client.distinct_qc_data_values")
    def test_get_distinct_values(
        self, mock_distinct_qc_data_values, mock_distinct_in_silico_values, mock_distinct_values
    ):
        mock_distinct_values.return_value = self.mock_distinct_values
        mock_distinct_in_silico_values.return_value = self.mock_distinct_in_silico_values
        mock_distinct_qc_data_values.return_value = self.mock_distinct_qc_data_values
        distinct_values = self.sample_metadata.get_distinct_values(
            self.mock_project,
            {"metadata": ["field1", "field2"], "in silico": ["field3"], "qc data": ["field4"]},
            ["institution A"],
        )
        self.assertIsInstance(distinct_values, list)
        # logging.critical("\nEXPECTED:\n{}\nGOT:\n{}".format(self.expected_distinct_values, distinct_values))
        self.assertEqual(self.expected_distinct_values, distinct_values)

    @patch("DataSources.sample_metadata.Monocle_Client.make_request")
    def test_distinct_values(self, mock_query):
        mock_query.return_value = '{"distinct values": []}'
        mock_fields = ["field1", "field2"]
        mock_institutions = ["institution A"]
        self.sample_metadata.monocle_client.distinct_values(self.mock_project, mock_fields, mock_institutions)
        mock_query.assert_called_once_with(
            "http://fake-container/metadata/juno/distinct_values",
            post_data={"fields": mock_fields, "institutions": mock_institutions},
        )

    @patch("DataSources.sample_metadata.Monocle_Client.make_request")
    def test_distinct_in_silico_values(self, mock_query):
        mock_query.return_value = '{"distinct values": []}'
        mock_fields = ["field3"]
        mock_institutions = ["institution A"]
        self.sample_metadata.monocle_client.distinct_in_silico_values(self.mock_project, mock_fields, mock_institutions)
        mock_query.assert_called_once_with(
            "http://fake-container/metadata/juno/distinct_in_silico_values",
            post_data={"fields": mock_fields, "institutions": mock_institutions},
        )

    @patch("DataSources.sample_metadata.Monocle_Client.make_request")
    def test_distinct_qc_data_values(self, mock_query):
        mock_query.return_value = '{"distinct values": []}'
        mock_fields = ["field4"]
        mock_institutions = ["institution A"]
        self.sample_metadata.monocle_client.distinct_qc_data_values(self.mock_project, mock_fields, mock_institutions)
        mock_query.assert_called_once_with(
            "http://fake-container/metadata/juno/distinct_qc_data_values",
            post_data={"fields": mock_fields, "institutions": mock_institutions},
        )

    @patch.object(Monocle_Client, "make_request")
    def test_reject_bad_get_sample_response(self, mock_request):
        with self.assertRaises(ProtocolError):
            mock_request.return_value = self.mock_bad_get_sample
            self.sample_metadata.get_samples(self.mock_project, self.expected_sanger_sample_ids[0])
