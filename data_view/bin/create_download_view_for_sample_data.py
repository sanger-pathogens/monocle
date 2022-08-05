#!/usr/bin/env python3

import argparse
import logging
import os
import re
import time
from contextlib import contextmanager
from os import path
from pathlib import Path, PurePath
from sys import argv
from urllib.error import HTTPError

from dash.api.service.DataSources.institution_data import InstitutionData
from dash.api.service.DataSources.sample_metadata import SampleMetadata
from dash.api.service.DataSources.sequencing_status import SequencingStatus


def create_download_view_for_sample_data(project, db, institution_keys, data_dir, output_dir):
    data_file_lookup_by_lane_id = _get_data_file_lookup_by_lane_id(data_dir)
    if len(institution_keys) == 0:
        logging.warning("No institutions were given.")
    else:
        for institution_key in institution_keys:
            logging.info(f"{institution_key}: getting samples and lane information")
            public_names_to_lane_ids = _get_public_names_with_lane_ids(project, institution_key, db)

            logging.info(f"{institution_key}: creating subdirectories")
            with _cd(Path(output_dir)):

                if public_names_to_lane_ids:
                    _mkdir(institution_key)

                    with _cd(institution_key):
                        for public_name, lane_ids in public_names_to_lane_ids.items():
                            for lane_id in lane_ids:
                                _create_public_name_dir_with_symlinks(
                                    data_file_lookup_by_lane_id, public_name, lane_id, institution_key, data_dir
                                )
                            if not lane_ids:
                                logging.debug(f'Creating empty directory "{public_name}" for {institution_key}.')
                                _mkdir(public_name)


def _get_data_file_lookup_by_lane_id(data_dir):
    # this find all the data files, and returns a dict to look up the paths from lane IDs
    # (note glob() is slow on big directories, so calling it just once provides a huge speed up)

    # this regex matches data files (files with names based on lane ID)
    # and provides a capture group for the lane ID
    data_file_name_pattern = re.compile(r"^[^/]+/(\d+_\d+#\d+)")
    data_file_lookup_by_lane_id = {}
    num_data_files = 0

    with _cd(data_dir):
        for this_file in list(Path().glob("**/*")):
            # pick out the data files
            data_file_name_match = data_file_name_pattern.search(str(this_file))
            if data_file_name_match:
                lane_id = data_file_name_match.group(1)
                this_file_full_path = PurePath(data_dir).joinpath(this_file)
                logging.debug("Found file for lane {}:  {}".format(lane_id, this_file_full_path))
                num_data_files += 1
                if lane_id in data_file_lookup_by_lane_id:
                    data_file_lookup_by_lane_id[lane_id].append(this_file_full_path)
                else:
                    data_file_lookup_by_lane_id[lane_id] = [this_file_full_path]
    logging.info("Found {} data files under {}".format(num_data_files, data_dir))

    return data_file_lookup_by_lane_id


def _get_public_names_with_lane_ids(project, institution_key, db):

    num_retries = 0
    final_exception = None
    samples_list = None
    while samples_list is None and num_retries < 10:
        num_retries += 1
        try:
            samples_list = db.get_samples(project, institution_keys=[institution_key])
        except Exception as e:
            logging.warning("failed to retrieve samples for institution {}: {}".format(institution_key, e))
            final_exception = e
            time.sleep(10)
    if samples_list is None:
        # if samples_list isn't a list, it means we got to max retries
        # without db.get_samples() running successfully
        logging.error(
            "gave up retrieving samples for {} institution {} after {} attempts".format(
                project, institution_key, num_retries
            )
        )
        raise final_exception

    public_names_to_sanger_sample_id = {sample["public_name"]: sample["sanger_sample_id"] for sample in samples_list}

    logging.info(f"{institution_key}: {len(public_names_to_sanger_sample_id)} public names")

    num_lanes = 0
    public_names_to_lane_ids = {}
    for public_name, sanger_sample_id in public_names_to_sanger_sample_id.items():
        # MLWH API can be fragile: catch HTTP errors
        try:
            seq_data = _get_sequencing_status_data([sanger_sample_id])
            lane_ids_of_one_sample = []
            for sample in seq_data.keys():
                for lane in seq_data[sample]["lanes"]:
                    num_lanes += 1
                    lane_ids_of_one_sample.append(lane["id"])
            if lane_ids_of_one_sample:
                logging.debug(f'{institution_key}: {len(lane_ids_of_one_sample)} lanes for "{public_name}"')
                public_names_to_lane_ids[public_name] = lane_ids_of_one_sample
            else:
                logging.debug(f'{institution_key}: No lanes found for "{public_name}"')
                # We add public names w/ no lanes, as we want to
                # create empty public name directories as well.
                public_names_to_lane_ids[public_name] = []
        except HTTPError as e:
            logging.error(
                "Failed to get sequence data for {} sample {}: {}".format(institution_key, public_name, repr(e))
            )

    logging.info(f"{institution_key} has a total of {num_lanes} lanes")

    return public_names_to_lane_ids


def _get_sequencing_status_data(sanger_sample_ids):
    return SequencingStatus().get_multiple_samples(sanger_sample_ids)


def _create_public_name_dir_with_symlinks(data_file_lookup_by_lane_id, public_name, lane_id, institution_key, data_dir):
    data_files = _get_data_files(data_file_lookup_by_lane_id, lane_id)

    logging.debug(f'Creating directory "{public_name}" for lane {lane_id} for {institution_key}.')
    _mkdir(public_name)

    with _cd(public_name):
        directory_containing_symlinks = Path().absolute()
        logging.debug(f"Creating symlinks in {directory_containing_symlinks} for lane {lane_id} for {institution_key}.")
        for data_file in data_files:
            _create_symlink_to(data_file, data_file.name)


def _get_data_files(data_file_lookup_by_lane_id, lane_id):
    # some lanes may legitimately have no data files
    return data_file_lookup_by_lane_id.get(lane_id, [])


def _create_symlink_to(path_to_file, symlink_name):
    logging.debug(f'Creating symlink "{symlink_name}" -> {path_to_file}.')
    if not Path(path_to_file).is_file():
        logging.error("data file {} does not exist".format(path_to_file))
    else:
        if Path(symlink_name).is_symlink():
            logging.debug("symlink {} already exists: not recreated".format(symlink_name))
        else:
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
    if Path(dir_name).is_dir():
        logging.debug(f"Directory {dir_name} already exists in {Path().absolute()}.")
    else:
        Path(dir_name).mkdir()
        logging.info(f"Directory {dir_name} was created at {Path().absolute()}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create sample data view")
    parser.add_argument("-D", "--data_dir", help="Data file directory")
    parser.add_argument("-O", "--output_dir", help="Institition view (output) file directory")
    parser.add_argument("-P", "--project", choices=["juno", "gps"], default="juno", help="Project")
    parser.add_argument(
        "-L",
        "--log_level",
        help="Logging level [default: WARNING]",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
    )
    options = parser.parse_args(argv[1:])

    project = options.project

    # adding `module` for log format allows us to filter out messages from SampleMetadata or squencing_status,
    # which can be handy
    logging.basicConfig(format="%(asctime)-15s %(levelname)s %(module)s:  %(message)s", level=options.log_level)

    logging.info("Getting sample metadata")
    sample_metadata = SampleMetadata()
    sample_metadata.current_project = project

    create_download_view_for_sample_data(
        project,
        sample_metadata,
        InstitutionData().get_all_institution_keys_regardless_of_user_membership(),
        options.data_dir,
        options.output_dir,
    )
