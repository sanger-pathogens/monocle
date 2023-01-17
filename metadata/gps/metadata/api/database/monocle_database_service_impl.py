# FIXME
#
# This was temporarily copied from metadata/common/... to metadata/juno... and metadata/gps/...
# so that the JUNO and GPS metadta APIs have a different version of this file
#
# This was necessary because the database table names are hardcoded into the SQL queries in error
#
# The table names (as well as the list of columns in each table) should be read from the config.json file

import logging
from typing import List

from flask import current_app as application
from metadata.api.database.monocle_database_service import MonocleDatabaseService
from metadata.api.model.db_connection_config import DbConnectionConfig
from metadata.api.model.in_silico_data import InSilicoData
from metadata.api.model.metadata import Metadata
from metadata.api.model.qc_data import QCData
from sqlalchemy import create_engine
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

    DELETE_ALL_SAMPLES_SQL = text("""delete from gps_sample""")

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
            "SELECT " + ", ".join(md_keys) + " FROM gps_sample ORDER BY sanger_sample_id"
        )
        self.SELECT_SAMPLES_SQL = text(
            "SELECT " + ", ".join(md_keys) + " FROM gps_sample WHERE sanger_sample_id IN :samples"
        )
        self.INSERT_OR_UPDATE_SAMPLE_SQL = self.initialize_sql_insert_or_update("gps_sample", md_keys)

        # In silico
        in_silico_keys = list(self.config["in_silico_data"]["spreadsheet_definition"].keys())
        self.SELECT_ALL_IN_SILICO_SQL = text(
            "SELECT " + ", ".join(in_silico_keys) + " FROM gps_in_silico ORDER BY lane_id"
        )
        self.SELECT_LANES_IN_SILICO_SQL = text(
            "SELECT " + ",".join(in_silico_keys) + " FROM gps_in_silico WHERE lane_id IN :lanes"
        )
        self.INSERT_OR_UPDATE_IN_SILICO_SQL = self.initialize_sql_insert_or_update("gps_in_silico", in_silico_keys)

        # QC data
        qc_keys = list(self.config["qc_data"]["spreadsheet_definition"].keys())
        self.SELECT_LANES_QC_DATA_SQL = text(
            "SELECT " + ", ".join(qc_keys) + " FROM gps_qc_data WHERE lane_id IN :lanes"
        )
        self.INSERT_OR_UPDATE_QC_DATA_SQL = self.initialize_sql_insert_or_update("gps_qc_data", qc_keys)

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
                params = {
                    k: self.convert_string(metadata.__dict__[k])
                    for k in self.config["metadata"]["spreadsheet_definition"]
                }
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
                con.execute(self.INSERT_OR_UPDATE_QC_DATA_SQL, **params)

        logger.info("update_lane_qc_data completed")

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
