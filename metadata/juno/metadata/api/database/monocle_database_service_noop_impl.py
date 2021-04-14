from metadata.api.model.metadata import Metadata
from metadata.api.model.db_connection_config import DbConnectionConfig
from metadata.api.database.monocle_database_service import MonocleDatabaseService


class MonocleDatabaseServiceNoOpImpl(MonocleDatabaseService):
    """ A dummy implementation for end to end testing """

    def __init__(self, config: DbConnectionConfig) -> None:
        pass

    def get_connection(self) -> None:
        pass

    def update_sample_metadata(self, samples: dict) -> None:
        """ Update sample metadata in the database """
        pass

    def get_download_metadata(self, keys: [str]) -> [Metadata]:
        """ Get download metadata for given list of 'sample:lane' keys """

