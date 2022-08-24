# FIXME
#
# This was temporarily copied from metadata/common/... to metadata/juno... and metadata/gps/...
# so that the JUNO and GPS metadta APIs have a different version of this file
#
# This was necessary because the database table names are hardcoded into the SQL queries in error
#
# The table names (as well as the list of columns in each table) should be read from the config.json file

import logging
from typing import Dict, List

from flask import current_app as application
from metadata.api.database.monocle_database_service import MonocleDatabaseService
from metadata.api.model.db_connection_config import DbConnectionConfig
from metadata.api.model.in_silico_data import InSilicoData
from metadata.api.model.metadata import Metadata
from metadata.api.model.qc_data import QCData
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text

logger = logging.getLogger()


class Connector:
    """Provide SQL Alchemy connections"""

    def __init__(self, config: DbConnectionConfig) -> None:
        self.application = application
        self.connection_url = config.connection_url
        self.engine = create_engine(self.connection_url)

    def get_connection(self) -> object:
        """Get a SQL Alchemy database connection"""
        return self.engine.connect()

    def get_transactional_connection(self) -> object:
        """Get a SQL Alchemy transactional database connection"""
        return self.engine.begin()


class MonocleDatabaseServiceImpl(MonocleDatabaseService):
    """DAO for metadata,in silico data and QC data access"""

    DELETE_ALL_SAMPLES_SQL = text("""delete from api_sample""")

    FILTER_SAMPLES_IN_SQL = """ \
            SELECT sanger_sample_id FROM api_sample WHERE {} IN :values"""

    FILTER_SAMPLES_IN_SQL_INCL_NULL = """ \
            SELECT sanger_sample_id FROM api_sample WHERE {} IN :values OR {} IS NULL"""

    IN_SILICO_FILTER_LANES_IN_SQL = """ \
            SELECT lane_id FROM in_silico WHERE {} IN :values"""

    IN_SILICO_FILTER_LANES_IN_SQL_INCL_NULL = """ \
            SELECT lane_id FROM in_silico WHERE {} IN :values OR {} IS NULL"""

    DISTINCT_FIELD_VALUES_SQL = """ \
            SELECT DISTINCT {} FROM api_sample WHERE submitting_institution IN :institutions"""

    DISTINCT_IN_SILICO_FIELD_VALUES_SQL = """ \
            SELECT DISTINCT {} FROM in_silico"""

    DISTINCT_QC_DATA_FIELD_VALUES_SQL = """ \
            SELECT DISTINCT {} FROM qc_data"""

    def __init__(self, connector: Connector) -> None:
        self.connector = connector
        self.initialize_sql_statements()

    def initialize_sql_insert_or_update(self, table, keys):
        return text(
            f"INSERT INTO {table} ("
            + ", ".join(keys)
            + ") VALUES ("
            + ", ".join(list(map(lambda k: f":{k}", keys)))
            + ") ON DUPLICATE KEY UPDATE "
            + ", ".join(list(map(lambda k: f"{k} = :{k}", keys)))
        )

    def initialize_sql_statements(self):
        self.config = self.connector.application.config

        # Metadata
        md_keys = list(self.config["metadata"]["spreadsheet_definition"].keys())
        self.SELECT_ALL_SAMPLES_SQL = text(
            "SELECT " + ", ".join(md_keys) + " FROM api_sample ORDER BY sanger_sample_id"
        )
        self.SELECT_SAMPLES_SQL = text(
            "SELECT " + ", ".join(md_keys) + " FROM api_sample WHERE sanger_sample_id IN :samples"
        )
        self.INSERT_OR_UPDATE_SAMPLE_SQL = self.initialize_sql_insert_or_update("api_sample", md_keys)

        # In silico
        in_silico_keys = list(self.config["in_silico_data"]["spreadsheet_definition"].keys())
        self.SELECT_ALL_IN_SILICO_SQL = text("SELECT " + ", ".join(in_silico_keys) + " FROM in_silico ORDER BY lane_id")
        self.SELECT_LANES_IN_SILICO_SQL = text(
            "SELECT " + ",".join(in_silico_keys) + " FROM in_silico WHERE lane_id IN :lanes"
        )
        self.INSERT_OR_UPDATE_IN_SILICO_SQL = self.initialize_sql_insert_or_update("in_silico", in_silico_keys)

        # QC data
        qc_keys = list(self.config["qc_data"]["spreadsheet_definition"].keys())
        self.SELECT_LANES_QC_DATA_SQL = text("SELECT " + ", ".join(qc_keys) + " FROM qc_data WHERE lane_id IN :lanes")
        self.INSERT_OR_UPDATE_QC_DATA_SQL = self.initialize_sql_insert_or_update("qc_data", qc_keys)

    def convert_string(self, val: str) -> str:
        """If a given string is empty return None"""
        return val if val else None

    def convert_int(self, val: str) -> int:
        """If a given string is empty then return None else try to convert to int"""
        if not val:
            return None

        try:
            int_val = int(val)
        except ValueError:
            logger.error("ERROR: Expected value {} to be an int!".format(val))
            raise

        return int_val

    def get_samples_filtered_by_metadata(self, filters: dict) -> List:
        """Get sample ids where their columns' values are in specified filters"""
        # TODO: Also consider other filters such as greater than/less than...
        sanger_sample_ids = []
        with self.connector.get_connection() as con:
            if len(filters) > 0:
                for filter, values in filters.items():
                    logging.info("filtering on {} for values {}".format(filter, values))
                    new_sanger_sample_ids = []
                    try:
                        if None in values:
                            this_sql_template = self.FILTER_SAMPLES_IN_SQL_INCL_NULL.format(filter, filter)
                        else:
                            this_sql_template = self.FILTER_SAMPLES_IN_SQL.format(filter)
                        rs = con.execute(text(this_sql_template), values=tuple(values))
                        new_sanger_sample_ids.extend([row["sanger_sample_id"] for row in rs])
                        if len(sanger_sample_ids) > 0:
                            tmp_ids = [id for id in new_sanger_sample_ids if id in sanger_sample_ids]
                            sanger_sample_ids = tmp_ids
                        else:
                            sanger_sample_ids = new_sanger_sample_ids
                    except OperationalError as e:
                        if "Unknown column" in str(e):
                            logging.error('attempted to apply filter to unknown field "{}"'.format(filter))
                            return None
                        else:
                            raise e
            else:
                rs = con.execute(self.SELECT_ALL_SAMPLES_SQL)
                sanger_sample_ids = [row["sanger_sample_id"] for row in rs]

        return sanger_sample_ids

    def get_lanes_filtered_by_in_silico_data(self, filters: dict) -> List:
        """Get lane ids from in silico data that match the specified filters"""
        # TODO: Also consider other filters such as greater than/less than...

        lane_ids = []
        with self.connector.get_connection() as con:
            if len(filters) > 0:
                for filter, values in filters.items():
                    logging.info("filtering on {} for values {}".format(filter, values))
                    new_lane_ids = []
                    try:
                        if None in values:
                            this_sql_template = self.IN_SILICO_FILTER_LANES_IN_SQL_INCL_NULL.format(filter, filter)
                        else:
                            this_sql_template = self.IN_SILICO_FILTER_LANES_IN_SQL.format(filter)
                        rs = con.execute(text(this_sql_template), values=tuple(values))
                        new_lane_ids.extend([row["lane_id"] for row in rs])
                        if len(lane_ids) > 0:
                            tmp_ids = [id for id in new_lane_ids if id in lane_ids]
                            lane_ids = tmp_ids
                        else:
                            lane_ids = new_lane_ids
                    except OperationalError as e:
                        if "Unknown column" in str(e):
                            logging.error('attempted to apply filter to unknown field "{}"'.format(filter))
                            return None
                        else:
                            raise e
            else:
                rs = con.execute(self.SELECT_ALL_IN_SILICO_SQL)
                lane_ids = [row["lane_id"] for row in rs]

        return lane_ids

    def get_distinct_values(self, field_type: str, fields: list, institutions: list) -> Dict:
        """
        Return distinct values found in db for each field name passed,
        from samples from certain institutions.
        Pass the field type ('metadata', 'in silico' or 'qc data');
        a list of names of the fields of interest; and a list of institution
        names.
        If any of the field names passed are non-existent, returns None
        """
        sql_query = {
            "metadata": self.DISTINCT_FIELD_VALUES_SQL,
            "in silico": self.DISTINCT_IN_SILICO_FIELD_VALUES_SQL,
            "qc data": self.DISTINCT_QC_DATA_FIELD_VALUES_SQL,
        }
        if field_type not in sql_query.keys():
            raise ValueError(
                "{} must be passed one of {}, not {}".format(
                    __class__.__name__, ", ".join(sql_query.keys()), field_type
                )
            )
        distinct_values = []
        with self.connector.get_connection() as con:
            for this_field in fields:
                try:
                    rs = con.execute(
                        text(sql_query[field_type].format(this_field)),
                        institutions=tuple(institutions),
                    )
                    these_distinct_values = []
                    includes_none = False
                    for row in rs:
                        if row[this_field] is None:
                            includes_none = True
                        else:
                            these_distinct_values.append(str(row[this_field]))
                    # can't sort if the list contains None, so sort...
                    these_distinct_values = sorted(these_distinct_values)
                    # ...and then add a None if there should be one in the list
                    if includes_none:
                        these_distinct_values.append(None)
                    if len(these_distinct_values) > 0:
                        distinct_values.append({"name": this_field, "values": these_distinct_values})

                except OperationalError as e:
                    if "Unknown column" in str(e):
                        logging.error('attempted to get distinct values from unknown field "{}"'.format(this_field))
                        return None
                    else:
                        raise e
        logging.info("distinct {} values: {}".format(field_type, distinct_values))
        return distinct_values

    def get_samples(self) -> List[Metadata]:
        """Retrieve all sample records"""
        results = []
        with self.connector.get_connection() as con:
            rs = con.execute(self.SELECT_ALL_SAMPLES_SQL)
        for row in rs:
            params = {k: row[k] for k in self.config["metadata"]["spreadsheet_definition"]}
            results.append(Metadata(**params))

        return results

    def update_sample_metadata(self, metadata_list: List[Metadata]) -> None:
        """Update sample metadata in the database"""

        if not metadata_list:
            return

        logger.info(
            "update_sample_metadata: About to write {} upload samples to the database...".format(len(metadata_list))
        )

        # Use a transaction...
        with self.connector.get_transactional_connection() as con:
            for metadata in metadata_list:
                params = {k: metadata.__dict__[k] for k in self.config["metadata"]["spreadsheet_definition"]}
                self._convert_empty_strings_to_none(params)
                logger.debug("SQL exec oparams:\n{}".format(params))
                con.execute(self.INSERT_OR_UPDATE_SAMPLE_SQL, **params)

        logger.info("update_sample_metadata completed")

    def update_lane_in_silico_data(self, in_silico_data_list: List[InSilicoData]) -> None:
        """Update sample in silico data in the database"""

        if not in_silico_data_list:
            return

        logger.info(
            "update_lane_in_silico_data: About to write {} upload samples to the database...".format(
                len(in_silico_data_list)
            )
        )

        # Use a transaction...
        with self.connector.get_transactional_connection() as con:
            for in_silico_data in in_silico_data_list:
                params = {
                    k: self.convert_string(in_silico_data.__dict__[k])
                    for k in self.config["in_silico_data"]["spreadsheet_definition"]
                }
                self._convert_empty_strings_to_none(params)
                logger.debug("SQL exec params:\n{}".format(params))
                con.execute(self.INSERT_OR_UPDATE_IN_SILICO_SQL, **params)

        logger.info("update_lane_in_silico_data completed")

    def update_lane_qc_data(self, qc_data_list: List[QCData]) -> None:
        """Update sample QC data in the database"""

        if not qc_data_list:
            return

        logger.info(
            "update_lane_qc_data: About to write {} upload samples to the database...".format(len(qc_data_list))
        )

        # Use a transaction...
        with self.connector.get_transactional_connection() as con:
            for qc_data in qc_data_list:
                params = {
                    k: self.convert_string(qc_data.__dict__[k])
                    for k in self.config["qc_data"]["spreadsheet_definition"]
                }
                self._convert_empty_strings_to_none(params)
                logger.debug("SQL exec params:\n{}".format(params))
                con.execute(self.INSERT_OR_UPDATE_QC_DATA_SQL, **params)

        logger.info("update_lane_qc_data completed")

    def _convert_empty_strings_to_none(self, db_params_dict):
        """Dicts passed to SQLAlchemy execute() should have None, not empty strings, for missing values."""
        for this_param_key in db_params_dict:
            if "" == db_params_dict[this_param_key]:
                logging.debug("setting {} to None".format(this_param_key))
                db_params_dict[this_param_key] = None
        return db_params_dict

    def get_download_metadata(self, keys: List[str]) -> List[Metadata]:
        """Get download metadata for given list of samples"""

        if len(keys) == 0:
            return []

        results = []
        sanger_sample_ids = tuple(keys)

        logger.info(
            "get_download_metadata: About to pull {} sample records from the database...".format(len(sanger_sample_ids))
        )
        logger.debug("get_download_metadata: Pulling sample ids {} from the database...".format(sanger_sample_ids))
        with self.connector.get_connection() as con:
            rs = con.execute(self.SELECT_SAMPLES_SQL, samples=sanger_sample_ids)

        for row in rs:
            params = {k: row[k] for k in self.config["metadata"]["spreadsheet_definition"]}
            results.append(Metadata(**params))

        logger.debug("get_download_metadata: Pulled records of samples {} from the database...".format(results))

        return results

    def get_download_qc_data(self, keys: List[str]) -> List[QCData]:
        """Get download QC data for given list of lane keys"""

        if len(keys) == 0:
            return []

        results = []
        lane_ids = tuple(keys)
        with self.connector.get_connection() as con:
            rs = con.execute(self.SELECT_LANES_QC_DATA_SQL, lanes=lane_ids)

        for row in rs:
            params = {k: row[k] for k in self.config["qc_data"]["spreadsheet_definition"]}
            results.append(QCData(**params))

        return results

    def get_download_in_silico_data(self, keys: List[str]) -> List[InSilicoData]:
        """Get download in silico data for given list of lane keys"""

        if len(keys) == 0:
            return []

        results = []
        lane_ids = tuple(keys)
        with self.connector.get_connection() as con:
            rs = con.execute(self.SELECT_LANES_IN_SILICO_SQL, lanes=lane_ids)

        for row in rs:
            params = {k: row[k] for k in self.config["in_silico_data"]["spreadsheet_definition"]}
            results.append(InSilicoData(**params))

        return results
