#!/usr/bin/env python3

from contextlib import contextmanager
import os
from os import path
from pathlib import Path
from urllib.error import HTTPError

import argparse
from sys import argv
import logging

from dash.api.service.DataSources.sample_metadata           import SampleMetadata
from dash.api.service.DataSources.sequencing_status         import SequencingStatus
from dash.api.service.DataServices.sample_tracking_services import MonocleSampleTracking

INITIAL_DIR = Path().absolute()
OUTPUT_SUBDIR='monocle_juno_institution_view'

def create_download_view_for_sample_data(db, institution_name_to_id, data_dir):
  logging.info('Getting list of institutions')
  institutions = list(db.get_institution_names())
  
  if 0 == len(institutions):
    logging.warning('No institutions were found.')
  
  else:
    for institution in institutions:
      logging.info(f'{institution}: getting samples and lane information')
      public_names_to_lane_ids = _get_public_names_with_lane_ids(institution, db)
  
      logging.info(f'{institution}: creating subdirectories')
      with _cd(Path().joinpath(INITIAL_DIR, OUTPUT_SUBDIR)):
  
        if public_names_to_lane_ids:
          institution_readable_id = institution_name_to_id[institution]
          _mkdir(institution_readable_id)
  
          with _cd(institution_readable_id):
            for public_name, lane_ids in public_names_to_lane_ids.items():
              for lane_id in lane_ids:
                _create_public_name_dir_with_symlinks(
                  public_name, lane_id, institution, data_dir)
              if not lane_ids:
                logging.debug(f'Creating empty directory "{public_name}" for {institution}.')
                _mkdir(public_name)


def _get_public_names_with_lane_ids(institution, db):
  public_names_to_sample_id = {
    sample["public_name"]: sample["sample_id"] for sample in db.get_samples(institutions=[institution])}

  logging.info(f'{institution}: {len(public_names_to_sample_id)} public names')

  num_lanes = 0
  public_names_to_lane_ids = {}
  for public_name, sample_id in public_names_to_sample_id.items():
    # MLWH API can be fragile: catch HTTP errors
    try:
      seq_data = _get_sequencing_status_data([sample_id])
      lane_ids_of_one_sample = []
      for sample in seq_data.keys():
        for lane in seq_data[sample]['lanes']:
          num_lanes += 1
          lane_ids_of_one_sample.append(lane['id'])
      if lane_ids_of_one_sample:
        logging.debug(f'{institution}: {len(lane_ids_of_one_sample)} lanes for "{public_name}"')
        public_names_to_lane_ids[public_name] = lane_ids_of_one_sample
      else:
        logging.debug(f'{institution}: No lanes found for "{public_name}"')
        # We add public names w/ no lanes, as we want to
        # create empty public name directories as well.
        public_names_to_lane_ids[public_name] = []
    except HTTPError as e:
      logging.error('Failed to get sequence data for {} sample {}: {}'.format(institution,public_name,repr(e)))

  logging.info(f'{institution} has a total of {num_lanes} lanes')

  return public_names_to_lane_ids


def _get_sequencing_status_data(sample_ids):
  return SequencingStatus().get_multiple_samples(sample_ids)


def _create_public_name_dir_with_symlinks(public_name, lane_id, institution, data_dir):
  data_files = _get_data_files(lane_id, data_dir)

  logging.debug(f'Creating directory "{public_name}" for lane {lane_id} for {institution}.')
  _mkdir(public_name)

  with _cd(public_name):
    directory_containing_symlinks = Path().absolute()
    logging.debug(f'Creating symlinks in {directory_containing_symlinks} for lane {lane_id} for {institution}.')
    for data_file in data_files:
      _create_symlink_to(data_file, data_file.name)


def _get_data_files(lane_id, data_dir):

  data_files_for_this_lane = []
   
  with _cd(data_dir):
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
   # set_up = False stops MonocleSampleTracking instantiating lots of objects we don't need...
   dashboard_data = MonocleSampleTracking(set_up=False)
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
  parser.add_argument("-D", "--data_dir", help="Data file directory")
  parser.add_argument("-L", "--log_level", help="Logging level [default: WARNING]", choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'], default='WARNING')
  options = parser.parse_args(argv[1:])

  # adding `module` for log format allows us to filter out messages from SampleMetadata or squencing_status,
  # which can be handy
  logging.basicConfig(format='%(asctime)-15s %(levelname)s %(module)s:  %(message)s', level=options.log_level)

  logging.info('Getting sample metadata')
  sample_metadata = SampleMetadata()

  create_download_view_for_sample_data(sample_metadata, get_institutions(sample_metadata), options.data_dir)
