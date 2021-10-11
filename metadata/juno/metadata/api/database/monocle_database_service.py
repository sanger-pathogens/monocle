from abc import ABC, abstractmethod
from typing import List
from metadata.api.model.metadata import Metadata
from metadata.api.model.in_silico_data import InSilicoData
from metadata.api.model.institution import Institution


class MonocleDatabaseService(ABC):
    """ Base class for metadata access """

    @abstractmethod
    def get_institution_names(self) -> List[Institution]:
        """ Return a list of institutions, names only """
        pass

    @abstractmethod
    def get_samples(self) -> List[Institution]:
        """ Return a list of samples """
        pass

    @abstractmethod
    def get_institutions(self) -> List[Institution]:
        """ Return a list of institutions """
        pass

    @abstractmethod
    def update_sample_metadata(self, metadata_list: List[Metadata]) -> None:
        """ Update sample metadata in the database """
        pass

    @abstractmethod
    def update_lane_in_silico_data(self, in_silico_data_list: List[InSilicoData]) -> None:
        """ Update sample in silico data in the database """
        pass

    @abstractmethod
    def get_download_metadata(self, keys: List[str]) -> List[Metadata]:
        """ Get download metadata for given list of 'sample:lane' keys """
        pass

    @abstractmethod
    def get_download_in_silico_data(self, keys: List[str]) -> List[Metadata]:
        """ Get download in silico data for given list of lane keys """
        pass
