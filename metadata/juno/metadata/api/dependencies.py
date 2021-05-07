import os
import logging
from flask import Config
from injector import singleton, Module, provider
from metadata.api.configuration import *
from metadata.api.upload_handler import UploadHandler
from metadata.api.download_handler import DownloadHandler
from metadata.api.database.monocle_database_service import MonocleDatabaseService
from metadata.api.database.monocle_database_service_impl import MonocleDatabaseServiceImpl
from metadata.api.database.monocle_database_service_noop_impl import MonocleDatabaseServiceNoOpImpl

logger = logging.getLogger()


class MetadataApiModule(Module):
    """ Dependency injection handler for this API """

    API_TEST_MODE = False

    def __init__(self) -> None:
        try:
            self.API_TEST_MODE = os.environ['API_TEST_MODE'].lower() == 'true'
        except KeyError:
            pass

    @provider
    @singleton
    def metadata_dao(self, config: Config) -> MonocleDatabaseService:
        if not self.API_TEST_MODE:
            return MonocleDatabaseServiceImpl(read_database_connection_config(config))
        else:
            logger.info('Using mock database back end')
            return MonocleDatabaseServiceNoOpImpl(read_mock_database_connection_config(config))

    @provider
    def upload_handler(self, config: Config) -> UploadHandler:
        return UploadHandler(read_spreadsheet_definition_config(config))

    @provider
    def download_handler(self, config: Config) -> DownloadHandler:
        return DownloadHandler(read_spreadsheet_definition_config(config))
