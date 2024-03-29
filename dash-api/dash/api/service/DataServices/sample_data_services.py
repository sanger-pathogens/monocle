import logging
import urllib.error
import urllib.parse
import urllib.request
from copy import deepcopy
from csv import QUOTE_NONNUMERIC
from datetime import datetime
from functools import reduce
from math import ceil
from os import environ
from pathlib import Path
from uuid import uuid4

import DataServices.sample_tracking_services
import DataSources.metadata_download
import DataSources.sample_metadata
import pandas
import yaml
from utils.file import format_file_size

API_ERROR_KEY = "_ERROR"
DATA_INST_VIEW_ENVIRON = {"juno": "JUNO_DATA_INSTITUTION_VIEW", "gps": "GPS_DATA_INSTITUTION_VIEW"}
FIELD_NAME_SUBMITTING_INSTITUTION = "submitting_institution"
MIN_ZIP_NUM_SAMPLES_CAPACITY = 3
MIN_ZIP_NUM_SAMPLES_CAPACITY_WITH_READS = 1
READ_MODE = "r"
ZIP_COMPRESSION_FACTOR_ASSEMBLIES_ANNOTATIONS = 1
ZIP_SIZE_OVERESTIMATE_FACTOR = 1.11
ZIP_SIZE_OVERESTIMATE_FACTOR_WITH_READS = 1.15

ASSEMBLY_FILE_SUFFIX = {"juno": ".contigs_spades.fa", "gps": ".contigs_velvet.fa"}
ANNOTATION_FILE_SUFFIX = {"juno": ".spades.gff", "gps": ".velvet.gff"}
READS_FILE_SUFFIXES = ("_1.fastq.gz", "_2.fastq.gz")
UNKNOWN_PUBLIC_NAME = "unknown"


class DataSourceConfigError(Exception):
    pass


