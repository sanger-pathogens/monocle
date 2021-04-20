from typing import Dict, List, Any

from metadata.api.model.metadata import Metadata


class ResponseHandler:
    """ Construct API response message data structures """

    def __append_to_dict(self, response_dict: {}, key: str, name: str, value: str, order: int) -> None:
        if value is None:
            value = ''

        response_dict[key] = {
                'order': order,
                'name': name,
                'value': value
            }

    def create_download_response(self, download: [Metadata]) -> List[Dict[Any, Any]]:
        """ Create the correct data structure for download responses """

        # TODO This method may need changing in future depending on the upload side
        # We could explicitly data type some of the fields, instead of just defaulting to string
        # These names could also potentially go in the config file - we'll see.

        response: List[Dict[Any, Any]] = []

        for entry in download:
            record_dict = {}
            idx = 1
            self.__append_to_dict(record_dict, "sanger_sample_id", "Sanger_Sample_ID", entry.sanger_sample_id, idx)
            idx += 1
            self.__append_to_dict(record_dict, "supplier_sample_name", "Supplier_Sample_Name", entry.supplier_sample_name, idx)
            idx += 1
            self.__append_to_dict(record_dict, "public_name", "Public_Name", entry.public_name, idx)
            idx += 1
            self.__append_to_dict(record_dict, "lane_id", "Lane_ID", entry.lane_id, idx)
            idx += 1
            self.__append_to_dict(record_dict, "study_name", "Study_Name", entry.study_name, idx)
            idx += 1
            self.__append_to_dict(record_dict, "study_ref", "Study_Reference", entry.study_ref, idx)
            idx += 1
            self.__append_to_dict(record_dict, "selection_random", "Selection_Random", entry.selection_random, idx)
            idx += 1
            self.__append_to_dict(record_dict, "country", "Country", entry.country, idx)
            idx += 1
            self.__append_to_dict(record_dict, "county_state", "County / state", entry.county_state, idx)
            idx += 1
            self.__append_to_dict(record_dict, "city", "City", entry.city, idx)
            idx += 1
            self.__append_to_dict(record_dict, "submitting_institution", "Submitting_Institution", entry.submitting_institution, idx)
            idx += 1
            self.__append_to_dict(record_dict, "collection_year", "Collection_year", entry.collection_year, idx)
            idx += 1
            self.__append_to_dict(record_dict, "collection_month", "Collection_month", entry.collection_month, idx)
            idx += 1
            self.__append_to_dict(record_dict, "collection_day", "Collection_day", entry.collection_day, idx)
            idx += 1
            self.__append_to_dict(record_dict, "host_species", "Host_species", entry.host_species, idx)
            idx += 1
            self.__append_to_dict(record_dict, "gender", "Gender", entry.gender, idx)
            idx += 1
            self.__append_to_dict(record_dict, "age_group", "Age_group", entry.age_group, idx)
            idx += 1
            self.__append_to_dict(record_dict, "age_years", "Age_years", entry.age_years, idx)
            idx += 1
            self.__append_to_dict(record_dict, "age_months", "Age_months", entry.age_months, idx)
            idx += 1
            self.__append_to_dict(record_dict, "age_weeks", "Age_weeks", entry.age_weeks, idx)
            idx += 1
            self.__append_to_dict(record_dict, "age_days", "Age_days", entry.age_days, idx)
            idx += 1
            self.__append_to_dict(record_dict, "host_status", "Host_status", entry.host_status, idx)
            idx += 1
            self.__append_to_dict(record_dict, "disease_type", "Disease_type", entry.disease_type, idx)
            idx += 1
            self.__append_to_dict(record_dict, "disease_onset", "Disease_onset", entry.disease_onset, idx)
            idx += 1
            self.__append_to_dict(record_dict, "isolation_source", "Isolation_source", entry.isolation_source, idx)
            idx += 1
            self.__append_to_dict(record_dict, "serotype", "Serotype", entry.serotype, idx)
            idx += 1
            self.__append_to_dict(record_dict, "serotype_method", "Serotype_method", entry.serotype_method, idx)
            idx += 1
            self.__append_to_dict(record_dict, "infection_during_pregnancy", "Infection_during_pregnancy", entry.infection_during_pregnancy, idx)
            idx += 1
            self.__append_to_dict(record_dict, "maternal_infection_type", "Maternal_infection_type", entry.maternal_infection_type, idx)
            idx += 1
            self.__append_to_dict(record_dict, "gestational_age_weeks", "Gestational_age_weeks", entry.gestational_age_weeks, idx)
            idx += 1
            self.__append_to_dict(record_dict, "birth_weight_gram", "Birthweight_gram", entry.birth_weight_gram, idx)
            idx += 1
            self.__append_to_dict(record_dict, "apgar_score", "Apgar_score", entry.apgar_score, idx)
            idx += 1
            self.__append_to_dict(record_dict, "ceftizoxime", "Ceftizoxime", entry.ceftizoxime, idx)
            idx += 1
            self.__append_to_dict(record_dict, "ceftizoxime_method", "Ceftizoxime_method", entry.ceftizoxime_method, idx)
            idx += 1
            self.__append_to_dict(record_dict, "cefoxitin", "Cefoxitin", entry.cefoxitin, idx)
            idx += 1
            self.__append_to_dict(record_dict, "cefoxitin_method", "Cefoxitin_method", entry.cefoxitin_method, idx)
            idx += 1
            self.__append_to_dict(record_dict, "cefotaxime", "Cefotaxime", entry.cefotaxime, idx)
            idx += 1
            self.__append_to_dict(record_dict, "cefotaxime_method", "Cefotaxime_method", entry.cefotaxime_method, idx)
            idx += 1
            self.__append_to_dict(record_dict, "cefazolin", "Cefazolin", entry.cefazolin, idx)
            idx += 1
            self.__append_to_dict(record_dict, "cefazolin_method", "Cefazolin_method", entry.cefazolin_method, idx)
            idx += 1
            self.__append_to_dict(record_dict, "ampicillin", "Ampicillin", entry.ampicillin, idx)
            idx += 1
            self.__append_to_dict(record_dict, "ampicillin_method", "Ampicillin_method", entry.ampicillin_method, idx)
            idx += 1
            self.__append_to_dict(record_dict, "penicillin", "Penicillin", entry.penicillin, idx)
            idx += 1
            self.__append_to_dict(record_dict, "penicillin_method", "Penicillin_method", entry.penicillin_method, idx)
            idx += 1
            self.__append_to_dict(record_dict, "erythromycin", "Erythromycin", entry.erythromycin, idx)
            idx += 1
            self.__append_to_dict(record_dict, "erythromycin_method", "Erythromycin_method", entry.erythromycin_method, idx)
            idx += 1
            self.__append_to_dict(record_dict, "clindamycin", "Clindamycin", entry.clindamycin, idx)
            idx += 1
            self.__append_to_dict(record_dict, "clindamycin_method", "Clindamycin_method", entry.clindamycin_method, idx)
            idx += 1
            self.__append_to_dict(record_dict, "tetracycline", "Tetracycline", entry.tetracycline, idx)
            idx += 1
            self.__append_to_dict(record_dict, "tetracycline_method", "Tetracycline_method", entry.tetracycline_method, idx)
            idx += 1
            self.__append_to_dict(record_dict, "levofloxacin", "Levofloxacin", entry.levofloxacin, idx)
            idx += 1
            self.__append_to_dict(record_dict, "levofloxacin_method", "Levofloxacin_method", entry.levofloxacin_method, idx)
            idx += 1
            self.__append_to_dict(record_dict, "ciprofloxacin", "Ciprofloxacin", entry.ciprofloxacin, idx)
            idx += 1
            self.__append_to_dict(record_dict, "ciprofloxacin_method", "Ciprofloxacin_method", entry.ciprofloxacin_method, idx)
            idx += 1
            self.__append_to_dict(record_dict, "daptomycin", "Daptomycin", entry.daptomycin, idx)
            idx += 1
            self.__append_to_dict(record_dict, "daptomycin_method", "Daptomycin_method", entry.daptomycin_method, idx)
            idx += 1
            self.__append_to_dict(record_dict, "vancomycin", "Vancomycin", entry.vancomycin, idx)
            idx += 1
            self.__append_to_dict(record_dict, "vancomycin_method", "Vancomycin_method", entry.vancomycin_method, idx)
            idx += 1
            self.__append_to_dict(record_dict, "linezolid", "Linezolid", entry.linezolid, idx)
            idx += 1
            self.__append_to_dict(record_dict, "linezolid_method", "Linezolid_method", entry.linezolid_method, idx)
            idx += 1
            self.__append_to_dict(record_dict, "additional_metadata", "Additional_metadata", entry.additional_metadata, idx)

            response.append(record_dict)
            
        return response

