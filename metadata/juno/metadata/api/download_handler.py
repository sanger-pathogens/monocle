from typing import Dict, List, Any

from metadata.api.model.metadata import Metadata
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition
from metadata.api.database.monocle_database_service import MonocleDatabaseService


class DownloadHandler:
    """ Construct API download response message data structures """

    def __init__(self, dao: MonocleDatabaseService, in_def: SpreadsheetDefinition) -> None:
        self.__dao = dao
        self.__spreadsheet_def = in_def
        self.__field_index = 1

    def _append_to_dict(self, response_dict: {}, key: str, value: str) -> None:
        if value is None:
            value = ''

        response_dict[key] = {
                'order': self.__field_index,
                'name': self.__spreadsheet_def.get_column_name(key),
                'value': value
            }

        self.__field_index += 1

    def read_download_metadata(self, keys: List[str]) -> List[Metadata]:
        """
            Return a list of metadata objects that correspond to the given sample id/lane id key values.
        """
        return self.__dao.get_download_metadata(keys)

    def create_download_response(self, download: [Metadata]) -> List[Dict[Any, Any]]:
        """ Create the correct data structure for download responses """

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

