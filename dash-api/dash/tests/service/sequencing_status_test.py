import logging
from unittest import TestCase
from unittest.mock import patch
from urllib.error import URLError

from DataSources.sequencing_status import MLWH_Client, ProtocolError, SequencingStatus

logging.basicConfig(format="%(asctime)-15s %(levelname)s:  %(message)s", level="CRITICAL")


class SequencingStatusTest(TestCase):

    test_config = "dash/tests/mock_data/data_sources.yml"
    bad_config = "dash/tests/mock_data/data_sources_bad.yml"
    genuine_api_host = "http://mlwh_api.dev.pam.sanger.ac.uk/"
    bad_api_host = "http://no.such.host/"
    bad_api_endpoint = "/no/such/endpoint"
    base_url_regex = "^https?://[\w\-]+(\.dev)?\.pam\.sanger\.ac\.uk$"
    endpoint_regex = "(/[\w\-\.]+)+"
    required_sample_keys = {
        "lanes": type(["a list"]),
        "dna_measured_volume": type(1.1),
        "dna_concentration": type(1.1),
        "total_dna_ng": type(1.1),
        "pool_barcode": type("a string"),
        "creation_datetime": type("a string"),
        "library_prep_complete": type("a string"),
    }
    absent_sample_keys = ["id"]
    required_lane_keys = {
        "id": type("a string"),
        "qc_lib": type(1),
        "qc_seq": type(1),
        "run_status": type("a string"),
        "qc_started": type(1),
        "qc_complete_datetime": type("a string"),
        "complete_datetime": type("a string"),
        "q30_yield_forward": type(1),
        "q30_yield_reverse": type(1),
        "q30_total_yield": type(1),
    }

    expected_sample_ids = ["5903STDY8059053", "5903STDY8059055"]

    mock_bad_get_sample = """{  "wrong key":
                                       {  "does": "not matter what appears here"
                                       }
                                    }"""

    mock_get_sample = """{   "sample":
                                       {
                                          "id": "5903STDY8059053",
                                          "lanes": [
                                          {
                                             "id": "31663_7#43",
                                             "qc_lib": 1,
                                             "qc_seq": 1,
                                             "run_status": "qc complete",
                                             "qc_started": 1,
                                             "qc_complete_datetime": "2019-09-22T01:59:30Z",
                                             "complete_datetime": "2019-09-20T01:20:53Z",
                                             "q30_yield_forward": 170437,
                                             "q30_yield_reverse": 160998,
                                             "q30_total_yield": 331435
                                          }
                                          ],
                                          "dna_measured_volume": 26.9784,
                                          "dna_concentration": 195.72,
                                          "total_dna_ng": 5280.21,
                                          "pool_barcode": "NT1570031O",
                                          "creation_datetime": "2019-09-18T08:46:35Z",
                                          "library_prep_complete": "2019-09-19T08:46:35Z"
                                       }
                                    }"""

    mock_get_multiple_samples = """{   "samples": [
                                       {
                                          "id": "5903STDY8059053",
                                          "lanes": [
                                          {
                                             "id": "31663_7#43",
                                             "qc_lib": 1,
                                             "qc_seq": 1,
                                             "run_status": "qc complete",
                                             "qc_started": 1,
                                             "qc_complete_datetime": "2019-09-22T01:59:30Z",
                                             "complete_datetime": "2019-09-20T01:20:53Z",
                                             "q30_yield_forward": 170437,
                                             "q30_yield_reverse": 160998,
                                             "q30_total_yield": 331435
                                          }
                                          ],
                                          "dna_measured_volume": 26.9784,
                                          "dna_concentration": 195.72,
                                          "total_dna_ng": 5280.21,
                                          "pool_barcode": "NT1570031O",
                                          "creation_datetime": "2019-09-18T08:46:35Z",
                                          "library_prep_complete": "2019-09-19T08:46:35Z"
                                       },
                                       {
                                          "id": "5903STDY8059055",
                                          "lanes": [
                                          {
                                             "id": "31663_7#52",
                                             "qc_lib": 1,
                                             "qc_seq": 1,
                                             "run_status": "qc complete",
                                             "qc_started": 1,
                                             "qc_complete_datetime": "2019-09-22T01:59:30Z",
                                             "complete_datetime": "2019-09-20T01:20:53Z",
                                             "q30_yield_forward": 194391,
                                             "q30_yield_reverse": 182730,
                                             "q30_total_yield": 377121
                                          }
                                          ],
                                          "dna_measured_volume": 27.136,
                                          "dna_concentration": 200.974,
                                          "total_dna_ng": 5453.63,
                                          "pool_barcode": "NT1570031O",
                                          "creation_datetime": "2019-09-18T08:46:35Z",
                                          "library_prep_complete": "2019-09-19T08:46:35Z"
                                       }
                                    ]
                                    }"""

    def setUp(self):
        self.seq_status = SequencingStatus(set_up=False)
        self.seq_status.mlwh_client = MLWH_Client(set_up=False)
        self.seq_status.mlwh_client.set_up(self.test_config)

    def test_init(self):
        self.assertIsInstance(self.seq_status, SequencingStatus)
        self.assertIsInstance(self.seq_status.mlwh_client, MLWH_Client)

    def test_init_values(self):
        self.assertRegex(self.seq_status.mlwh_client.config["mlwh_api_connection"]["base_url"], self.base_url_regex)
        self.assertRegex(self.seq_status.mlwh_client.config["swagger"], self.endpoint_regex)
        self.assertRegex(self.seq_status.mlwh_client.config["findById"], self.endpoint_regex)
        self.assertIsInstance(self.seq_status.mlwh_client.config["findById_key"], type("a string"))
        self.assertRegex(self.seq_status.mlwh_client.config["findByIds"], self.endpoint_regex)
        self.assertIsInstance(self.seq_status.mlwh_client.config["findByIds_key"], type("a string"))

    def test_reject_bad_config(self):
        with self.assertRaises(KeyError):
            doomed = MLWH_Client(set_up=False)
            doomed.set_up(self.bad_config)

    def test_missing_config(self):
        with self.assertRaises(FileNotFoundError):
            doomed = MLWH_Client(set_up=False)
            doomed.set_up("no_such_config.yml")

    # @patch('DataSources.sequencing_status.datetime')
    @patch.object(MLWH_Client, "make_request")
    def test_get_sample(self, mock_request):
        ##from datetime import date
        ##mock_datetime.datetime.now.return_value = date(2010, 3, 19)
        mock_request.return_value = self.mock_get_sample
        sample = self.seq_status.get_sample(self.expected_sample_ids[0])
        self.assertIsInstance(sample, type({"a": "dict"}))
        for required in self.required_sample_keys.keys():
            self.assertTrue(required in sample, msg="required key '{}' not found in sample dict".format(required))
            self.assertIsInstance(
                sample[required],
                self.required_sample_keys[required],
                msg="sample item {} is wrong type".format(required),
            )

    @patch.object(MLWH_Client, "make_request")
    def test_get_multiple_samples(self, mock_request):
        mock_request.return_value = self.mock_get_multiple_samples
        samples = self.seq_status.get_multiple_samples(self.expected_sample_ids)
        self.assertIsInstance(samples, type({"a": "dict"}))
        for this_sample_id in self.expected_sample_ids:
            self.assertTrue(
                this_sample_id in samples,
                msg="test sample ID '{}' not returned by get_multiple_samples()".format(this_sample_id),
            )
        for this_sample_id in samples.keys():
            this_sample = samples[this_sample_id]
            self.assertIsInstance(
                this_sample, type({"a": "dict"}), msg="sample should be a dict, not {}".format(type(this_sample))
            )
            for required in self.required_sample_keys.keys():
                self.assertTrue(
                    required in this_sample, msg="required key '{}' not found in sample dict".format(required)
                )
                self.assertIsInstance(
                    this_sample[required],
                    self.required_sample_keys[required],
                    msg="sample item {} is wrong type".format(required),
                )
            for required_absent in self.absent_sample_keys:
                self.assertFalse(
                    required_absent in this_sample,
                    msg="key '{}' found in sample dict, but it should be absent".format(required_absent),
                )
            for this_lane in this_sample["lanes"]:
                for required in self.required_lane_keys.keys():
                    self.assertTrue(
                        required in this_lane, msg="required key '{}' not found in lane dict".format(required)
                    )
                    self.assertIsInstance(
                        this_lane[required],
                        self.required_lane_keys[required],
                        msg="lane item {} is wrong type".format(required),
                    )

    @patch.object(MLWH_Client, "make_request")
    def test_reject_bad_get_sample_response(self, mock_request):
        with self.assertRaises(ProtocolError):
            mock_request.return_value = self.mock_bad_get_sample
            self.seq_status.get_sample(self.expected_sample_ids[0])

    def test_reject_bad_url(self):
        with self.assertRaises(URLError):
            doomed = MLWH_Client(set_up=False)
            doomed.set_up(self.test_config)
            doomed.config["mlwh_api_connection"]["base_url"] = self.bad_api_host
            endpoint = doomed.config["findById"] + self.expected_sample_ids[0]
            doomed.make_request(endpoint)

    def test_reject_bad_endpoint(self):
        with self.assertRaises(URLError):
            doomed = MLWH_Client(set_up=False)
            doomed.set_up(self.test_config)
            doomed.config["mlwh_api_connection"]["base_url"] = self.genuine_api_host
            endpoint = self.bad_api_endpoint + self.expected_sample_ids[0]
            doomed.make_request(endpoint)
