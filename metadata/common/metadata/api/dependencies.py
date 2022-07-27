import logging
import os

from flask import Config
from injector import Module, provider, singleton
from metadata.api.configuration import (
    read_database_connection_config,
    read_mock_database_connection_config,
    read_spreadsheet_definition_config,
)
from metadata.api.database.monocle_database_service import MonocleDatabaseService
from metadata.api.database.monocle_database_service_impl import Connector, MonocleDatabaseServiceImpl
from metadata.api.database.monocle_database_service_noop_impl import MonocleDatabaseServiceNoOpImpl
from metadata.api.download_handlers import DownloadInSilicoHandler, DownloadMetadataHandler, DownloadQCDataHandler
from metadata.api.upload_handlers import UploadInSilicoHandler, UploadMetadataHandler, UploadQCDataHandler

logger = logging.getLogger()


class MetadataApiModule(Module):
    """Dependency injection handler for this API"""

    API_TEST_MODE = False

    def __init__(self) -> None:
        try:
            self.API_TEST_MODE = os.environ["API_TEST_MODE"].lower() == "true"
        except KeyError:
            pass

    @provider
    @singleton
    def metadata_dao(self, config: Config) -> MonocleDatabaseService:
        if not self.API_TEST_MODE:
            return MonocleDatabaseServiceImpl(Connector(read_database_connection_config(config)))
        else:
            logger.info("Using mock database back end")
            return MonocleDatabaseServiceNoOpImpl(read_mock_database_connection_config(config))

    @provider
    def upload_metadata_handler(self, config: Config, metadata_dao: MonocleDatabaseService) -> UploadMetadataHandler:
        do_validation = False
        try:
            do_validation = config["metadata"]["upload_validation_enabled"]
        except KeyError:
            pass
        upload_metadata_handler = UploadMetadataHandler(
            metadata_dao, read_spreadsheet_definition_config(config["metadata"]), do_validation
        )
        return upload_metadata_handler

    @provider
    def upload_in_silico_handler(self, config: Config, metadata_dao: MonocleDatabaseService) -> UploadInSilicoHandler:
        do_validation = False
        try:
            do_validation = config["in_silico_data"]["upload_validation_enabled"]
        except KeyError:
            pass
        upload_in_silico_handler = UploadInSilicoHandler(
            metadata_dao, read_spreadsheet_definition_config(config["in_silico_data"]), do_validation
        )
        return upload_in_silico_handler

    @provider
    def upload_qc_data_handler(self, config: Config, metadata_dao: MonocleDatabaseService) -> UploadQCDataHandler:
        do_validation = False
        try:
            do_validation = config["qc_data"]["upload_validation_enabled"]
        except KeyError:
            pass
        upload_qc_data_handler = UploadQCDataHandler(
            metadata_dao, read_spreadsheet_definition_config(config["qc_data"]), do_validation
        )
        return upload_qc_data_handler

    @provider
    def download_metadata_handler(
        self, config: Config, metadata_dao: MonocleDatabaseService
    ) -> DownloadMetadataHandler:
        return DownloadMetadataHandler(metadata_dao, read_spreadsheet_definition_config(config["metadata"]))

    @provider
    def download_in_silico_handler(
        self, config: Config, metadata_dao: MonocleDatabaseService
    ) -> DownloadInSilicoHandler:
        return DownloadInSilicoHandler(metadata_dao, read_spreadsheet_definition_config(config["in_silico_data"]))

    @provider
    def download_qc_data_handler(self, config: Config, metadata_dao: MonocleDatabaseService) -> DownloadQCDataHandler:
        return DownloadQCDataHandler(metadata_dao, read_spreadsheet_definition_config(config["qc_data"]))
