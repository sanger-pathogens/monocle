#!/usr/bin/env python3

import argparse
import json
import logging
import os
import os.path
import re
import sys
from datetime import datetime
from pathlib import Path
from sys import argv
from urllib.error import HTTPError

from dash.api.service.DataSources.sample_metadata import SampleMetadata
from dash.api.service.DataSources.sequencing_status import SequencingStatus

from lib.qc_data import QCData

QC_DIR = "monocle_pipeline_qc"


def get_lane_ids(db):
    """Get lane ids for each insitution"""

    lane_ids = []
    institutions = list(db.get_institution_names())

    for institution in institutions:
        sanger_sample_ids = [sample["sanger_sample_id"] for sample in db.get_samples(institutions=[institution])]

        logging.info(f"{institution}: {len(sanger_sample_ids)} sample ids")

        if not sanger_sample_ids:
            # we expect institutions without samples => this could be noisy in a cron job => INFO
            logging.info(f"No sample ids found for {institution}")

        for sanger_sample_id in sanger_sample_ids:
            try:
                seq_data = _get_sequencing_status_data([sanger_sample_id])
                for sample in seq_data.keys():
                    for lane in seq_data[sample]["lanes"]:
                        lane_ids.append(lane["id"])
            except HTTPError as e:
                logging.error(
                    "Failed to get sequence data for {} sample {}: {}".format(institution, sanger_sample_id, repr(e))
                )

    return lane_ids


def update_relative_abundance(lane_id, kraken_data_dir, species, qc_data):
    """Update the QC data for a lane with the relative abundance of a species from the kraken report"""

    kraken_report = Path(f"{kraken_data_dir}/{lane_id}_kraken.report").absolute()

    # Get relative abundance for species
    if os.path.exists(kraken_report):
        rel_abnd = _get_relative_abundance(kraken_report, species)
        if rel_abnd is not None:
            # Update QC data
            qc_info = {"species": species, "value": rel_abnd, "timestamp": str(datetime.now())}
            qc_data.update("rel_abundance", qc_info)

    else:
        # we expect lanes without kraken reports => this could be noisy in a cron job => INFO
        logging.info(f"No kraken report found for {lane_id}.")

    return qc_data


def _get_relative_abundance(kraken_report, species):
    """Get the relative abundance for a species from the kraken report"""

    rel_abnd = None
    file = open(kraken_report, "r")
    for line in file:
        if re.search(f"{species}$", line):
            rel_abnd = line.split("\t")[0].lstrip().split(" ")[0]
            file.close()
            break

    if rel_abnd is None:
        logging.warning(f'Species "{species}" not found in kraken report{kraken_report}.')

    return rel_abnd


def _get_sequencing_status_data(sanger_sample_ids):
    """Get the sequencing status of sample ids from the dash API"""

    return SequencingStatus().get_multiple_samples(sanger_sample_ids)


def get_arguments():
    parser = argparse.ArgumentParser(description="Get QC data")
    default_monocle_data_path = os.path.join(os.environ.get("MONOCLE_DATA", "."), "kraken_report")
    default_log_level = "WARNING"
    parser.add_argument(
        "-D",
        "--kraken_data_dir",
        help="Data file directory for kraken report [default: {}]; can use MONOCLE_DATA environment variable to set parent directory".format(
            default_monocle_data_path
        ),
        default=default_monocle_data_path,
    )
    parser.add_argument(
        "-S", "--species", help="Species name, e.g. 'Streptococcus agalactiae' or 'Streptococcus pneumoniae'"
    )
    parser.add_argument(
        "-L",
        "--log_level",
        help="Logging level [default: {}]".format(default_log_level),
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=default_log_level,
    )

    return parser


def main():
    parser = get_arguments()
    args = parser.parse_args()

    logging.basicConfig(format="%(asctime)-15s %(levelname)s %(module)s:  %(message)s", level=args.log_level)

    sample_metadata = SampleMetadata()
    lane_ids = get_lane_ids(sample_metadata)

    # Update the QC data file for each line
    for lane_id in lane_ids:
        qc_data = update_relative_abundance(
            lane_id, args.kraken_data_dir, args.species, QCData(f"{QC_DIR}/{lane_id}/qc_data.json")
        )
        ## TODO: Get more QC data
        qc_data.write_file()


if __name__ == "__main__":
    sys.exit(main())
