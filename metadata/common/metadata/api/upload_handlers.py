from typing import List

from metadata.api.model.in_silico_data import InSilicoData
from metadata.api.model.metadata import Metadata
from metadata.api.model.qc_data import QCData
from metadata.lib.upload_handler import UploadHandler, logger


class UploadMetadataHandler(UploadHandler):
    def parse(self) -> List[Metadata]:
        """Parse the data frame into dataclasses"""
        results = []
        df = self.data_frame()
        for _, row in df.iterrows():
            metadata_dict = {}
            for spreadsheet_column_name in self.application.config["metadata"]["spreadsheet_definition"]:
                metadata_dict[spreadsheet_column_name] = self.get_cell_value(spreadsheet_column_name, row)
            metadata = Metadata(**metadata_dict)
            results.append(metadata)
        return results

    def store(self):
        df = self.data_frame()
        if df is not None:
            logger.info("Storing spreadsheet...")
            dao = self.get_dao()
            dao.update_sample_metadata(self.parse())
        else:
            raise RuntimeError("No spreadsheet is currently loaded. Unable to store.")


class UploadInSilicoHandler(UploadHandler):
    def parse(self):
        """Parse in silico data into dataclass"""
        results = []
        df = self.data_frame()
        for _, row in df.iterrows():
            isd_dict = {}
            for k in self.application.config["in_silico_data"]["spreadsheet_definition"].keys():
                isd_dict[k] = self.get_cell_value(k, row)
            in_silico_data = InSilicoData(**isd_dict)
            results.append(in_silico_data)
        return results

    def store(self):
        df = self.data_frame()
        if df is not None:
            logger.info("Storing spreadsheet...")
            dao = self.get_dao()
            dao.update_lane_in_silico_data(self.parse())
        else:
            raise RuntimeError("No spreadsheet is currently loaded. Unable to store.")


class UploadQCDataHandler(UploadHandler):
    def parse(self):
        """Parse in QC data into dataclass"""
        results = []
        df = self.data_frame()
        for _, row in df.iterrows():
            isd_dict = {}
            for k in self.application.config["qc_data"]["spreadsheet_definition"].keys():
                isd_dict[k] = self.get_cell_value(k, row)
            qc_data = QCData(**isd_dict)
            results.append(qc_data)
        return results

    def store(self):
        df = self.data_frame()
        if df is not None:
            logger.info("Storing spreadsheet...")
            dao = self.get_dao()
            dao.update_lane_qc_data(self.parse())
        else:
            raise RuntimeError("No spreadsheet is currently loaded. Unable to store.")
