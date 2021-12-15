from unittest import TestCase
from unittest.mock import patch, Mock
from bin.get_qc_data import _get_relative_abundance, update_relative_abundance
from lib.qc_data import QCData
from datetime import datetime
import os

class GetQCData(TestCase):

    test_json = 'tests/test_data/test_qc_data.json'
    test_kraken_report = 'tests/test_data/test_kraken.report'
    test_data_dir = 'tests/test_data'
    lane_id = 'test'

    def setUp(self):
        self.qc_data = QCData(self.test_json)


    def test_get_relative_abundance(self):
        actual = _get_relative_abundance(self.test_kraken_report, "Streptococcus agalactiae")

        self.assertEqual("92.38", actual)


    @patch('bin.get_qc_data.datetime')
    def test_update_relative_abundance(self, mock_datetime):
        mock_datetime.now = Mock(return_value=datetime(2021, 12, 21))
        expected = {
            "rel_abundance": [
                {
                    "species": "Streptococcus agalactiae",
                    "value": "97.65",
                    "timestamp": "2021-12-15 09:32:59"
                },
                {
                    "species": "Streptococcus agalactiae",
                    "value": "92.38",
                    "timestamp": "2021-12-21 00:00:00"
                }
            ]
        }

        qc_data = update_relative_abundance(self.lane_id, self.test_data_dir, "Streptococcus agalactiae", self.qc_data)

        self.assertEqual(expected, qc_data.get_data())

        os.rmdir(self.lane_id)
