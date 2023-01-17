import json
import logging
from unittest import TestCase
from unittest.mock import patch
from urllib.error import URLError

from DataSources.sample_metadata import MonocleClient, ProtocolError, SampleMetadata

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
                                                "submitting_institution": "MinHeaCen", "id": "an_id"},
                                             {  "lane_id": "fake_lane_1#124", "sanger_sample_id":"fake_sample_id_2", "public_name":"fake_name",
                                                "disease_name":"fake disease", "serotype": "fake_serotype", "host_status": "unknown",
                                                "submitting_institution": "NatRefLab", "id": "an_id"},
                                             {  "lane_id": "fake_lane_1#125", "sanger_sample_id":"fake_sample_id_3", "public_name":"fake_name",
                                                "disease_name":"fake disease", "serotype": "fake_serotype", "host_status": "unknown",
                                                "submitting_institution": "ChiUniHonKon", "id": "an_id"}
                                             ]
                              }"""

    mock_project_information = """{
                                "name": "JUNO Project",
                                "logo_url": "/imgs/junologo.svg",
                                "project_url": "https://www.gbsgen.net/",
                                "header_links": [
                                    {"label": "About", "url": "https://www.gbsgen.net/#about"},
                                    {"label": "Team", "url": "https://www.gbsgen.net/#team"},
                                    {"label": "Partners", "url": "https://www.gbsgen.net/#partners"},
                                    {"label": "News", "url": "https://www.gbsgen.net/#twitterFeed"},
                                    {"label": "Funders", "url": "https://www.gbsgen.net/#funders"}
                                ],
                                "contacts": [
                                    {"label": "Monocle Help", "url": "mailto:monocle-help@sanger.ac.uk"},
                                    {"label": "Stephen Bentley", "url": "mailto:sdb@sanger.ac.uk"}
                                ]
                                }"""

    mock_metadata_field = "any_filter_field"
    mock_in_silico_field = "any_in_silico_field"
    mock_metadata_values = ["any", "metadata", "values"]
    mock_in_silico_values = ["any", "in", "silico", "values"]

    expected_sanger_sample_ids = ["5903STDY8059053", "5903STDY8059055"]
    required_sample_dict_keys = ["sanger_sample_id", "public_name", "submitting_institution"]

    def setUp(self):
        self.sample_metadata = SampleMetadata(set_up=False)
        self.sample_metadata.monocle_client = MonocleClient(set_up=False)
        self.sample_metadata.monocle_client.set_up(self.test_config)

    def test_init(self):
        self.assertIsInstance(self.sample_metadata, SampleMetadata)

    def test_reject_bad_config(self):
        with self.assertRaises(KeyError):
            doomed = MonocleClient(set_up=False)
            doomed.set_up(self.bad_config)

    def test_missing_config(self):
        with self.assertRaises(FileNotFoundError):
            doomed = MonocleClient(set_up=False)
            doomed.set_up("no_such_config.yml")

    def test_reject_bad_url(self):
        with self.assertRaises(URLError):
            doomed = MonocleClient(set_up=False)
            doomed.set_up(self.test_config)
            doomed.config[self.mock_project]["base_url"] = self.bad_api_host
            endpoint = doomed.config[self.mock_project]["samples"] + self.expected_sanger_sample_ids[0]
            doomed.make_request("http://fake-container" + endpoint)

    def test_reject_bad_endpoint(self):
        with self.assertRaises(URLError):
            doomed = MonocleClient(set_up=False)
            doomed.set_up(self.test_config)
            doomed.config[self.mock_project]["base_url"] = self.genuine_api_host
            endpoint = self.bad_api_endpoint + self.expected_sanger_sample_ids[0]
            doomed.make_request("http://fake-container" + endpoint)

    @patch("DataSources.sample_metadata.MonocleClient.make_request")
    def test_get_project_information(self, mock_query):
        expected_project_response = {"project": 42}
        mock_query.return_value = json.dumps(expected_project_response)

        actual_project_information = self.sample_metadata.get_project_information(self.mock_project)

        self.assertEqual(expected_project_response["project"], actual_project_information)

    @patch("DataSources.sample_metadata.MonocleClient.make_request")
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

    @patch.object(MonocleClient, "make_request")
    def test_reject_bad_get_sample_response(self, mock_request):
        with self.assertRaises(ProtocolError):
            mock_request.return_value = self.mock_bad_get_sample
            self.sample_metadata.get_samples(self.mock_project, self.expected_sanger_sample_ids[0])
