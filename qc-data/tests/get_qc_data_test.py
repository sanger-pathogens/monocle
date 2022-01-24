from unittest import TestCase
from unittest.mock import patch, Mock, call, ANY

from bin.get_qc_data import (
    get_lane_ids,
    _get_relative_abundance,
    update_relative_abundance,
    get_arguments,
    main
)
from lib.qc_data import QCData
from datetime import datetime
import os
import argparse
import shutil
import json

INSTITUTIONS = {
  "institutions": {
    "FacPhaSueCanUni": {
      "name": "Faculty of Pharmacy, Suez Canal University",
      "db_key": "Faculty of Pharmacy, Suez Canal University"
    },
    "LabCenEstPar": {
      "name": "Laboratório Central do Estado do Paraná",
      "db_key": "Laboratório Central do Estado do Paraná"
    },
    "NatRefLab": {
      "name": "National Reference Laboratories",
      "db_key": "National Reference Laboratories"
    },
    "TheChiUniHonKon": {
      "name": "The Chinese University of Hong Kong",
      "db_key": "The Chinese University of Hong Kong"
    },
    "UniFedRioJan": {
      "name": "Universidade Federal do Rio de Janeiro",
      "db_key": "Universidade Federal do Rio de Janeiro"
    },
    "WelSanIns": {
      "name": "Wellcome Sanger Institute",
      "db_key": "Wellcome Sanger Institute"
    }
  }
}

SAMPLE_IDS = ['a', 'b', 'c', 'd', 'e']
PUBLIC_NAMES = list(
  map(lambda sample_id: sample_id * 2, SAMPLE_IDS))
INSTITUTION_WITHOUT_LANES = {
  'name': INSTITUTIONS['institutions']['FacPhaSueCanUni']['name'],
  'id': 'FacPhaSueCanUni',
  'samples': [
    {'public_name': PUBLIC_NAMES[4], 'sample_id': SAMPLE_IDS[4]}
  ]
}
INSTITUTIONS_WITH_PUBLIC_NAMES = [{
  'name': INSTITUTIONS['institutions']['NatRefLab']['name'],
  'id': 'NatRefLab',
  'samples': [
    {'public_name': PUBLIC_NAMES[0], 'sample_id': SAMPLE_IDS[0]},
    {'public_name': PUBLIC_NAMES[1], 'sample_id': SAMPLE_IDS[1]}
  ]
}, {
  'name': INSTITUTIONS['institutions']['WelSanIns']['name'],
  'id': 'WelSanIns',
  'samples': [
    {'public_name': PUBLIC_NAMES[2], 'sample_id': SAMPLE_IDS[2]},
    {'public_name': PUBLIC_NAMES[3], 'sample_id': SAMPLE_IDS[3]}
  ]
},
  INSTITUTION_WITHOUT_LANES
]
INSTITUTIONS_WITHOUT_PUBLIC_NAMES = [{
  'name': INSTITUTIONS['institutions']['UniFedRioJan']['name'],
  'id': 'UniFedRioJan',
  'samples': []
}]
INSTITUTIONS = INSTITUTIONS_WITH_PUBLIC_NAMES + INSTITUTIONS_WITHOUT_PUBLIC_NAMES
LANES = ['x', 'y', 'z']
SEQUENCING_STATUS_DATA = {
  SAMPLE_IDS[0]: {
    SAMPLE_IDS[0]:
      {'lanes': [{'id': LANES[0]}, {'id': LANES[1]}]}
  },
  SAMPLE_IDS[1]: {},
  SAMPLE_IDS[2]: {
    SAMPLE_IDS[2]:
      {'lanes': [{'id': LANES[2]}]}
  },
  SAMPLE_IDS[3]: {
    SAMPLE_IDS[3]:
      {'lanes': []}
  },
  SAMPLE_IDS[4]: {
    SAMPLE_IDS[4]:
      {'lanes': []}
  }
}

def get_sequencing_status_data(sample_ids):
  return SEQUENCING_STATUS_DATA[sample_ids[0]]

