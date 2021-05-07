from typing import Dict, List, Any

from metadata.api.model.metadata import Metadata
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition


class DownloadHandler:
    """ Construct API download response message data structures """

    def __init__(self, in_def: SpreadsheetDefinition) -> None:
        self.spreadsheet_def = in_def
        self.field_index = 1

    def __append_to_dict(self, response_dict: {}, key: str, value: str) -> None:
        if value is None:
            value = ''

        response_dict[key] = {
                'order': self.field_index,
                'name': self.spreadsheet_def.get_column_name(key),
                'value': value
            }

        self.field_index += 1

    def create_download_response(self, download: [Metadata]) -> List[Dict[Any, Any]]:
        """ Create the correct data structure for download responses """

        response: List[Dict[Any, Any]] = []

        for entry in download:
            record_dict = {}
            self.field_index = 1
            self.__append_to_dict(record_dict, "sanger_sample_id", entry.sanger_sample_id)
            self.__append_to_dict(record_dict, "supplier_sample_name", entry.supplier_sample_name)
            self.__append_to_dict(record_dict, "public_name", entry.public_name)
            self.__append_to_dict(record_dict, "lane_id", entry.lane_id)
            self.__append_to_dict(record_dict, "study_name", entry.study_name)
            self.__append_to_dict(record_dict, "study_ref", entry.study_ref)
            self.__append_to_dict(record_dict, "selection_random", entry.selection_random)
            self.__append_to_dict(record_dict, "country", entry.country)
            self.__append_to_dict(record_dict, "county_state", entry.county_state)
            self.__append_to_dict(record_dict, "city", entry.city)
            self.__append_to_dict(record_dict, "submitting_institution", entry.submitting_institution)
            self.__append_to_dict(record_dict, "collection_year", entry.collection_year)
            self.__append_to_dict(record_dict, "collection_month", entry.collection_month)
            self.__append_to_dict(record_dict, "collection_day", entry.collection_day)
            self.__append_to_dict(record_dict, "host_species", entry.host_species)
            self.__append_to_dict(record_dict, "gender", entry.gender)
            self.__append_to_dict(record_dict, "age_group", entry.age_group)
            self.__append_to_dict(record_dict, "age_years", entry.age_years)
            self.__append_to_dict(record_dict, "age_months", entry.age_months)
            self.__append_to_dict(record_dict, "age_weeks", entry.age_weeks)
            self.__append_to_dict(record_dict, "age_days", entry.age_days)
            self.__append_to_dict(record_dict, "host_status", entry.host_status)
            self.__append_to_dict(record_dict, "disease_type", entry.disease_type)
            self.__append_to_dict(record_dict, "disease_onset", entry.disease_onset)
            self.__append_to_dict(record_dict, "isolation_source", entry.isolation_source)
            self.__append_to_dict(record_dict, "serotype", entry.serotype)
            self.__append_to_dict(record_dict, "serotype_method", entry.serotype_method)
            self.__append_to_dict(record_dict, "infection_during_pregnancy", entry.infection_during_pregnancy)
            self.__append_to_dict(record_dict, "maternal_infection_type", entry.maternal_infection_type)
            self.__append_to_dict(record_dict, "gestational_age_weeks", entry.gestational_age_weeks)
            self.__append_to_dict(record_dict, "birth_weight_gram", entry.birth_weight_gram)
            self.__append_to_dict(record_dict, "apgar_score", entry.apgar_score)
            self.__append_to_dict(record_dict, "ceftizoxime", entry.ceftizoxime)
            self.__append_to_dict(record_dict, "ceftizoxime_method", entry.ceftizoxime_method)
            self.__append_to_dict(record_dict, "cefoxitin", entry.cefoxitin)
            self.__append_to_dict(record_dict, "cefoxitin_method", entry.cefoxitin_method)
            self.__append_to_dict(record_dict, "cefotaxime", entry.cefotaxime)
            self.__append_to_dict(record_dict, "cefotaxime_method", entry.cefotaxime_method)
            self.__append_to_dict(record_dict, "cefazolin", entry.cefazolin)
            self.__append_to_dict(record_dict, "cefazolin_method", entry.cefazolin_method)
            self.__append_to_dict(record_dict, "ampicillin", entry.ampicillin)
            self.__append_to_dict(record_dict, "ampicillin_method", entry.ampicillin_method)
            self.__append_to_dict(record_dict, "penicillin", entry.penicillin)
            self.__append_to_dict(record_dict, "penicillin_method", entry.penicillin_method)
            self.__append_to_dict(record_dict, "erythromycin", entry.erythromycin)
            self.__append_to_dict(record_dict, "erythromycin_method", entry.erythromycin_method)
            self.__append_to_dict(record_dict, "clindamycin", entry.clindamycin)
            self.__append_to_dict(record_dict, "clindamycin_method", entry.clindamycin_method)
            self.__append_to_dict(record_dict, "tetracycline", entry.tetracycline)
            self.__append_to_dict(record_dict, "tetracycline_method", entry.tetracycline_method)
            self.__append_to_dict(record_dict, "levofloxacin", entry.levofloxacin)
            self.__append_to_dict(record_dict, "levofloxacin_method", entry.levofloxacin_method)
            self.__append_to_dict(record_dict, "ciprofloxacin", entry.ciprofloxacin)
            self.__append_to_dict(record_dict, "ciprofloxacin_method", entry.ciprofloxacin_method)
            self.__append_to_dict(record_dict, "daptomycin", entry.daptomycin)
            self.__append_to_dict(record_dict, "daptomycin_method", entry.daptomycin_method)
            self.__append_to_dict(record_dict, "vancomycin", entry.vancomycin)
            self.__append_to_dict(record_dict, "vancomycin_method", entry.vancomycin_method)
            self.__append_to_dict(record_dict, "linezolid", entry.linezolid)
            self.__append_to_dict(record_dict, "linezolid_method", entry.linezolid_method)
            self.__append_to_dict(record_dict, "additional_metadata", entry.additional_metadata)

            response.append(record_dict)
            
        return response

