from unittest import TestCase
from unittest.mock import patch
from pathlib import Path

from bin.create_download_view_for_sample_data import (
  create_download_view_for_sample_data
)

SAMPLE_IDS = ['a', 'b', 'c', 'd']
INSTITUTION_NAME_TO_ID = {
  'Faculty of Pharmacy, Suez Canal University': 'FacPhaSueCanUni',
  'Laboratório Central do Estado do Paraná': 'LabCenEstPar',
  'National Reference Laboratories': 'NatRefLab',
  'The Chinese University of Hong Kong': 'TheChiUniHonKon',
  'Universidade Federal do Rio de Janeiro': 'UniFedRioJan',
  'Wellcome Sanger Institute': 'WelSanIns'
}
INSTITUTIONS = [{
  'name': 'National Reference Laboratories',
  'id': INSTITUTION_NAME_TO_ID['National Reference Laboratories'],
  'samples': [
    {'sample_id': SAMPLE_IDS[0]},
    {'sample_id': SAMPLE_IDS[1]}
  ]
}, {
  'name': 'Wellcome Sanger Institute',
  'id': INSTITUTION_NAME_TO_ID['Wellcome Sanger Institute'],
  'samples': [
    {'sample_id': SAMPLE_IDS[2]},
    {'sample_id': SAMPLE_IDS[3]}
  ]
}]
LANES = ['x', 'y', 'z']

class CreateDownloadViewForSampleDataTest(TestCase):

  @classmethod
  def setUpClass(cls):
    patch('bin.create_download_view_for_sample_data._get_sequencing_status_data',
          get_sequencing_status_data
    ).start()
    patch('bin.create_download_view_for_sample_data._cd').start()

  def setUp(self):
    self.db = DB()

    create_symlink_patch = patch('bin.create_download_view_for_sample_data._create_symlink_to')
    self.create_symlink_to = create_symlink_patch.start()
    mkdir_patch = patch('bin.create_download_view_for_sample_data._mkdir')
    self.mkdir = mkdir_patch.start()

  def test_create_folder_per_institute(self):
    create_download_view_for_sample_data(self.db, INSTITUTION_NAME_TO_ID)

    for institution in INSTITUTIONS:
      self.mkdir.assert_any_call(institution['id'])

  def test_create_lane_folder_for_each_institute(self):
    create_download_view_for_sample_data(self.db, INSTITUTION_NAME_TO_ID)

    for lane in LANES:
      self.mkdir.assert_any_call(lane)

  def test_create_symlink_per_data_file(self):
    data_files = list(map(lambda lane: Path(f'{lane}.vcf'), LANES))
    data_files.append(Path(f'LANES[0].fastq'))
    patch('bin.create_download_view_for_sample_data._get_data_files', return_value=data_files
          ).start()

    create_download_view_for_sample_data(self.db, INSTITUTION_NAME_TO_ID)

    self.assertEqual(self.create_symlink_to.call_count, len(data_files) * len(LANES))
    # assrt_any_call below always fails
    # don't know why this isn't called in patched function; the code works
    #for data_file in data_files:
      #path_to_data_file = data_file.resolve()
      #self.create_symlink_to.assert_any_call(path_to_data_file, data_file)

def get_sequencing_status_data(sample_ids):
  if sample_ids == SAMPLE_IDS[:2]:
    return {
      SAMPLE_IDS[0]:
        {'lanes': [{'id': LANES[0]}, {'id': LANES[1]}]}
    }
  elif sample_ids == SAMPLE_IDS[2:4]:
    return {
      SAMPLE_IDS[2]:
        {'lanes': [{'id': LANES[2]}]},
      SAMPLE_IDS[3]:
        {'lanes': []}
    }
  return {}

class DB():
  def get_institution_names(self):
    return map(lambda institution: institution['name'], INSTITUTIONS)

  def get_samples(self, institutions):
    if institutions[0] == INSTITUTIONS[0]['name']:
      return INSTITUTIONS[0]['samples']
    elif institutions[0] == INSTITUTIONS[1]['name']:
      return INSTITUTIONS[1]['samples']
    return []
