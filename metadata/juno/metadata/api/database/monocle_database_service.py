from abc import ABC, abstractmethod
from metadata.api.model.metadata import Metadata


class MonocleDatabaseService(ABC):
    """ Base class for metadata access """

    @abstractmethod
    def update_sample_metadata(self, samples: dict) -> None:
        """ Update sample metadata in the database """
        pass

    @abstractmethod
    def get_download_metadata(self, keys: [str]) -> [Metadata]:
        """ Get download metadata for given list of 'sample:lane' keys """
        pass
