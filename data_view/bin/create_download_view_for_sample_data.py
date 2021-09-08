#!/usr/bin/env python3

from contextlib import contextmanager
import os
from os import path
from pathlib import Path

import argparse
from sys import argv
import logging

from dash.api.service.DataSources.sample_metadata import SampleMetadata
from dash.api.service.DataSources.sequencing_status import SequencingStatus
from dash.api.service.data_services import MonocleData

INITIAL_DIR = Path().absolute()
# directory in which the data files are located
DATA_DIR='/home/ubuntu/monocle_juno'
OUTPUT_SUBDIR='monocle_juno_institution_view'

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
  logging.info("{}: {} samples".format(institution,len(sample_ids)))
  if not sample_ids:
    logging.warning(f'No sample found for {institution}')
    return []
  seq_data = _get_sequencing_status_data(sample_ids)
  # this list contains all the lanes for sampels from this institution
  # (we don't need to know which lanes came from each sample originally)
  all_lanes = []
  for this_sample in seq_data.keys():
    for this_lane in seq_data[this_sample]['lanes']:
       all_lanes.append(this_lane['id'])
  logging.info("{}: {} lanes".format(institution,len(all_lanes)))
  if 0 == len(all_lanes):
    logging.warning(f'No lanes found for {institution}')
  return all_lanes


def _get_sequencing_status_data(sample_ids):
  return SequencingStatus().get_multiple_samples(sample_ids)


def _create_lane_dir_with_symlinks(lane_id, institution):
  data_files = _get_data_files(lane_id)

  logging.debug(f'Creating directory {lane_id} for lane {lane_id} for {institution}.')
  _mkdir(lane_id)

  with _cd(lane_id):
    directory_containing_symlinks = Path().absolute()
    logging.debug(f'Creating symlinks in {directory_containing_symlinks} for lane {lane_id} for {institution}.')
    for data_file in data_files:
      _create_symlink_to(data_file, data_file.name)


def _get_data_files(lane_id):
   
  data_files_for_this_lane = []
   
  with _cd(DATA_DIR):
    data_files_for_this_lane = list(Path().glob(f'**/{lane_id}[_.]*'))
    if len(data_files_for_this_lane) > 0:
      logging.debug("found {} data files for lane {}".format(len(data_files_for_this_lane),lane_id))
      # store absolute paths
      data_files_for_this_lane = [ d.resolve() for d in data_files_for_this_lane ]
    else:
      # we expect that there will be data files that are not found;
      # it just means that the lane has been sequenced, but has not
      # been through the pipelines
      # TODO we could look at the pipeline status to check if we expect
      #      that a file should exist; this would be a useful data integrity test
      logging.debug("no data files for lane {}".format(lane_id))
      
  return data_files_for_this_lane


def _create_symlink_to(path_to_file, symlink_name):
  logging.debug(f'Creating symlink "{symlink_name}" -> {path_to_file}.')
  if not Path(path_to_file).is_file():
    logging.error("data file {} does not exist".format(path_to_file))
  else:
    if Path(symlink_name).is_symlink():
      logging.debug("symlink {} already exists: not recreated".format(symlink_name))
    else:
      Path(symlink_name).symlink_to(path_to_file)


def get_institutions(sample_metadata):
   name_to_id = {}
   # set_up = False stops MonocleData instantiating lots of objects we don't need...
   dashboard_data = MonocleData(set_up=False)
   # ...but that means we need to give it a SampleMetadata
   dashboard_data.sample_metadata = sample_metadata
   institutions = dashboard_data.get_institutions()
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
  if Path(dir_name).is_dir():
     logging.debug(f'Directory {dir_name} already exists in {Path().absolute()}.')
  else:
    Path(dir_name).mkdir()
    logging.info(f'Directory {dir_name} was created at {Path().absolute()}.')


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Create sample data view')
  parser.add_argument("-D", "--data_dir", help="Data file directory [default: {}]".format(DATA_DIR), default=DATA_DIR )
  parser.add_argument("-L", "--log_level", help="Logging level [default: WARNING]", choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'], default='WARNING')
  options = parser.parse_args(argv[1:])

  DATA_DIR=options.data_dir

  # adding `module` for log format allows us to filter out messages from SampleMetadata or squencing_status,
  # which can be handy
  logging.basicConfig(format='%(asctime)-15s %(levelname)s %(module)s:  %(message)s', level=options.log_level)

  sample_metadata = SampleMetadata()

  create_download_view_for_sample_data(sample_metadata, get_institutions(sample_metadata))
