from typing import Any, Dict, List

from metadata.api.model.in_silico_data import InSilicoData
from metadata.api.model.metadata import Metadata
from metadata.api.model.qc_data import QCData
from metadata.lib.download_handler import DownloadHandler


class DownloadMetadataHandler(DownloadHandler):
    """Construct API metadata download response message data structures"""

    def read_download_metadata(self, keys: List[str]) -> List[Metadata]:
        """
        Return a list of metadata objects that correspond to the given sample id/lane id key values.
        """
        dao = self.get_dao()
        return dao.get_download_metadata(keys)

    def create_download_response(self, download: [Metadata]) -> List[Dict[Any, Any]]:
        """Create the correct data structure for download responses"""

        response: List[Dict[Any, Any]] = []

        for entry in download:
            record_dict = {}
            self.__field_index = 1
            for k in self.application.config["metadata"]["spreadsheet_definition"].keys():
                self._append_to_dict(record_dict, k, entry.__dict__[k])

            response.append(record_dict)

        return response


class DownloadInSilicoHandler(DownloadHandler):
    """Construct API in silico data download response message data structures"""

    def read_download_in_silico_data(self, keys: List[str]) -> List[InSilicoData]:
        """
        Return a list of in silico data objects that correspond to the given sample id/lane id key values.
        """
        dao = self.get_dao()
        return dao.get_download_in_silico_data(keys)

    def create_download_response(self, download: [InSilicoData]) -> List[Dict[Any, Any]]:
        """Create the correct data structure for download responses"""

        response: List[Dict[Any, Any]] = []

        for entry in download:
            record_dict = {}
            self.__field_index = 1
            for k in self.application.config["in_silico_data"]["spreadsheet_definition"].keys():
                self._append_to_dict(record_dict, k, entry.__dict__[k])

            response.append(record_dict)

        return response


class DownloadQCDataHandler(DownloadHandler):
    """Construct API QC data download response message data structures"""

    def read_download_qc_data(self, keys: List[str]) -> List[QCData]:
        """
        Return a list of QC data objects that correspond to the given sample id/lane id key values.
        """
        dao = self.get_dao()
        return dao.get_download_qc_data(keys)

    def create_download_response(self, download: [QCData]) -> List[Dict[Any, Any]]:
        """Create the correct data structure for download responses"""

        response: List[Dict[Any, Any]] = []

        for entry in download:
            record_dict = {}
            self.__field_index = 1
            for k in self.application.config["qc_data"]["spreadsheet_definition"].keys():
                self._append_to_dict(record_dict, k, entry.__dict__[k])

            response.append(record_dict)

        return response
