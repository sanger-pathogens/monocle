#!/usr/bin/env python3

import argparse
import sys
from sys import argv
import logging
import os
import os.path
import json
from datetime import datetime
from urllib.error import HTTPError
from pathlib import Path
import re

from dash.api.service.DataSources.sample_metadata        import SampleMetadata
from dash.api.service.DataSources.sequencing_status      import SequencingStatus

from lib._mkdir import _mkdir
from lib.qc_data import QCData

QC_DIR = 'monocle_pipeline_qc'


def get_lane_ids(db):
    """Get lane ids for each insitution"""

    lane_ids = []
    institutions = list(db.get_institution_names())

    for institution in institutions:
        sample_ids = [sample["sample_id"] for sample in db.get_samples(institutions=[institution])]

        logging.info(f'{institution}: {len(sample_ids)} sample ids')

        if not sample_ids:
            logging.warning(f'No sample ids found for {institution}')

        for sample_id in sample_ids:
            try:
                seq_data = _get_sequencing_status_data([sample_id])
                for sample in seq_data.keys():
                    for lane in seq_data[sample]['lanes']:
                        lane_ids.append(lane['id'])
            except HTTPError as e:
                logging.error('Failed to get sequence data for {} sample {}: {}'.format(institution, sample_id, repr(e)))

    return lane_ids


def update_relative_abundance(lane_id, kraken_data_dir, species, qc_data):
    """Update the QC data for a lane with the relative abundance of a species from the kraken report"""

    kraken_report = Path(f'{kraken_data_dir}/{lane_id}_kraken.report').absolute()

    # Get relative abundance for species
    if os.path.exists(kraken_report):
        rel_abnd = _get_relative_abundance(kraken_report, species)
        # Get lane id and create directory
        lane_id = os.path.basename(kraken_report).split('_kraken.report')[0]
        _mkdir(f'{QC_DIR}/{lane_id}')
        # Update QC data
        qc_info = {
            "species": species,
            "value": rel_abnd,
            "timestamp": str(datetime.now())}

        qc_data.update('rel_abundance', qc_info)

    else:
        logging.warning(f'No kraken report found for {lane_id}.')

    return qc_data


def _get_relative_abundance(kraken_report, species):
    """Get the relative abundance for a species from the kraken report"""

    file = open(kraken_report, "r")
    for line in file:
        if re.search(f'{species}$', line):
            rel_abnd = line.split('\t')[0].split(' ')[1]
            file.close()
            break

    return rel_abnd


def _get_sequencing_status_data(sample_ids):
    """Get the sequencing status of sample ids from the dash API"""

    return SequencingStatus().get_multiple_samples(sample_ids)


def get_arguments():
    parser = argparse.ArgumentParser(description='Get QC data')
    parser.add_argument("-D", "--kraken_data_dir", help="Data file directory for kraken report")
    parser.add_argument("-S", "--species", help="Species name e.g. 'Streptococcus agalactiae'")
    parser.add_argument("-L", "--log_level", help="Logging level [default: WARNING]", choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'], default='WARNING')

    return parser


def main():
    parser = get_arguments()
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)-15s %(levelname)s %(module)s:  %(message)s', level=args.log_level)

    sample_metadata = SampleMetadata()
    lane_ids = get_lane_ids(sample_metadata)

    # Update the QC data file for each line
    for lane_id in lane_ids:
        qc_data = update_relative_abundance(lane_id, args.kraken_data_dir, args.species, QCData(f'{QC_DIR}/{lane_id}/qc_data.json'))
        ## TODO: Get more QC data
        qc_data.write_file()


if __name__ == '__main__':
    sys.exit(main())
