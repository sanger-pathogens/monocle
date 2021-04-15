from sqlalchemy import create_engine
from sqlalchemy.sql import text
from metadata.api.model.metadata import Metadata
from metadata.api.model.db_connection_config import DbConnectionConfig
from metadata.api.database.monocle_database_service import MonocleDatabaseService


class MonocleDatabaseServiceImpl(MonocleDatabaseService):
    """ DAO for metadata access """

    def __init__(self, config: DbConnectionConfig) -> None:
        self.connection_uri = config.connection_url

    def get_connection(self):
        """ Get a SQL Alchemy database connection """
        return create_engine(self.connection_uri)

    def update_sample_metadata(self, samples: dict) -> None:
        """ Update sample metadata in the database """
        pass

    def get_download_metadata(self, keys: [str]) -> [Metadata]:
        """ Get download metadata for given list of 'sample:lane' keys """

        if len(keys) == 0:
            return []

        results = []
        samples, lanes = self.split_keys(keys)
        lane_ids = tuple(lanes)

        sql = text(""" \
                    SELECT
                        sample_id,
                        lane_id,
                        serotype,
                        submitting_institution_id
                    FROM api_sample
                    WHERE
                        lane_id IN :lanes""")

        with self.get_connection().connect() as con:
            rs = con.execute(sql, lanes=lane_ids)

            for row in rs:
                results.append(
                    Metadata(
                        sanger_sample_id=row['sample_id'],
                        lane_id=row['lane_id'],
                        submitting_institution=row['submitting_institution_id'],
                        supplier_sample_name='',
                        public_name='',
                        host_status='',
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
                        serotype=row['serotype'],
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
