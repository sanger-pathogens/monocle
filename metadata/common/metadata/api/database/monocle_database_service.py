from abc import ABC, abstractmethod
from typing import Dict, List

from flask import request
from metadata.api.model.in_silico_data import InSilicoData
from metadata.api.model.institution import Institution
from metadata.api.model.metadata import Metadata
from metadata.api.model.qc_data import QCData


class MonocleDatabaseService(ABC):
    """Base class for metadata access"""

    @abstractmethod
    def get_institution_names(self) -> List[Institution]:
        """Return a list of institutions, names only"""
        pass

    @abstractmethod
    def get_samples(self) -> List[Metadata]:
        """Return a list of samples"""
        pass

    @abstractmethod
    def get_samples_filtered_by_metadata(self, filters: dict) -> List:
        """Return a list of samples ids"""
        pass

    @abstractmethod
    def get_lanes_filtered_by_in_silico_data(self, filters: dict) -> List:
        """Return a list of lane ids"""
        pass

    @abstractmethod
    def get_distinct_values(self, fields: list) -> Dict:
        """Return a distinct values found in db for each field name passed"""
        pass

    @abstractmethod
    def get_institutions(self, req_obj: request) -> List[Institution]:
        """Return a list of institutions"""
        pass

    @abstractmethod
    def update_sample_metadata(self, metadata_list: List[Metadata]) -> None:
        """Update sample metadata in the database"""
        pass

    @abstractmethod
    def update_lane_in_silico_data(self, in_silico_data_list: List[InSilicoData]) -> None:
        """Update sample in silico data in the database"""
        pass

    @abstractmethod
    def update_lane_qc_data(self, qc_data_list: List[QCData]) -> None:
        """Update sample QC data in the database"""
        pass

    @abstractmethod
    def get_download_metadata(self, keys: List[str]) -> List[Metadata]:
        """Get download metadata for given list of 'sample:lane' keys"""
        pass

    @abstractmethod
    def get_download_in_silico_data(self, keys: List[str]) -> List[InSilicoData]:
        """Get download in silico data for given list of lane keys"""
        pass

    @abstractmethod
    def get_download_qc_data(self, keys: List[str]) -> List[QCData]:
        """Get download QC data for given list of lane keys"""
        pass