class MonocleSampleData:
    """
    Provides wrapper for classes that query various data sources for Monocle data.
    This class exists to convert data between the form in which they are provided by the data sources,
    and whatever form is most convenient for rendering the dashboard.
    """

    default_data_source_config = "data_sources.yml"

    # date from which progress is counted
    day_zero = datetime(2019, 9, 17)

    def __init__(
        self,
        data_source_config=default_data_source_config,
        MonocleSampleTracking_ref=None,
        set_up=True,
    ):
        self.user_record = None
        self.current_project = None
        self._institutions = None
        self.data_source_config = None
        # requite config files; can be passed, default to variables
        self.data_source_config_name = data_source_config
        if not Path(self.data_source_config_name).is_file():
            return self._download_config_error(
                "data source config file {} is missing".format(self.data_source_config_name)
            )

        # DataServices.sample_tracking_services.MonocleSampleTracking object can be passed
        # (otherwise assign None, indicating it is to be created later)
        self.sample_tracking = None
        if MonocleSampleTracking_ref is not None:
            self.sample_tracking = MonocleSampleTracking_ref

        # set_up flag causes data objects to be loaded on instantiation
        # only set to False if you know what you're doing
        if set_up:
            self.updated = datetime.now()
            self.metadata_download_source = DataSources.metadata_download.MetadataDownload()
            self.sample_metadata_source = DataSources.sample_metadata.SampleMetadata()

    def get_sample_tracking_service(self):
        """
        Returns instance of DataServices.sample_tracking_services.MonocleSampleTracking
        This must have the user_record and current_project attributes assigned,
        but that cannopt be done in __init__ as ServiceFactory only assigned this after
        MonocleSampleData objects are instantiated
        """
        if self.sample_tracking is None:
            self.sample_tracking = DataServices.sample_tracking_services.MonocleSampleTracking()
        self.sample_tracking.user_record = self.user_record
        self.sample_tracking.current_project = self.current_project
        return self.sample_tracking

    def get_metadata(
        self,
        sample_filters,
        start_row=None,
        num_rows=None,
        metadata_columns=None,
        in_silico_columns=None,
        qc_data_columns=None,
        include_in_silico=False,
        include_qc_data=False,
    ):
        """
        Pass sample filters dict (describes the filters applied in the front end)
        If pagination is wanted, pass the number of the starting row (first row is 1) *and* number of rows wanted;
        num_rows is ignored unless start_rows is defined. Passing start_row without num_rows is an error.
        Optionally pass lists of metadata_columns, qc_data_columns and in_silico_columns to specify which metadata,
        QC data and in silico (respectively) columns are returned.
        Optional flags:
        'include_qc_data' if QC data should be retrieved and merged into the metadata.
        'include_in_silico' if in silico data should be retrieved and merged into the metadata.

        Returns array of samples that match the filter(s); each sample is a dict containing the metadata
        and (if requested) in silico & QC data.  Metadata, in silico and QC data are represented with the same format:
        a dict of fields, where each dict value is a dict with the title, column position (order) and value
        for that field.
        [
           { metadata: { 'metadata_field_1' : {'title': 'field name', order: 1, value: 'the value'},
                         'metadata_field_2' : {'title': 'another field name', order: 2, value: 'another value'},
                          ...
                          },
            'qc data'   :{   'qc_data_field_1' : {'title': 'field name', order: 1, value: 'the value'},
                             'qc_data_field_2' : {'title': 'another field name', order: 2, value: 'another value'},
                          ...
                          }
           },
            'in silico' :{   'in_silico_field_1' : {'title': 'field name', order: 1, value: 'the value'},
                             'in_silico_field_2' : {'title': 'another field name', order: 2, value: 'another value'},
                          ...
                          },
           ...
        ]

        If no samples were found, returns None
        """

        # get_filtered_samples filters the samples for us, from the sequencing status data
        try:
            filtered_samples = self.get_filtered_samples(sample_filters, disable_public_name_fetch=True)
        # catch 404s -- this means the metadata API found no matching samples
        except urllib.error.HTTPError as e:
            if "404" not in str(e):
                raise e
            return None

        # be careful using total_num_matching_samples in following lines, as this is the complete
        # number of samples, but pagination params mean we may below be working with a smaller
        # (possibly empty) list of samples
        total_num_matching_samples = len(filtered_samples)
        logging.info(
            "{}.get_filtered_samples returned {} samples".format(__class__.__name__, total_num_matching_samples)
        )
        logging.debug("{}.get_filtered_samples returned {}".format(__class__.__name__, filtered_samples))
        # if paginating, take a slice of the samples
        if start_row is None:
            last_sample_row_returned = total_num_matching_samples
            logging.info('No "start row" passed: returning all {} matching samples'.format(total_num_matching_samples))
        else:
            assert num_rows is not None, "{} must be passed start_row and num_rows, or neither.".format(
                __class__.__name__
            )
            filtered_samples = list(filtered_samples[(start_row - 1) : ((start_row - 1) + num_rows)])
            logging.info(
                'Passed "start row"={} and "num rows"={}: returning slice with {} samples'.format(
                    start_row, num_rows, len(filtered_samples)
                )
            )
            # last_sample_row_returned must be the actual last row, which may be lower
            # than expected when the end of the result set is reached
            last_sample_row_returned = (start_row - 1) + len(filtered_samples)
        logging.info(
            "pagination (start {}, num {}) working with {} samples".format(start_row, num_rows, len(filtered_samples))
        )

        # if filters or pagination results in an empty samples list, return an empty response
        if 1 > len(filtered_samples):
            logging.info("no matching samples: {} is returning None".format(__class__.__name__))
            return None

        # the samples IDs can be used to get the sample metadata
        try:
            sanger_sample_id_list = [s["sanger_sample_id"] for s in filtered_samples]
        except KeyError:
            logging.error(
                "{}.get_filtered_samples returned one or more samples without a sample ID (expected 'sanger_sample_id' key)".format(
                    __class__.__name__
                )
            )
            raise
        logging.info(
            "sample filters {} resulted in {} samples being returned".format(sample_filters, len(sanger_sample_id_list))
        )
        metadata = self.metadata_download_source.get_metadata(self.current_project, sanger_sample_id_list)

        # combined_metadata is the structure to be returned
        combined_metadata = [{"metadata": m} for m in metadata]
        if include_qc_data:
            combined_metadata = self._merge_qc_data_into_combined_metadata(filtered_samples, combined_metadata)
        if include_in_silico:
            combined_metadata = self._merge_in_silico_data_into_combined_metadata(filtered_samples, combined_metadata)

        # filtering metadata columns is done last, because some columns are needed in the processes above
        if metadata_columns is not None or in_silico_columns is not None or qc_data_columns is not None:
            combined_metadata = self._filter_combined_metadata_columns(
                combined_metadata, metadata_columns, qc_data_columns, in_silico_columns
            )

        logging.info("{}.get_metadata returning {} samples".format(__class__.__name__, len(combined_metadata)))
        return {
            "samples": combined_metadata,
            "total rows": total_num_matching_samples,
            "last row": last_sample_row_returned,
        }

    def _merge_qc_data_into_combined_metadata(self, filtered_samples, combined_metadata):
        """
        Pass
        - filtered samples structure (as constructed by `get_filtered_samples()`)
        - combined metadata structure (of the type `get_metadata()` creates and returns) but which contains
        only a `metadata` key for each sample

        Retrieves QC data from the metadata API, and inserts it into the combined metadata structure

        Returns the combined metadata structure
        """
        # QC data must be retrieved using lane IDs
        lane_id_list = []
        # also need to track which lane(s) are associated with each sample
        sample_to_lanes_lookup = {}
        for this_sample in filtered_samples:
            sample_to_lanes_lookup[this_sample["sanger_sample_id"]] = []
            try:
                # remember, some samples may legitimately have no lanes
                for this_lane_id in this_sample["lanes"]:
                    if this_lane_id is not None:
                        lane_id_list.append(this_lane_id)
                        sample_to_lanes_lookup[this_sample["sanger_sample_id"]].append(this_lane_id)
            except KeyError:
                logging.error(
                    "{}.get_filtered_samples returned one or more samples without lanes data (expected 'lanes' key)".format(
                        __class__.__name__
                    )
                )
                raise
        qc_data = self.metadata_download_source.get_qc_data(self.current_project, lane_id_list)
        logging.debug("{}.metadata_download_source.get_qc_data returned {}".format(__class__.__name__, qc_data))
        lane_to_qc_data_lookup = {}
        for this_qc_data in qc_data:
            try:
                lane_to_qc_data_lookup[this_qc_data["lane_id"]["value"]] = this_qc_data
            except KeyError:
                logging.error(
                    "{}.metadata_download_source.get_qc_data returned an item with no lane ID (expected 'lane_id'/'value' keys)".format(
                        __class__.__name__
                    )
                )
                raise

        for combined_metadata_item in combined_metadata:
            this_sanger_sample_id = combined_metadata_item["metadata"]["sanger_sample_id"]["value"]
            # now get QC data for this sample's lane(s)
            # some samples may legitimately have no lanes
            multiple_qc_data_lanes = False
            for this_lane_id in sample_to_lanes_lookup.get(this_sanger_sample_id, []):
                # some lanes may legitimately have no QC data
                this_lane_qc_data = lane_to_qc_data_lookup.get(this_lane_id, None)
                if this_lane_qc_data is not None:
                    if "qc data" in combined_metadata_item:
                        multiple_qc_data_lanes = True
                    else:
                        combined_metadata_item["qc data"] = this_lane_qc_data
            if multiple_qc_data_lanes:
                logging.warning(
                    "sample {} has more than one lane with QC data, which is not supported: no QC data will be provided for this sample".format(
                        this_sanger_sample_id
                    )
                )
                combined_metadata_item.pop("qc data")

        return combined_metadata

    def _merge_in_silico_data_into_combined_metadata(self, filtered_samples, combined_metadata):
        """
        Pass
        - filtered samples structure (as constructed by `get_filtered_samples()`)
        - combined metadata structure (of the type `get_metadata()` creates and returns) but which contains
        only a `metadata` key for each sample

        Retrieves _in silico_ data from the metadata API, and inserts it into the combined metadata structure

        Returns the combined metadata structure
        """
        # in silco data must be retrieved using lane IDs
        lane_id_list = []
        # also need to track which lane(s) are associated with each sample
        sample_to_lanes_lookup = {}
        for this_sample in filtered_samples:
            sample_to_lanes_lookup[this_sample["sanger_sample_id"]] = []
            try:
                # remember, some samples may legitimately have no lanes
                for this_lane_id in this_sample["lanes"]:
                    if this_lane_id is not None:
                        lane_id_list.append(this_lane_id)
                        sample_to_lanes_lookup[this_sample["sanger_sample_id"]].append(this_lane_id)
            except KeyError:
                logging.error(
                    "{}.get_filtered_samples returned one or more samples without lanes data (expected 'lanes' key)".format(
                        __class__.__name__
                    )
                )
                raise
        in_silico_data = self.metadata_download_source.get_in_silico_data(self.current_project, lane_id_list)
        logging.debug(
            "{}.metadata_download_source.get_in_silico_data returned {}".format(__class__.__name__, in_silico_data)
        )
        lane_to_in_silico_lookup = {}
        for this_in_silico_data in in_silico_data:
            try:
                lane_to_in_silico_lookup[this_in_silico_data["lane_id"]["value"]] = this_in_silico_data
            except KeyError:
                logging.error(
                    "{}.metadata_download_source.get_in_silico_data returned an item with no lane ID (expected 'lane_id'/'value' keys)".format(
                        __class__.__name__
                    )
                )
                raise

        for combined_metadata_item in combined_metadata:
            this_sanger_sample_id = combined_metadata_item["metadata"]["sanger_sample_id"]["value"]
            # now get in silico data for this sample's lane(s)
            # some samples may legitimately have no lanes
            multiple_in_silico_lanes = False
            for this_lane_id in sample_to_lanes_lookup.get(this_sanger_sample_id, []):
                # some lanes may legitimately have no in silico data
                this_lane_in_silico_data = lane_to_in_silico_lookup.get(this_lane_id, None)
                if this_lane_in_silico_data is not None:
                    if "in silico" in combined_metadata_item:
                        multiple_in_silico_lanes = True
                    else:
                        combined_metadata_item["in silico"] = this_lane_in_silico_data
            if multiple_in_silico_lanes:
                logging.warning(
                    "sample {} has more than one lane with in silico data, which is not supported: no in silico data will be provided for this sample".format(
                        this_sanger_sample_id
                    )
                )
                combined_metadata_item.pop("in silico")
        return combined_metadata

    def _filter_combined_metadata_columns(
        self, combined_metadata, metadata_columns, qc_data_columns, in_silico_columns
    ):
        """
        Pass
        - combined metadata structure (of the type `get_metadata()` creates and returns)
        - a list of metadata columns
        - a list of QC data columns
        - a list of in silico data columns
        All columns that are _not_ in the column lists will be removed from the combined metadata.
        (Pass `None` in place of a list if metadata and/or in silico columns should *not* be filtered).

        Returns the (probably modified) combined metadata structure
        """
        for this_sample in combined_metadata:
            if metadata_columns is not None:
                metadata = this_sample["metadata"]
                for this_column in list(metadata):
                    if this_column not in metadata_columns:
                        logging.debug("removing unwanted metadata column {}".format(this_column))
                        del metadata[this_column]
            # some samples will legitimately have no in silico data
            if in_silico_columns is not None and "in silico" in this_sample:
                in_silico = this_sample["in silico"]
                for this_column in list(in_silico):
                    if this_column not in in_silico_columns:
                        del in_silico[this_column]
            # some samples will legitimately have no QC data
            if qc_data_columns is not None and "qc data" in this_sample:
                qc_data = this_sample["qc data"]
                for this_column in list(qc_data):
                    if this_column not in qc_data_columns:
                        del qc_data[this_column]
        return combined_metadata

    def get_bulk_download_info(self, sample_filters, **kwargs):
        """
        Pass sample filters dict (describes the filters applied in the front end)
        and an optional boolean flag per assembly, annotation, and reads types of lane files.
        Returns a dict w/ a summary for an expected sample bulk download.
        {
           num_samples: <int>,
           size: <str>,
           size_zipped: <str>
        }
        If no samples were found, returns None
        """
        try:
            filtered_samples = self.get_filtered_samples(sample_filters)
        # catch 404s -- this means the metadata API found no matching samples
        except urllib.error.HTTPError as e:
            if "404" not in str(e):
                raise e
            return None

        max_samples = self.get_bulk_download_max_samples_per_download()
        num_samples_restricted_to = None
        if len(filtered_samples) > max_samples:
            logging.warning(
                "bulk download requested for {} samples, will be restricted to {}".format(
                    len(filtered_samples), max_samples
                )
            )
            filtered_samples = filtered_samples[0:max_samples]
            num_samples_restricted_to = max_samples

        include_reads = kwargs.get("reads", False)
        public_name_to_lane_files = self.get_public_name_to_lane_files_dict(
            filtered_samples,
            assemblies=kwargs.get("assemblies", False),
            annotations=kwargs.get("annotations", False),
            reads=kwargs.get("reads", False),
        )
        total_lane_files_size = 0
        for lane_files in public_name_to_lane_files.values():
            lane_files_size = reduce(lambda accum, fl: accum + self._get_file_size(fl), lane_files, 0)
            total_lane_files_size = total_lane_files_size + lane_files_size

        num_samples = len(filtered_samples)
        total_lane_files_size_zipped = total_lane_files_size / ZIP_COMPRESSION_FACTOR_ASSEMBLIES_ANNOTATIONS
        return {
            "num_samples": num_samples,
            "size": format_file_size(total_lane_files_size),
            "size_zipped": format_file_size(total_lane_files_size_zipped),
            "size_per_zip_options": self._calculate_zip_size_options(
                num_samples, total_lane_files_size_zipped, include_reads
            ),
            "num_samples_restricted_to": num_samples_restricted_to,
        }

    def get_filtered_samples(self, sample_filters, disable_public_name_fetch=False):
        """
        Pass sample filters dict (describes the filters applied in the front end)
        Optionally pass `disable_public_name_fetch` (default: false) to stop public names being retrieved
        from metadata API (will be slightly quicker, so use this if you don't need public names)

        Returns a list of matching samples' sequencing status data w/ institution keys and (unless
        disable_public_name_fetch was passed) public names added.

        Supports `batches` filter:
           "batches": [{"institution key": "MinHeaCenLab", "batch date": "2019-11-15"}, ... ]

        Also filters based on sequencing/pipeline status, e.g.
           "sequencing": {"success": True}

        Return format:

        [  {  'lanes':             ['32820_2#287'],
              'creation_datetime': '2019-11-15T13:56:07Z',
              'sanger_sample_id':  '5903STDY8113167',
              'inst_key':          'MinHeaCenLab',
              'public_name':       'JN_IL_ST00002'
              }
           ]

        """
        inst_key_batch_date_pairs = sample_filters["batches"]
        if len(inst_key_batch_date_pairs) == 0:
            logging.debug(
                f'{__class__.__name__}.get_filtered_samples(): The list of batches ({"institution key", "batch date"} dicts) is empty.'
            )
            return []

        institution_keys = [
            inst_key_batch_date_pair["institution key"] for inst_key_batch_date_pair in inst_key_batch_date_pairs
        ]
        if not disable_public_name_fetch:
            sanger_sample_id_to_public_name = self._get_sanger_sample_id_to_public_name_dict(institution_keys)
        filtered_samples = []
        sequencing_status_data = deepcopy(self.get_sample_tracking_service().get_sequencing_status())
        # lane_data is a temporary store of lane data that are needed for filters
        # (we don't want all of the lane data permanetly stored in filtered_samples)
        lane_data = {}
        for this_inst_key_batch_date_pair in inst_key_batch_date_pairs:
            inst_key = this_inst_key_batch_date_pair["institution key"]
            batch_date_stamp = this_inst_key_batch_date_pair["batch date"]
            try:
                samples = [
                    (sanger_sample_id, sample)
                    for sanger_sample_id, sample in sequencing_status_data[inst_key].items()
                    if sample
                ]
            except KeyError:
                logging.warning(f'No key "{inst_key}" in sequencing status data.')
                continue
            for sanger_sample_id, sample in samples:
                if (
                    self.get_sample_tracking_service().convert_mlwh_datetime_stamp_to_date_stamp(
                        sample["creation_datetime"]
                    )
                    == batch_date_stamp
                ):
                    lane_data[sanger_sample_id] = sample.get("lanes", [])
                    # `sample` contains all sequencing status data (because it was copy from the dict returned by
                    # get_sequencing_status()) but we only want a subset, so strip it down to what's needed:
                    for this_key in list(sample):
                        if "lanes" == this_key:
                            sample[this_key] = [lane["id"] for lane in sample[this_key]]
                        elif this_key not in ["creation_datetime", "inst_key", "public_name", "sanger_sample_id"]:
                            del sample[this_key]
                    # sample ID is the key in sequencing_status_data, so was not included in the dict, but it is useful to
                    # add it as otherwise functions that call get_filtered_samples() wouldn't have access to the sample ID
                    sample["sanger_sample_id"] = sanger_sample_id
                    sample["inst_key"] = inst_key
                    if not disable_public_name_fetch:
                        sample["public_name"] = sanger_sample_id_to_public_name[sanger_sample_id]
                    filtered_samples.append(sample)
        logging.info("batch from {} on {}:  found {} samples".format(inst_key, batch_date_stamp, len(filtered_samples)))

        # if filters based on sequencing or pipeline status were passed, filter the results
        if "sequencing" in sample_filters:
            filtered_samples = self._apply_sequencing_filters(filtered_samples, sample_filters["sequencing"], lane_data)
        if "pipeline" in sample_filters:
            filtered_samples = self._apply_pipeline_filters(filtered_samples, sample_filters["pipeline"], lane_data)

        logging.info("fully filtered sample list contains {} samples".format(len(filtered_samples)))
        return filtered_samples

    def _apply_sequencing_filters(self, filtered_samples, sequencing_filters, lane_data):
        logging.info(
            "{}._apply_sequencing_filters filtering initial list of {} samples".format(
                __class__.__name__, len(filtered_samples)
            )
        )
        failed_samples = []
        for this_sample in filtered_samples:
            this_sample_id = this_sample["sanger_sample_id"]
            at_least_one_lane_passes_sequencing_filters = False
            for this_lane in lane_data[this_sample_id]:
                (
                    this_lane_complete,
                    this_lane_success,
                    discard_this,
                ) = self.get_sample_tracking_service().get_sequencing_outcome_for_lane(this_sample_id, this_lane)
                this_lane_passes_sequencing_filters = True
                if "complete" in sequencing_filters:
                    if not sequencing_filters["complete"] == this_lane_complete:
                        this_lane_passes_sequencing_filters = False
                if "success" in sequencing_filters:
                    if not sequencing_filters["success"] == this_lane_success:
                        this_lane_passes_sequencing_filters = False
                if this_lane_passes_sequencing_filters:
                    at_least_one_lane_passes_sequencing_filters = True
                    break
            if not at_least_one_lane_passes_sequencing_filters:
                logging.debug("sample {} FAILS filter {}".format(this_sample_id, sequencing_filters))
                failed_samples.append(this_sample_id)

            # remove failed samples from filtered_samples
            filtered_samples = list(filter(lambda s: s["sanger_sample_id"] not in failed_samples, filtered_samples))
        return filtered_samples

    def _apply_pipeline_filters(self, filtered_samples, pipeline_filters, lane_data):
        logging.info(
            "{}._apply_pipeline_filters filtering initial list of {} samples".format(
                __class__.__name__, len(filtered_samples)
            )
        )
        failed_samples = []
        for this_sample in filtered_samples:
            this_sample_id = this_sample["sanger_sample_id"]
            at_least_one_lane_passes_pipeline_filters = False
            for this_lane in lane_data[this_sample_id]:
                this_lane_complete, this_lane_success = self._get_pipeline_outcome_for_lane(this_lane["id"])
                this_lane_passes_pipeline_filters = True
                if "complete" in pipeline_filters:
                    if not pipeline_filters["complete"] == this_lane_complete:
                        this_lane_passes_pipeline_filters = False
                if "success" in pipeline_filters:
                    if not pipeline_filters["success"] == this_lane_success:
                        this_lane_passes_pipeline_filters = False
                if this_lane_passes_pipeline_filters:
                    at_least_one_lane_passes_pipeline_filters = True
                    break
            if not at_least_one_lane_passes_pipeline_filters:
                logging.debug("sample {} FAILS filter {}".format(this_sample_id, pipeline_filters))
                failed_samples.append(this_sample_id)

            # remove failed samples from filtered_samples
            filtered_samples = list(filter(lambda s: s["sanger_sample_id"] not in failed_samples, filtered_samples))
        return filtered_samples

    # sequencing status for a lane is provided by sample_tracking_services.MonocleSampleTracking.get_sequencing_outcome_for_lane()
    # but there is no exact equivalent for pipelines, that has a different method of collecting status data via
    # pipeline_status.PipelineStatus
    # this method provides a similar function to get_sequencing_outcome_for_lane(), for pipelines
    def _get_pipeline_outcome_for_lane(self, lane_id):
        this_lane_complete = False
        this_lane_success = False
        this_lane_pipeline_status = self.get_sample_tracking_service().get_pipeline_status().lane_status(lane_id)
        # keys FAILED and SUCCESS are always defined
        # they are both False if we have no status for the lane (i.e. pending in the pipeline)
        if this_lane_pipeline_status["FAILED"] or this_lane_pipeline_status["SUCCESS"]:
            this_lane_complete = True
        if this_lane_pipeline_status["SUCCESS"]:
            this_lane_success = True
        return (this_lane_complete, this_lane_success)

    def _get_sanger_sample_id_to_public_name_dict(self, institution_keys):
        sanger_sample_id_to_public_name = {}
        for sample in self.get_sample_tracking_service().sample_metadata.get_samples(
            self.current_project, institution_keys=institution_keys
        ):
            sanger_sample_id = sample["sanger_sample_id"]
            try:
                public_name = sample["public_name"]
            except KeyError:
                logging.error(f"No public name for sample {sanger_sample_id}")
                sanger_sample_id_to_public_name[sanger_sample_id] = UNKNOWN_PUBLIC_NAME
            else:
                sanger_sample_id_to_public_name[sanger_sample_id] = public_name
        return sanger_sample_id_to_public_name

    def _calculate_zip_size_options(self, num_samples, total_zip_size, include_reads):
        max_samples_per_zip = min(
            self.get_bulk_download_max_samples_per_zip(including_reads=include_reads), num_samples
        )
        if 1 == num_samples:
            return [
                {
                    "max_samples_per_zip": 1,
                    "size_per_zip": format_file_size(total_zip_size),
                }
            ]
        sample_size = total_zip_size / num_samples
        zip_size = sample_size * max_samples_per_zip
        min_zip_num_samples_capacity, zip_size_overestimate_factor = (
            (MIN_ZIP_NUM_SAMPLES_CAPACITY_WITH_READS, ZIP_SIZE_OVERESTIMATE_FACTOR_WITH_READS)
            if include_reads
            else (MIN_ZIP_NUM_SAMPLES_CAPACITY, ZIP_SIZE_OVERESTIMATE_FACTOR)
        )
        min_zip_size = sample_size * min_zip_num_samples_capacity
        factor = 4
        zip_size_options = []
        first_iteration = True
        while zip_size >= min_zip_size and max_samples_per_zip >= min_zip_num_samples_capacity:
            zip_size_with_weight = zip_size * zip_size_overestimate_factor
            if first_iteration:
                num_zips = ceil(num_samples / max_samples_per_zip)
                # Avoid "overestimating" the size per ZIP when there is only one ZIP, as in that case
                # the size is simply `total_zip_size`.
                if num_zips == 1:
                    zip_size_with_weight = total_zip_size
            zip_size_options.append(
                {
                    "max_samples_per_zip": max_samples_per_zip,
                    "size_per_zip": format_file_size(zip_size_with_weight),
                }
            )
            # without this condition, if loop continues iterating if max_samples_per_zip is reduced to 1
            if 1 == max_samples_per_zip:
                break
            max_samples_per_zip = ceil(max_samples_per_zip / factor)
            zip_size = zip_size / factor
            factor = factor * 1.2
            first_iteration = False
        return zip_size_options

    def get_public_name_to_lane_files_dict(self, samples, **kwargs):
        """
        Pass a list of samples and an optional boolean flag per assembly, annotation, and reads types of lane files.
        Returns a dict of public names to lane files corresponding to the parameters.

        {
           <public name 1>: [<lane files>],
           <public name 2>: ...
        }
        """
        data_inst_view_environ = DATA_INST_VIEW_ENVIRON[self.current_project]
        try:
            data_inst_view_path = environ[data_inst_view_environ]
        except KeyError:
            self._download_config_error(f"environment variable {data_inst_view_environ} is not set")

        public_name_to_lane_files = {}
        assemblies = kwargs.get("assemblies", False)
        annotations = kwargs.get("annotations", False)
        reads = kwargs.get("reads", False)

        for sample in samples:
            if not sample:
                continue
            public_name = sample["public_name"]
            institution_key = sample["inst_key"]
            for lane_id in sample["lanes"]:
                lane_file_names = self._get_lane_file_names(
                    lane_id, assemblies=assemblies, annotations=annotations, reads=reads
                )
                for lane_file_name in lane_file_names:
                    lane_file = Path(data_inst_view_path, institution_key, public_name, lane_file_name)
                    if not lane_file.exists():
                        logging.debug(f"File {lane_file} doesn't exist")
                        continue
                    if public_name not in public_name_to_lane_files:
                        public_name_to_lane_files[public_name] = []
                    public_name_to_lane_files[public_name].append(lane_file)

        return public_name_to_lane_files

    def _get_lane_file_names(self, lane_id, **kwargs):
        lane_file_names = []
        if kwargs.get("assemblies"):
            lane_file_names.append(f"{lane_id}{ASSEMBLY_FILE_SUFFIX[self.current_project]}")
        if kwargs.get("annotations"):
            lane_file_names.append(f"{lane_id}{ANNOTATION_FILE_SUFFIX[self.current_project]}")
        if kwargs.get("reads"):
            for file_suffix in READS_FILE_SUFFIXES:
                lane_file_names.append(f"{lane_id}{file_suffix}")
        return lane_file_names

    def get_bulk_download_location(self):
        data_source_config = self._get_data_source_config()
        data_inst_view_environ = DATA_INST_VIEW_ENVIRON[self.current_project]
        if data_inst_view_environ not in environ:
            return self._download_config_error("environment variable {} is not set".format(data_inst_view_environ))
        try:
            cross_institution_dir = data_source_config["data_download"]["cross_institution_dir"]
            return Path(environ[data_inst_view_environ], cross_institution_dir)
        except KeyError as err:
            self._download_config_error(err)

    def get_bulk_download_route(self):
        data_source_config = self._get_data_source_config()
        try:
            return data_source_config["data_download"]["download_route"]
        except KeyError as err:
            self._download_config_error(err)

    def get_bulk_download_max_samples_per_download(self):
        data_source_config = self._get_data_source_config()
        try:
            max_samples_per_download = int(data_source_config["data_download"]["max_samples_per_download"])
        except (KeyError, ValueError) as err:
            self._download_config_error(err)
        if not max_samples_per_download > 0:
            self._download_config_error(
                'data source config data_download.max_samples_per_download must be a positive integer, not "{}"'.format(
                    max_samples_per_download
                )
            )
        return max_samples_per_download

    def get_bulk_download_max_samples_per_zip(self, including_reads=False):
        data_source_config = self._get_data_source_config()
        try:
            max_samples_per_zip = (
                int(data_source_config["data_download"]["max_samples_per_zip_with_reads"])
                if including_reads
                else int(data_source_config["data_download"]["max_samples_per_zip"])
            )
        except (KeyError, ValueError) as err:
            self._download_config_error(err)
        if not max_samples_per_zip > 0:
            self._download_config_error(
                'data source config data_download.max_samples_per_zip must be a positive integer, not "{}"'.format(
                    max_samples_per_zip
                )
            )
        return max_samples_per_zip

    def get_metadata_for_download(self, download_hostname, institution_key, category, status):
        """
        This acts as a wrapper for get_csv_download().

        get_metadata_for_download() was the original implementation when metadata were only available
        for download via the dashboard, selected according to whether sequencing of pipelines had succeeded or failed;
        so the input parameters are simpler than get_csv_download().

        It is useful to retain this wrapper as it supports the existing routes that (because params are simple)
        conveniently accept GET requests.

        Pass host name (used for download links), institution key, category ('sequencing' or 'pipeline')
        and status ('successful' or 'failed').  These are translated into the parameters required by
        get_csv_download().

        Returns the return value(s) of get_csv_download().
        """
        # validate params
        institution_data = self.get_sample_tracking_service().get_institutions()
        categories = ["sequencing", "pipeline"]
        statuses = ["successful", "failed"]
        if institution_key not in institution_data:
            message = 'institution "{}" passed, but should be one of "{}"'.format(
                institution_key, '", "'.join(institution_data)
            )
            logging.error("Invalid request to {}: {}".format(__class__.__name__, message))
            return {"success": False, "error": "request", "message": message}
        if category not in categories:
            message = 'Invalid request to {}: category "{}" passed, but should be one of "{}"'.format(
                __class__.__name__, category, '", "'.join(categories)
            )
            logging.error(message)
            raise RuntimeError(message)
        if status not in statuses:
            message = 'Invalid request to {}: status "{}" passed, but should be one of "{}"'.format(
                __class__.__name__, status, '", "'.join(statuses)
            )
            logging.error(message)
            raise RuntimeError(message)

        # Create a sample filter that includes all batches for this institution
        batches_filter = []
        # get all batches for the institution
        batches_data = self.get_sample_tracking_service().get_batches().get(institution_key)
        for this_delivery in batches_data["deliveries"]:
            batches_filter.append({"institution key": institution_key, "batch date": this_delivery["date"]})
        # request should never have been made for an institution with no samples
        if 0 == len(batches_filter):
            message = "no batches could be found for {}".format(institution_key)
            logging.error(message)
            raise RuntimeError(message)

        # Create a sample filter for the sequencing/pipeline status required
        # This always restricts samples to those that have completed
        status_filter = {"complete": True}
        if "successful" == status:
            status_filter["success"] = True
        else:
            status_filter["success"] = False

        sample_filters = {"batches": batches_filter, category: status_filter}
        logging.info(
            "metadata download {}/{}/{} will use sample filters: {}".format(
                institution_key, category, status, sample_filters
            )
        )

        filename = "{}_{}_{}.csv".format(institution_key, category, status)
        download_links = {"hostname": download_hostname, "institution_key": institution_key}
        # wrap get_csv_download()
        return self.get_csv_download(filename, sample_filters, download_links=download_links)

    def get_csv_download(self, csv_response_filename, sample_filters, download_links=None):
        """
        Retrieves metadata and (when available) in silico data as CSV for a set of samples.

        Pass the suggested filename (ultimately for HTTP headers) and sample filters (as understood
        by get_filtered_samples(), to indicate the samples to be downloaded).

        Optionally pass `download_links` if data download links are to be included in the CSV:
        this is a dict with 'hostname', the host name to be used in the URLs, and 'institution',
        the institution that "owns" the data.

        *Important:*  Currently download links can only be provided where all the samples are
        from a single institution.  If `sample_filters` matches samples from more than one
        institution, some of the download links will be broken!

        On success, returns content for response, with suggested filename

        {  'success'   : True,
           'filename'  : 'the-institution-name_the-category_the-status.csv',
           'content'   : 'a,very,long,multi-line,CSV,string'
           }

        On failure, returns reasons ('not found', 'request' or 'internal'; could extend in future if required??)
        that can be used to provide suitable HTTP status.  Optionally can include a message with details.

        {  'success'   : False,
           'error'     : 'not found',
           'message'   : 'No matching samples were found.'
           }

        """
        download_base_url = None
        if download_links is not None:
            try:
                institution_key = download_links["institution_key"]
                hostname = download_links["hostname"]
            except KeyError:
                logging.error(
                    "{} parameter download_links must provide 'institution_key' and 'hostname'".format(
                        __class__.__name__
                    )
                )
                raise
            institution_download_symlink_url_path = self.make_download_symlink(institution_key)
            if institution_download_symlink_url_path is None:
                logging.error("Failed to create a symlink for data downloads.")
                return {
                    "success": False,
                    "error": "internal",
                }
            host_url = "https://{}".format(hostname)
            # TODO add correct port number
            # not critical as it will always be default (80/443) in production, and default port is available on all current dev instances
            # port should be available as request.headers['X-Forwarded-Port'] but that header isn't present (NGINX proxy config error?)
            download_base_url = "/".join([host_url, institution_download_symlink_url_path])
            logging.info("Data download base URL = {}".format(download_base_url))

        csv_response_string = self._metadata_as_csv(sample_filters, download_base_url=download_base_url)

        if csv_response_string is None:
            return {"success": False, "error": "not found", "message": "No matching samples were found."}
        return {"success": True, "filename": csv_response_filename, "content": csv_response_string}

    def _metadata_as_csv(self, sample_filters, download_base_url=None):
        """
        Wrapper for _metadata_as_df() which passes its return values to _metadata_df_to_csv(),
        and returns the CSV.
        Returns None if there are no matching samples.
        """
        metadata_df, column_order = self._metadata_as_df(sample_filters, download_base_url=download_base_url)
        if metadata_df is None:
            return None
        return self._metadata_df_to_csv(metadata_df, column_order)

    def _metadata_as_df(self, sample_filters, download_base_url=None):
        """
        Pass sample filters (as understood by get_filtered_samples() to indicate the samples to
        be downloaded.

        Optionally pass a base URL for the download; if provided, a download URL for each sample
        (this base URL with the public name appended) will be added as an extra column.

        When available, in silico data for each sample are included.

        The config file states if QC data, when available, should be included.

        Returns pandas data frame and column order; or None if there are no matching samples
        """
        # for metadata downloads, we just need a dict with sample IDs as keys,
        # value are arrays of lane ID(s) for each sample
        samples_for_download = {}
        # get_filtered_samples returns sequencing status data for the samples that match the sample filters used
        try:
            filtered_samples = self.get_filtered_samples(sample_filters, disable_public_name_fetch=True)
            # extract what we need from seq status data
            for this_sample in filtered_samples:
                this_sanger_sample_id = this_sample["sanger_sample_id"]
                for this_lane in this_sample["lanes"]:
                    if this_sanger_sample_id in samples_for_download:
                        samples_for_download[this_sanger_sample_id].append(this_lane)
                    else:
                        samples_for_download[this_sanger_sample_id] = [this_lane]

        # catch 404s -- this means the metadata API found no matching samples
        except urllib.error.HTTPError as e:
            if "404" not in str(e):
                raise e

        if 1 > len(samples_for_download):
            return (None, None)

        # retrieve the sample metadata and load into DataFrame
        logging.debug("Requesting metadata for samples: {}".format(samples_for_download))
        metadata, metadata_col_order = self._metadata_download_to_pandas_data(
            self.metadata_download_source.get_metadata(self.current_project, list(samples_for_download))
        )
        metadata_df = pandas.DataFrame(metadata)

        # we need to get the names of various fields with sample identifiers used
        # to colelct and merge metadta, in silico data and QC data for the download
        (
            sanger_sample_id_field,
            public_name_field,
            metadata_merge_field,
            in_silico_merge_field,
            qc_data_merge_field,
        ) = self._get_download_id_and_merge_fields()

        # IMPORTANT
        # the metadata returned from the metadata API will (probably) contain lane IDs, for historical reasons:  THESE MUST BE IGNORED
        # instead we use the lane IDs that MLWH told us are associated with each sample, as stored in the samples_for_download dict (just above)
        # it is possible, but rarely (perhaps never in practice) happens, that a sample may have multiple lane IDs;
        # in this case they are all put into the lane ID cell
        logging.info(
            "REMINDER: the lane IDs returned by the metadata API are ignored, and the lanes IDs provided by MLWH for each sample are provided in the metadata download!"
        )
        metadata_df = metadata_df.assign(
            Lane_ID=[
                " ".join(samples_for_download[this_sanger_sample_id])
                for this_sanger_sample_id in metadata_df[sanger_sample_id_field].tolist()
            ]
        )

        # if required, add download links to metadata DataFrame
        if download_base_url is not None:
            metadata_df = metadata_df.assign(
                Download_Link=[
                    "/".join([download_base_url, urllib.parse.quote(pn)])
                    for pn in metadata_df[public_name_field].tolist()
                ]
            )
            logging.info("metadata plus download links DataFrame.head:\n{}".format(metadata_df.head()))

        # if there are any in silico data, these are merged into the metadata DataFrame
        lanes_for_download = []
        for this_sample in samples_for_download:
            lanes_for_download.extend(samples_for_download[this_sample])

        # this flag indicates if QC data should be included in the CSV download
        # it is set in the configuration file, separately for each project
        include_qc_data = self._get_merge_qc_data_flag()
        if include_qc_data:
            # if there are any QC data, these are merged into the metadata DataFrame
            logging.debug("Requesting QC data for lanes: {}".format(lanes_for_download))
            qc_data, qc_data_col_order = self._metadata_download_to_pandas_data(
                self.metadata_download_source.get_qc_data(self.current_project, lanes_for_download)
            )
            if len(qc_data) > 0:
                logging.info(
                    "merging using metadata field {} and QC data field {}".format(
                        metadata_merge_field, qc_data_merge_field
                    )
                )
                qc_data_df = pandas.DataFrame(qc_data)
                for this_qc_data_column in qc_data_df:
                    if this_qc_data_column != qc_data_merge_field and this_qc_data_column in metadata_df:
                        qc_data_df.pop(this_qc_data_column)
                        logging.debug(
                            "QC column {} will not be included in merged data because it already exists in the metadata".format(
                                this_qc_data_column
                            )
                        )

                logging.debug("QC data DataFrame.head:\n{}".format(qc_data_df.head()))
                # merge with left join on Lane ID: incl. all metadata rows, only QC data rows where they match a metadata row
                # validate to ensure lane ID is unique in both dataframes
                metadata_df = metadata_df.merge(
                    qc_data_df,
                    left_on=metadata_merge_field,
                    right_on=qc_data_merge_field,
                    how="left",
                    validate="one_to_one",
                )
                del qc_data_df
                # add QC data columns to the list
                metadata_col_order = metadata_col_order + qc_data_col_order
            else:
                logging.info("There are no QC data to be merged")

        logging.debug("Requesting in silico data for lanes: {}".format(lanes_for_download))
        in_silico_data, in_silico_data_col_order = self._metadata_download_to_pandas_data(
            self.metadata_download_source.get_in_silico_data(self.current_project, lanes_for_download)
        )
        if len(in_silico_data) > 0:
            logging.info(
                "merging using metadata field {} and in silico data field {}".format(
                    metadata_merge_field, in_silico_merge_field
                )
            )
            in_silico_data_df = pandas.DataFrame(in_silico_data)

            for this_in_silico_column in in_silico_data_df:
                if this_in_silico_column != in_silico_merge_field and this_in_silico_column in metadata_df:
                    in_silico_data_df.pop(this_in_silico_column)
                    logging.debug(
                        "In silico column {} will not be included in merged data because it already exists in the metadata".format(
                            this_in_silico_column
                        )
                    )

            logging.debug("in silico data DataFrame.head:\n{}".format(in_silico_data_df.head()))
            # merge with left join on LaneID: incl. all metadata rows, only in silico rows where they match a metadata row
            # validate to ensure lane ID is unique in both dataframes
            metadata_df = metadata_df.merge(
                in_silico_data_df,
                left_on=metadata_merge_field,
                right_on=in_silico_merge_field,
                how="left",
                validate="one_to_one",
            )
            del in_silico_data_df
            # add silico data columns to the list
            metadata_col_order = metadata_col_order + in_silico_data_col_order

        # list of columns in `metadata_col_order` defines the CSV output
        # remove the fields used for merging the QC and in silico data into the metadata
        # (because these are duplicated in the metadata)
        while in_silico_merge_field in metadata_col_order:
            metadata_col_order.remove(in_silico_merge_field)
        while qc_data_merge_field in metadata_col_order:
            metadata_col_order.remove(qc_data_merge_field)
        # removing the merge fields from QC and in silico data may have removed the
        # field from the metadta, if it has the same field name in both; so
        # check and reinsert if required
        if metadata_merge_field not in metadata_col_order:
            metadata_col_order.insert(2, metadata_merge_field)
        # move public name to first column
        while public_name_field in metadata_col_order:
            metadata_col_order.remove(public_name_field)
        metadata_col_order.insert(0, public_name_field)
        # if download links are included, put them in last column
        if download_base_url is not None:
            metadata_col_order.append("Download_Link")

        return (metadata_df, metadata_col_order)

    def _get_download_id_and_merge_fields(self):
        data_source_config = self._get_data_source_config()
        project_specific_sections = {"juno": "metadata_download_juno", "gps": "metadata_download_gps"}
        section_wanted = project_specific_sections[self.current_project]
        try:
            sanger_sample_id_field = data_source_config[section_wanted]["sanger_sample_id_field"]
            public_name_field = data_source_config[section_wanted]["public_name_field"]
            metadata_merge_field = data_source_config[section_wanted]["metadata_merge_field"]
            in_silico_merge_field = data_source_config[section_wanted]["in_silico_merge_field"]
            qc_data_merge_field = data_source_config[section_wanted]["qc_data_merge_field"]
        except KeyError as err:
            self._download_config_error(err)
        return (
            sanger_sample_id_field,
            public_name_field,
            metadata_merge_field,
            in_silico_merge_field,
            qc_data_merge_field,
        )

    def _get_merge_qc_data_flag(self):
        data_source_config = self._get_data_source_config()
        project_specific_sections = {"juno": "metadata_download_juno", "gps": "metadata_download_gps"}
        section_wanted = project_specific_sections[self.current_project]
        try:
            merge_qc_data = data_source_config[section_wanted]["merge_qc_data"]
        except KeyError as err:
            self._download_config_error(err)
        return merge_qc_data

    def _metadata_df_to_csv(self, metadata_df, metadata_col_order):
        """
        Pass panda dataframe and column order.
        Returns CSV.
        """
        metadata_csv = metadata_df.to_csv(columns=metadata_col_order, index=False, quoting=QUOTE_NONNUMERIC)
        logging.debug("merged metadata, in silico and QC data as CSV:\n{}".format(metadata_csv))
        return metadata_csv

    def _metadata_download_to_pandas_data(self, api_data):
        """
        Transforms data returned by MetadataDownload methods into a form that can be loaded by pandas
        Something of this form:
           {"order": 1, "name": "Sanger_Sample_ID",  "value": "a_sammple_id"   }
           {"order": 2, "name": "Other_Field",       "value": "something_else" }
        will become:
           {"Sanger_Sample_ID": "a_sammple_id", "Other_Field": "something_else"}
        and a list of hte column ordering is also created:
           ["Sanger_Sample_ID", "Other_Field"]
        Returns tuple: data_dict,column_order_list
        """
        pandas_data = []
        col_order = []
        first_row = True
        for this_row in api_data:
            pandas_row = {}
            # get_metadata returns dicts incl. an item item `order` which should be used to sort columns
            for this_column in sorted(this_row, key=lambda col: (this_row[col]["order"])):
                if first_row:
                    col_order.append(this_row[this_column]["title"])
                # get_metadata returns dicts incl. items `name` and `value`for name & value of each column
                pandas_row[this_row[this_column]["title"]] = this_row[this_column]["value"]
            pandas_data.append(pandas_row)
            first_row = False
        return pandas_data, col_order

    def make_download_symlink(self, target_institution_key=None, **kwargs):
        """
        Pass the institution name _or_ cross_institution=True

        This creates a symlink from the web server download directory to the
        directory in which an institution's sample data (annotations,
        assemblies, reads etc.) or a cross-institution sample ZIP file can be found.

        The symlink has a random name so only someone given the URL will be
        able to access it.

        The symlink path (relative to web server document root) is returned.
        """
        if target_institution_key is None and not kwargs.get("cross_institution"):
            message = "must pass either a target institution key or 'cross_institution=True'"
            logging.error("{} parameter error: {}".format(__class__.__name__, message))
            raise ValueError(message)

        download_config_section = "data_download"
        download_dir_param = "web_dir"
        download_url_path_param = "url_path"
        cross_institution_dir_param = "cross_institution_dir"
        # read config, check required params
        data_sources = self._get_data_source_config()
        if (
            download_config_section not in data_sources
            or download_dir_param not in data_sources[download_config_section]
        ):
            return self._download_config_error(
                "data source config file {} does not provide the required parameter {}.{}".format(
                    self.data_source_config_name, download_config_section, download_dir_param
                )
            )
        download_web_dir = Path(data_sources[download_config_section][download_dir_param])
        if (
            download_config_section not in data_sources
            or download_url_path_param not in data_sources[download_config_section]
        ):
            return self._download_config_error(
                "data source config file {} does not provide the required parameter {}.{}".format(
                    self.data_source_config_name, download_config_section, download_url_path_param
                )
            )
        download_url_path = data_sources[download_config_section][download_url_path_param]
        if (
            download_config_section not in data_sources
            or cross_institution_dir_param not in data_sources[download_config_section]
        ):
            return self._download_config_error(
                "data source config file {} does not provide the required parameter {}.{}".format(
                    self.data_source_config_name, download_config_section, cross_institution_dir_param
                )
            )
        cross_institution_dir = data_sources[download_config_section][cross_institution_dir_param]
        if not download_web_dir.is_dir():
            return self._download_config_error(
                "data download web server directory {} does not exist (or not a directory)".format(
                    str(download_web_dir)
                )
            )
        logging.debug("web server data download dir = {}".format(str(download_web_dir)))
        # get the "target" directory where the data for the institution is kept, and check it exists
        # (Why an environment variable? Because this can be set by docker-compose, and it is a path
        # to a volume mount that is also set up by docker-compose.)
        data_inst_view_environ = DATA_INST_VIEW_ENVIRON[self.current_project]
        if data_inst_view_environ not in environ:
            return self._download_config_error("environment variable {} is not set".format(data_inst_view_environ))
        child_dir = cross_institution_dir if kwargs.get("cross_institution") else target_institution_key
        download_host_dir = Path(environ[data_inst_view_environ], child_dir)
        if not download_host_dir.is_dir():
            return self._download_config_error(
                "data download host directory {} does not exist (or not a directory)".format(str(download_host_dir))
            )
        logging.debug("host data download dir = {}".format(str(download_host_dir)))
        # create a randomly named symlink to present to the user (do..while is just in case the path exists already)
        while True:
            random_name = uuid4().hex
            data_download_link = Path(download_web_dir, random_name)
            download_url_path = "/".join([download_url_path, random_name])
            if not data_download_link.exists():
                break
        logging.debug("creating symlink {} -> {}".format(str(data_download_link), str(download_host_dir)))
        data_download_link.symlink_to(download_host_dir.absolute())
        return download_url_path

    def _get_file_size(self, path_instance):
        try:
            logging.debug("counting size of download file: {}  {}".format(path_instance, path_instance.stat().st_size))
            return path_instance.stat().st_size
        except OSError as err:
            logging.info(f"Failed to open file {path_instance}: {err}")
            return 0

    def _get_data_source_config(self):
        # read file if not cached
        if self.data_source_config is None:
            try:
                with open(self.data_source_config_name, READ_MODE) as data_source_config_file:
                    self.data_source_config = yaml.load(data_source_config_file, Loader=yaml.FullLoader)
            except EnvironmentError as err:
                self._download_config_error(err)
        # return config
        return self.data_source_config

    def _download_config_error(self, description):
        """
        Call for errors occurring in make_download_symlink().
        Pass error description of problem, which is logged.
        Raises DataSourceConfigError.
        """
        message = "Invalid data download config: {}".format(description)
        logging.error(message)
        raise DataSourceConfigError(message)
