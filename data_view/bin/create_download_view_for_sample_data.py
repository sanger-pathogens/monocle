#!/usr/bin/env python3

from contextlib import contextmanager
import os
from os import path
from pathlib import Path

from DataSources.monocledb import MonocleDB
from DataSources.sequencing_status import SequencingStatus

INSTITUTION_NAME_TO_ID = {
  'Faculty of Pharmacy, Suez Canal University': 'FacPhaSueCanUni',
  'Laboratório Central do Estado do Paraná': 'LabCenEstPar',
  'National Reference Laboratories': 'NatRefLab',
  'The Chinese University of Hong Kong': 'TheChiUniHonKon',
  'Universidade Federal do Rio de Janeiro': 'UniFedRioJan',
  'Wellcome Sanger Institute': 'WelSanIns'
}
INITIAL_DIR = Path().absolute()


def create_download_view_for_sample_data(db):
  institutions = db.get_institution_names()
  for institution in institutions:
    lane_ids = _get_lane_ids(institution, db)

    if lane_ids:
      institution_readable_id = INSTITUTION_NAME_TO_ID[institution]
      _mkdir(institution_readable_id)

      with _cd(institution_readable_id):
        for lane_id in lane_ids:
          _create_lane_dir_with_symlinks(lane_id)


def _get_lane_ids(institution, db):
  sample_ids = [ sample['sample_id'] for sample in db.get_samples(institutions=[institution]) ]
  if not sample_ids:
    return []
  return _get_sequencing_status_data(sample_ids).get('lane_id', [])


def _get_sequencing_status_data(sample_ids):
  return SequencingStatus().get_multiple_samples(sample_ids)


def _create_lane_dir_with_symlinks(lane_id):
  data_files = _get_data_files(lane_id)

  if data_files:
    _mkdir(lane_id)

    with _cd(lane_id):
      for data_file in data_files:
        path_to_data_file = data_file.resolve()
        _create_symlink_to(path_to_data_file, data_file)


def _get_data_files(lane_id):
  with _cd(INITIAL_DIR):
    return Path().glob(f'{lane_id}.*')


def _create_symlink_to(path_to_file, symlink_name):
  Path(symlink_name).symlink_to(path_to_file)


# Allows to `cd` in the context of the `with` statement and automatically
# `cd` back  upon leaving the corresponding`with` statement
# (credits to https://stackoverflow.com/a/24176022/4579279).
@contextmanager
def _cd(dir):
  prev_dir = os.getcwd()
  os.chdir(path.expanduser(dir))
  try:
    yield
  finally:
    os.chdir(prev_dir)


def _mkdir(dir_name):
  Path(dir_name).mkdir()


if __name__ == '__main__':
  create_download_view_for_sample_data(MonocleDB())