class DB():
  def get_institution_names(self):
    return map(lambda institution: institution['name'], INSTITUTIONS)

  def get_samples(self, institutions):
    if institutions[0] == INSTITUTIONS[0]['name']:
      return INSTITUTIONS[0]['samples']
    elif institutions[0] == INSTITUTIONS[1]['name']:
      return INSTITUTIONS[1]['samples']
    elif institutions[0] == INSTITUTIONS[2]['name']:
      return INSTITUTIONS[2]['samples']
    return []

TEST_DATA_DIR = 'tests/get_qc_test_data'
LANE_ID1 = 'test_lane1'
LANE_ID2 = 'test_lane2'
LANE_ID3 = 'test_lane3'
TEST_KRAKEN_REPORT = f'{TEST_DATA_DIR}/{LANE_ID1}_kraken.report'
TEST_JSON1 = f'{TEST_DATA_DIR}/{LANE_ID1}/qc_data.json'
TEST_JSON2 = f'{TEST_DATA_DIR}/{LANE_ID2}/qc_data.json'
TEST_JSON3 = f'{TEST_DATA_DIR}/{LANE_ID3}/qc_data.json'

class GetQCData(TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            patch('bin.get_qc_data._get_sequencing_status_data',
                  get_sequencing_status_data
            ).start()
            patch('bin.get_qc_data.QC_DIR', TEST_DATA_DIR).start()
        except Exception as e:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        # Copy the original json file back to one that was overwritten
        shutil.copyfile(TEST_JSON1, TEST_JSON2)

    def setUp(self):
        self.db = DB()

    def test_get_lane_ids(self):
        actual = get_lane_ids(self.db)

        self.assertEqual(['x', 'y', 'z'], actual)

    def test_get_relative_abundance(self):
        actual = _get_relative_abundance(TEST_KRAKEN_REPORT, "Streptococcus agalactiae")

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

        qc_data = update_relative_abundance(LANE_ID1, TEST_DATA_DIR, "Streptococcus agalactiae", QCData(TEST_JSON1))

        self.assertEqual(expected, qc_data.get_data())


    @patch('bin.get_qc_data.datetime')
    def test_update_relative_abundance_with_no_initial_qc_data(self, mock_datetime):
        mock_datetime.now = Mock(return_value=datetime(2021, 12, 21))
        expected = {
            "rel_abundance": [
                {
                    "species": "Streptococcus agalactiae",
                    "value": "92.38",
                    "timestamp": "2021-12-21 00:00:00"
                }
            ]
        }

        qc_data = update_relative_abundance(LANE_ID3, TEST_DATA_DIR, "Streptococcus agalactiae", QCData(TEST_JSON3))

        self.assertEqual(expected, qc_data.get_data())


    def test_get_arguments(self):
        actual = get_arguments().parse_args(['--kraken_data_dir', 'kraken_reports_directory', '--species', 'Streptococcus agalactiae'])

        self.assertEqual(actual,
                         argparse.Namespace(kraken_data_dir='kraken_reports_directory', species='Streptococcus agalactiae', log_level='WARNING'))

    def test_get_arguments_short_options(self):
        actual = get_arguments().parse_args(['-D', 'kraken_reports_directory', '-S', 'Streptococcus agalactiae'])

        self.assertEqual(actual,
                         argparse.Namespace(kraken_data_dir='kraken_reports_directory', species='Streptococcus agalactiae', log_level='WARNING'))

    @patch('bin.get_qc_data.get_arguments')
    @patch('bin.get_qc_data.SampleMetadata')
    @patch('bin.get_qc_data.get_lane_ids')
    @patch('bin.get_qc_data.datetime')
    def test_main(self, mock_datetime, mock_get_lane_ids, mock_sample_metadata, mock_get_arguments):

        args = mock_get_arguments.return_value.parse_args()
        args.kraken_data_dir = TEST_DATA_DIR
        args.species = 'Streptococcus agalactiae'
        args.log_level = 'WARNING'
        mock_sample_metadata.return_value = DB
        mock_get_lane_ids.return_value = [LANE_ID2]
        mock_datetime.now = Mock(return_value=datetime(2021, 12, 21))

        main()

        f = open(TEST_JSON2)
        actual = json.load(f)
        f.close()
        self.assertEqual(actual, {
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
        })
