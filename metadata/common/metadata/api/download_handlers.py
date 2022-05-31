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
            self._append_to_dict(record_dict, "sanger_sample_id", entry.sanger_sample_id)
            self._append_to_dict(record_dict, "supplier_sample_name", entry.supplier_sample_name)
            self._append_to_dict(record_dict, "public_name", entry.public_name)
            self._append_to_dict(record_dict, "lane_id", entry.lane_id)
            self._append_to_dict(record_dict, "study_name", entry.study_name)
            self._append_to_dict(record_dict, "study_ref", entry.study_ref)
            self._append_to_dict(record_dict, "selection_random", entry.selection_random)
            self._append_to_dict(record_dict, "country", entry.country)
            self._append_to_dict(record_dict, "county_state", entry.county_state)
            self._append_to_dict(record_dict, "city", entry.city)
            self._append_to_dict(record_dict, "submitting_institution", entry.submitting_institution)
            self._append_to_dict(record_dict, "collection_year", entry.collection_year)
            self._append_to_dict(record_dict, "collection_month", entry.collection_month)
            self._append_to_dict(record_dict, "collection_day", entry.collection_day)
            self._append_to_dict(record_dict, "host_species", entry.host_species)
            self._append_to_dict(record_dict, "gender", entry.gender)
            self._append_to_dict(record_dict, "age_group", entry.age_group)
            self._append_to_dict(record_dict, "age_years", entry.age_years)
            self._append_to_dict(record_dict, "age_months", entry.age_months)
            self._append_to_dict(record_dict, "age_weeks", entry.age_weeks)
            self._append_to_dict(record_dict, "age_days", entry.age_days)
            self._append_to_dict(record_dict, "host_status", entry.host_status)
            self._append_to_dict(record_dict, "disease_type", entry.disease_type)
            self._append_to_dict(record_dict, "disease_onset", entry.disease_onset)
            self._append_to_dict(record_dict, "isolation_source", entry.isolation_source)
            self._append_to_dict(record_dict, "serotype", entry.serotype)
            self._append_to_dict(record_dict, "serotype_method", entry.serotype_method)
            self._append_to_dict(record_dict, "infection_during_pregnancy", entry.infection_during_pregnancy)
            self._append_to_dict(record_dict, "maternal_infection_type", entry.maternal_infection_type)
            self._append_to_dict(record_dict, "gestational_age_weeks", entry.gestational_age_weeks)
            self._append_to_dict(record_dict, "birth_weight_gram", entry.birth_weight_gram)
            self._append_to_dict(record_dict, "apgar_score", entry.apgar_score)
            self._append_to_dict(record_dict, "ceftizoxime", entry.ceftizoxime)
            self._append_to_dict(record_dict, "ceftizoxime_method", entry.ceftizoxime_method)
            self._append_to_dict(record_dict, "cefoxitin", entry.cefoxitin)
            self._append_to_dict(record_dict, "cefoxitin_method", entry.cefoxitin_method)
            self._append_to_dict(record_dict, "cefotaxime", entry.cefotaxime)
            self._append_to_dict(record_dict, "cefotaxime_method", entry.cefotaxime_method)
            self._append_to_dict(record_dict, "cefazolin", entry.cefazolin)
            self._append_to_dict(record_dict, "cefazolin_method", entry.cefazolin_method)
            self._append_to_dict(record_dict, "ampicillin", entry.ampicillin)
            self._append_to_dict(record_dict, "ampicillin_method", entry.ampicillin_method)
            self._append_to_dict(record_dict, "penicillin", entry.penicillin)
            self._append_to_dict(record_dict, "penicillin_method", entry.penicillin_method)
            self._append_to_dict(record_dict, "erythromycin", entry.erythromycin)
            self._append_to_dict(record_dict, "erythromycin_method", entry.erythromycin_method)
            self._append_to_dict(record_dict, "clindamycin", entry.clindamycin)
            self._append_to_dict(record_dict, "clindamycin_method", entry.clindamycin_method)
            self._append_to_dict(record_dict, "tetracycline", entry.tetracycline)
            self._append_to_dict(record_dict, "tetracycline_method", entry.tetracycline_method)
            self._append_to_dict(record_dict, "levofloxacin", entry.levofloxacin)
            self._append_to_dict(record_dict, "levofloxacin_method", entry.levofloxacin_method)
            self._append_to_dict(record_dict, "ciprofloxacin", entry.ciprofloxacin)
            self._append_to_dict(record_dict, "ciprofloxacin_method", entry.ciprofloxacin_method)
            self._append_to_dict(record_dict, "daptomycin", entry.daptomycin)
            self._append_to_dict(record_dict, "daptomycin_method", entry.daptomycin_method)
            self._append_to_dict(record_dict, "vancomycin", entry.vancomycin)
            self._append_to_dict(record_dict, "vancomycin_method", entry.vancomycin_method)
            self._append_to_dict(record_dict, "linezolid", entry.linezolid)
            self._append_to_dict(record_dict, "linezolid_method", entry.linezolid_method)

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
            self._append_to_dict(record_dict, "lane_id", entry.lane_id),
            self._append_to_dict(record_dict, "cps_type", entry.cps_type),
            self._append_to_dict(record_dict, "ST", entry.ST),
            self._append_to_dict(record_dict, "adhP", entry.adhP),
            self._append_to_dict(record_dict, "pheS", entry.pheS),
            self._append_to_dict(record_dict, "atr", entry.atr),
            self._append_to_dict(record_dict, "glnA", entry.glnA),
            self._append_to_dict(record_dict, "sdhA", entry.sdhA),
            self._append_to_dict(record_dict, "glcK", entry.glcK),
            self._append_to_dict(record_dict, "tkt", entry.tkt),
            self._append_to_dict(record_dict, "twenty_three_S1", entry.twenty_three_S1),
            self._append_to_dict(record_dict, "twenty_three_S3", entry.twenty_three_S3),
            self._append_to_dict(record_dict, "AAC6APH2", entry.AAC6APH2),
            self._append_to_dict(record_dict, "AADECC", entry.AADECC),
            self._append_to_dict(record_dict, "ANT6", entry.ANT6),
            self._append_to_dict(record_dict, "APH3III", entry.APH3III),
            self._append_to_dict(record_dict, "APH3OTHER", entry.APH3OTHER),
            self._append_to_dict(record_dict, "CATPC194", entry.CATPC194),
            self._append_to_dict(record_dict, "CATQ", entry.CATQ),
            self._append_to_dict(record_dict, "ERMA", entry.ERMB),
            self._append_to_dict(record_dict, "ERMB", entry.ERMB),
            self._append_to_dict(record_dict, "ERMT", entry.ERMT),
            self._append_to_dict(record_dict, "LNUB", entry.LNUB),
            self._append_to_dict(record_dict, "LNUC", entry.LNUC),
            self._append_to_dict(record_dict, "LSAC", entry.LSAC),
            self._append_to_dict(record_dict, "MEFA", entry.MEFA),
            self._append_to_dict(record_dict, "MPHC", entry.MPHC),
            self._append_to_dict(record_dict, "MSRA", entry.MSRA),
            self._append_to_dict(record_dict, "MSRD", entry.MSRD),
            self._append_to_dict(record_dict, "FOSA", entry.FOSA),
            self._append_to_dict(record_dict, "GYRA", entry.GYRA),
            self._append_to_dict(record_dict, "PARC", entry.PARC),
            self._append_to_dict(record_dict, "RPOBGBS_1", entry.RPOBGBS_1),
            self._append_to_dict(record_dict, "RPOBGBS_2", entry.RPOBGBS_2),
            self._append_to_dict(record_dict, "RPOBGBS_3", entry.RPOBGBS_3),
            self._append_to_dict(record_dict, "RPOBGBS_4", entry.RPOBGBS_4),
            self._append_to_dict(record_dict, "SUL2", entry.SUL2),
            self._append_to_dict(record_dict, "TETB", entry.TETB),
            self._append_to_dict(record_dict, "TETL", entry.TETL),
            self._append_to_dict(record_dict, "TETM", entry.TETM),
            self._append_to_dict(record_dict, "TETO", entry.TETO),
            self._append_to_dict(record_dict, "TETS", entry.TETS),
            self._append_to_dict(record_dict, "ALP1", entry.ALP1),
            self._append_to_dict(record_dict, "ALP23", entry.ALP23),
            self._append_to_dict(record_dict, "ALPHA", entry.ALPHA),
            self._append_to_dict(record_dict, "HVGA", entry.HVGA),
            self._append_to_dict(record_dict, "PI1", entry.PI1),
            self._append_to_dict(record_dict, "PI2A1", entry.PI2A1),
            self._append_to_dict(record_dict, "PI2A2", entry.PI2A2),
            self._append_to_dict(record_dict, "PI2B", entry.PI2B),
            self._append_to_dict(record_dict, "RIB", entry.RIB),
            self._append_to_dict(record_dict, "SRR1", entry.SRR1),
            self._append_to_dict(record_dict, "SRR2", entry.SRR2),
            self._append_to_dict(record_dict, "twenty_three_S1_variant", entry.twenty_three_S1_variant),
            self._append_to_dict(record_dict, "twenty_three_S3_variant", entry.twenty_three_S3_variant),
            self._append_to_dict(record_dict, "GYRA_variant", entry.GYRA_variant),
            self._append_to_dict(record_dict, "PARC_variant", entry.PARC_variant),
            self._append_to_dict(record_dict, "RPOBGBS_1_variant", entry.RPOBGBS_1_variant),
            self._append_to_dict(record_dict, "RPOBGBS_2_variant", entry.RPOBGBS_2_variant),
            self._append_to_dict(record_dict, "RPOBGBS_3_variant", entry.RPOBGBS_3_variant),
            self._append_to_dict(record_dict, "RPOBGBS_4_variant", entry.RPOBGBS_4_variant)

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
            self._append_to_dict(record_dict, "lane_id", entry.lane_id),
            self._append_to_dict(record_dict, "rel_abun_sa", entry.rel_abun_sa)

            response.append(record_dict)

        return response
