#!/usr/bin/env python3

from contextlib import contextmanager
import os
from os import path
from pathlib import Path

import argparse
from sys import argv
import logging

from DataSources.monocledb import MonocleDB
from DataSources.sequencing_status import SequencingStatus
from MonocleDash import monocleclient

INITIAL_DIR = Path().absolute()
OUTPUT_SUBDIR='data_view'

def create_download_view_for_sample_data(db, institution_name_to_id):
  institutions = list(db.get_institution_names())
  
  if 0 == len(institutions):
    logging.warning('No institutions were found.')
  
  else:
    for institution in institutions:
      lane_ids = _get_lane_ids(institution, db)
  
      with _cd(Path().joinpath(INITIAL_DIR,OUTPUT_SUBDIR)):
  
        if lane_ids:
          institution_readable_id = institution_name_to_id[institution]
          _mkdir(institution_readable_id)
  
          with _cd(institution_readable_id):
            for lane_id in lane_ids:
              _create_lane_dir_with_symlinks(lane_id, institution)
      


def _get_lane_ids(institution, db):
  sample_ids = [ sample['sample_id'] for sample in db.get_samples(institutions=[institution]) ]
  if not sample_ids:
    logging.warning(f'No sample IDs for {institution} were found in the DB')
    return []
  seq_data = _get_sequencing_status_data(sample_ids)
  # this list contains all the lanes for sampels from this institution
  # (we don't need to know which lanes came from each sample originally)
  all_lanes = []
  for this_sample in seq_data.keys():
    for this_lane in seq_data[this_sample]['lanes']:
       all_lanes.append(this_lane['id'])
  if 0 == len(all_lanes):
   logging.warning(f'No lanes for {institution} were returned from the DB')
  return all_lanes


def _get_sequencing_status_data(sample_ids):
  return SequencingStatus().get_multiple_samples(sample_ids)


def _create_lane_dir_with_symlinks(lane_id, institution):
  data_files = _get_data_files(lane_id)

  if data_files:
    _mkdir(lane_id)

    with _cd(lane_id):
      for data_file in data_files:
        path_to_data_file = data_file.resolve()
        _create_symlink_to(path_to_data_file, data_file)

  else:
    logging.warning(f'No data files for the lane {lane_id} for {institution} were found.')


def _get_data_files(lane_id):
  with _cd(INITIAL_DIR):
    return Path().glob(f'{lane_id}.*')


def _create_symlink_to(path_to_file, symlink_name):
  Path(symlink_name).symlink_to(path_to_file)
  logging.info(f'Symlink "{symlink_name}" to {path_to_file} was created.')


def get_institutions():
   name_to_id = {}
   institutions = monocleclient.MonocleData().get_institutions()
   for this_institution_id in institutions.keys():
      name_to_id[ institutions[this_institution_id]['name'] ] = this_institution_id
   return name_to_id


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
  Path(dir_name).mkdir(exist_ok=True)
  logging.info(f'Directory {dir_name} was created at {Path().absolute()}.')


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Create sample data view')
  parser.add_argument("-L", "--log_level", help="Logging level [default: WARNING]", choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'], default='WARNING')
  options = parser.parse_args(argv[1:])

  logging.basicConfig(format='%(levelname)s: %(message)s.', level=options.log_level)

  create_download_view_for_sample_data(MonocleDB(), get_institutions())
