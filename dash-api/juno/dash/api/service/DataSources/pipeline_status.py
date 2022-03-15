import logging
from os import environ

import pandas
import yaml
from pandas import DataFrame, read_csv


class PipelineStatusDataError(Exception):
    """exception when an error is detected with the pipeline status data"""

    pass


class PipelineStatus:
    """provides access to pipeline status data"""

    data_sources_config = "data_sources.yml"
    data_source = "pipeline_status"
    pipeline_lane_field = "Name"
    stage_done_string = "Done"
    stage_failed_string = "Failed"
    stage_null_string = "-"
    # these are the pipeline stages we'd like information about
    pipeline_stage_fields = ["Import", "QC", "Assemble", "Annotate"]

    def __init__(self, config=None):
        if config is None:
            config = self.data_sources_config
        with open(config, "r") as file:
            data_sources = yaml.load(file, Loader=yaml.FullLoader)
            this_source = data_sources[self.data_source]
        data_path_environ = this_source["data_path_environ"]
        try:
            data_path = environ[data_path_environ]
        except KeyError:
            message = "environment variable {} is not set".format(data_path_environ)
            logging.error(message)
            raise PipelineStatusDataError(message)
        self.csv_file = "/".join([data_path, this_source["csv_file"]])
        self.num_columns = this_source["num_columns"]
        self.populate_dataframe(self.csv_file)

    def populate_dataframe(self, csv_filename):
        logging.info("reading pipeline status data from {}".format(csv_filename))
        with open(csv_filename, "r") as csv:
            self.dataframe = pandas.read_csv(csv).set_index(self.pipeline_lane_field)
        logging.debug(self.dataframe)
        self.validate_dataframe()
        return self.dataframe

    # some basic validation
    # TODO consider adding a proper schema for pandas to do thorough validation
    def validate_dataframe(self):
        # because one columns is used as index, number of ciolumns is the CSV is one greater than pandas tells us
        num_columns_read = len(self.dataframe.columns) + 1
        if self.num_columns != num_columns_read:
            logging.error(
                "Pipeline status data file {} has {} columns, but {} are expected".format(
                    self.csv_file, num_columns_read, self.num_columns
                )
            )
            raise PipelineStatusDataError("pipeline status data is badly formatted")
        row_error_found = False
        for this_row_num_columns_read in [c + 1 for c in self.dataframe.count(axis="columns")]:
            if self.num_columns != this_row_num_columns_read:
                logging.error(
                    "Pipeline status data file {} contains a row with {} columns, but {} are expected for all rows".format(
                        self.csv_file, this_row_num_columns_read, self.num_columns
                    )
                )
                row_error_found = True
        if row_error_found:
            raise PipelineStatusDataError("pipeline status data is badly formatted")

    def lane_status(self, lane_id):
        assert self.dataframe is not None, "lane_status() called before dataframe was populated"
        logging.debug("extracting pipeline status data for lane {}".format(lane_id))
        status_data = {
            "FAILED": False,
            "SUCCESS": False,
        }
        num_stages_done = 0
        for this_field in self.pipeline_stage_fields:
            try:
                this_value = self.dataframe.loc[lane_id, this_field]
            except KeyError:
                this_value = None
            # if a value was read...
            if this_value is not None:
                # convert "null" string to `None`
                if this_value == self.stage_null_string:
                    this_value = None
                # any occurrence of the "failed" string sets FAILED flag
                elif this_value == self.stage_failed_string:
                    # if any stage fails, flag lane as failed
                    status_data["FAILED"] = True
                    logging.debug("   found failed status for {} stage".format(this_field))
                # the "done" string increments the count of stages done
                elif this_value == self.stage_done_string:
                    num_stages_done += 1
            status_data[this_field] = this_value
        # if all stages are done, flag lane as completed successfully
        if len(self.pipeline_stage_fields) == num_stages_done:
            status_data["SUCCESS"] = True
            logging.debug("   all stages are '{}'".format(self.stage_done_string))
        logging.debug("   lane status: {}".format(status_data))
        return status_data
