from typing import List
from metadata.api.model.metadata import Metadata
from metadata.api.model.db_connection_config import DbConnectionConfig
from metadata.api.database.monocle_database_service import MonocleDatabaseService
from metadata.api.model.institution import Institution


class MonocleDatabaseServiceNoOpImpl(MonocleDatabaseService):
    """ A dummy implementation for end to end testing """

    def __init__(self, config: DbConnectionConfig) -> None:
        pass

    def get_connection(self) -> None:
        pass

    def get_institutions(self) -> List[Institution]:
        """ Return a list of institutions """
        results = [
            Institution('UniversityA', 'United Kingdom', 0, 0),
            Institution('UniversityB', 'France', 0, 0),
            Institution('UniversityC', 'Germany', 0, 0),
            Institution('UniversityD', 'Italy', 0, 0)
        ]

        return results

    def update_sample_metadata(self, metadata_list: List[Metadata]) -> None:
        """ Update sample metadata in the database """
        pass

    def get_download_metadata(self, keys: List[str]) -> List[Metadata]:
        """ Get download mock metadata for given list of 'sample:lane' keys """

        results = []
        samples, lanes = self.split_keys(keys)

        for sample_id, lane_id in zip(samples, lanes):

            results.append(
                Metadata(
                    sanger_sample_id=sample_id,
                    lane_id=lane_id,
                    submitting_institution='My institution',
                    supplier_sample_name='CUHK_GBS2WT_00',
                    public_name='JN_HK_GBS2WT',
                    host_status='Invasive',
                    study_name='',
                    study_ref='',
                    selection_random='',
                    country='',
                    county_state='',
                    city='',
                    collection_year='',
                    collection_month='',
                    collection_day='',
                    host_species='',
                    gender='',
                    age_group='',
                    age_years='',
                    age_months='',
                    age_weeks='',
                    age_days='',
                    disease_type='',
                    disease_onset='',
                    isolation_source='',
                    serotype='III',
                    serotype_method='',
                    infection_during_pregnancy='',
                    maternal_infection_type='',
                    gestational_age_weeks='',
                    birth_weight_gram='',
                    apgar_score='',
                    ceftizoxime='',
                    ceftizoxime_method='',
                    cefoxitin='',
                    cefoxitin_method='',
                    cefotaxime='',
                    cefotaxime_method='',
                    cefazolin='',
                    cefazolin_method='',
                    ampicillin='',
                    ampicillin_method='',
                    penicillin='',
                    penicillin_method='',
                    erythromycin='',
                    erythromycin_method='',
                    clindamycin='',
                    clindamycin_method='',
                    tetracycline='',
                    tetracycline_method='',
                    levofloxacin='',
                    levofloxacin_method='',
                    ciprofloxacin='',
                    ciprofloxacin_method='',
                    daptomycin='',
                    daptomycin_method='',
                    vancomycin='',
                    vancomycin_method='',
                    linezolid='',
                    linezolid_method='',
                    additional_metadata=''
                )
            )

        return results

