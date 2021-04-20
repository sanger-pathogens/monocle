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

    """ =============== Utility methods ============= """

    @staticmethod
    def split_keys(keys: [str]) -> [str]:
        """ Get lists of samples and associated lanes from 'sample:lane' keys """

        samples = []
        lanes = []
        for key in keys:
            key_parts = key.split(':')
            if len(key_parts) == 2 and key_parts[0] != '' and key_parts[1] != '':
                samples.append(key_parts[0])
                lanes.append(key_parts[1])
            else:
                raise ValueError("Illegal key format: " + key)

        return samples, lanes
