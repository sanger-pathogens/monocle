import logging
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from metadata.api.model.metadata import Metadata
from metadata.api.model.institution import Institution
from metadata.api.model.db_connection_config import DbConnectionConfig
from metadata.api.database.monocle_database_service import MonocleDatabaseService

logger = logging.getLogger()


class MonocleDatabaseServiceImpl(MonocleDatabaseService):
    """ DAO for metadata access """

    DELETE_ALL_SAMPLES_SQL = text("""delete from api_sample""")

    INSERT_SAMPLE_SQL = text(""" \
            insert into api_sample (
                sample_id, lane_id, supplier_sample_name, public_name, host_status, serotype, submitting_institution_id,
                additional_metadata, age_days, age_group, age_months, age_weeks, age_years, ampicillin,
                ampicillin_method, apgar_score, birthweight_gram, cefazolin, cefazolin_method, cefotaxime,
                cefotaxime_method, cefoxitin, cefoxitin_method, ceftizoxime, ceftizoxime_method,
                ciprofloxacin, ciprofloxacin_method, city, clindamycin, clindamycin_method, collection_day,
                collection_month, collection_year, country, county_state, daptomycin, daptomycin_method, disease_onset,
                disease_type, erythromycin, erythromycin_method, gender, gestational_age_weeks,
                host_species, infection_during_pregnancy, isolation_source, levofloxacin, levofloxacin_method,
                linezolid, linezolid_method, maternal_infection_type, penicillin, penicillin_method,
                selection_random, serotype_method, study_name, study_ref, tetracycline, tetracycline_method,
                vancomycin, vancomycin_method
            ) values (
                :sample_id, :lane_id, :supplier_sample_name, :public_name, :host_status, :serotype, :submitting_institution_id,
                :additional_metadata, :age_days, :age_group, :age_months, :age_weeks, :age_years, :ampicillin,
                :ampicillin_method, :apgar_score, :birthweight_gram, :cefazolin, :cefazolin_method, :cefotaxime,
                :cefotaxime_method, :cefoxitin, :cefoxitin_method, :ceftizoxime, :ceftizoxime_method,
                :ciprofloxacin, :ciprofloxacin_method, :city, :clindamycin, :clindamycin_method, :collection_day,
                :collection_month, :collection_year, :country, :county_state, :daptomycin, :daptomycin_method, :disease_onset,
                :disease_type, :erythromycin, :erythromycin_method, :gender, :gestational_age_weeks,
                :host_species, :infection_during_pregnancy, :isolation_source, :levofloxacin, :levofloxacin_method,
                :linezolid, :linezolid_method, :maternal_infection_type, :penicillin, :penicillin_method,
                :selection_random, :serotype_method, :study_name, :study_ref, :tetracycline, :tetracycline_method,
                :vancomycin, :vancomycin_method
            )""")

    SELECT_LANES_SQL = text(""" \
            SELECT
                sample_id, lane_id, supplier_sample_name, public_name, host_status, serotype, submitting_institution_id,
                additional_metadata, age_days, age_group, age_months, age_weeks, age_years, ampicillin,
                ampicillin_method, apgar_score, birthweight_gram, cefazolin, cefazolin_method, cefotaxime,
                cefotaxime_method, cefoxitin, cefoxitin_method, ceftizoxime, ceftizoxime_method,
                ciprofloxacin, ciprofloxacin_method, city, clindamycin, clindamycin_method, collection_day,
                collection_month, collection_year, country, county_state, daptomycin, daptomycin_method, disease_onset,
                disease_type, erythromycin, erythromycin_method, gender, gestational_age_weeks,
                host_species, infection_during_pregnancy, isolation_source, levofloxacin, levofloxacin_method,
                linezolid, linezolid_method, maternal_infection_type, penicillin, penicillin_method,
                selection_random, serotype_method, study_name, study_ref, tetracycline, tetracycline_method,
                vancomycin, vancomycin_method
            FROM api_sample
            WHERE
                lane_id IN :lanes""")

    SELECT_INSTITUTIONS_SQL = text(""" \
                SELECT name, country, latitude, longitude
                FROM api_institution
                ORDER BY name""")

    def __init__(self, config: DbConnectionConfig) -> None:
        self.connection_uri = config.connection_url

    def get_connection(self):
        """ Get a SQL Alchemy database connection """
        return create_engine(self.connection_uri)

    def get_institutions(self) -> List[Institution]:
        """ Return a list of allowed institutions """
        results = []
        with self.get_connection().connect() as con:
            rs = con.execute(self.SELECT_INSTITUTIONS_SQL)

            for row in rs:
                results.append(
                    Institution(row['name'], row['country'], row['latitude'], row['longitude'])
                )

        return results

    def update_sample_metadata(self, metadata_list: List[Metadata]) -> None:
        """ Update sample metadata in the database """

        with self.get_connection().connect() as con:
            with con.begin():
                con.execute(self.DELETE_ALL_SAMPLES_SQL)

                for metadata in metadata_list:
                    con.execute(
                        self.INSERT_SAMPLE_SQL,
                        sample_id=metadata.sanger_sample_id,
                        lane_id=metadata.lane_id,
                        supplier_sample_name=metadata.supplier_sample_name,
                        public_name=metadata.public_name,
                        host_status=metadata.host_status,
                        serotype=metadata.serotype,
                        submitting_institution_id=metadata.submitting_institution,
                        additional_metadata=metadata.additional_metadata,
                        age_days=metadata.age_days,
                        age_group=metadata.age_group,
                        age_months=metadata.age_months,
                        age_weeks=metadata.age_weeks,
                        age_years=metadata.age_years,
                        ampicillin=metadata.ampicillin,
                        ampicillin_method=metadata.ampicillin_method,
                        apgar_score=metadata.apgar_score,
                        birthweight_gram=metadata.birth_weight_gram,
                        cefazolin=metadata.cefazolin,
                        cefazolin_method=metadata.cefazolin_method,
                        cefotaxime=metadata.cefotaxime,
                        cefotaxime_method=metadata.cefotaxime_method,
                        cefoxitin=metadata.cefoxitin,
                        cefoxitin_method=metadata.cefoxitin_method,
                        ceftizoxime=metadata.ceftizoxime,
                        ceftizoxime_method=metadata.ceftizoxime_method,
                        ciprofloxacin=metadata.ciprofloxacin,
                        ciprofloxacin_method=metadata.ciprofloxacin_method,
                        city=metadata.city,
                        clindamycin=metadata.clindamycin,
                        clindamycin_method=metadata.clindamycin_method,
                        collection_day=metadata.collection_day,
                        collection_month=metadata.collection_month,
                        collection_year=metadata.collection_year,
                        country=metadata.country,
                        county_state=metadata.county_state,
                        daptomycin=metadata.daptomycin,
                        daptomycin_method=metadata.daptomycin_method,
                        disease_onset=metadata.disease_onset,
                        disease_type=metadata.disease_type,
                        erythromycin=metadata.erythromycin,
                        erythromycin_method=metadata.erythromycin_method,
                        gender=metadata.gender,
                        gestational_age_weeks=metadata.gestational_age_weeks,
                        host_species=metadata.host_species,
                        infection_during_pregnancy=metadata.infection_during_pregnancy,
                        isolation_source=metadata.isolation_source,
                        levofloxacin=metadata.levofloxacin,
                        levofloxacin_method=metadata.levofloxacin_method,
                        linezolid=metadata.linezolid,
                        linezolid_method=metadata.linezolid_method,
                        maternal_infection_type=metadata.maternal_infection_type,
                        penicillin=metadata.penicillin,
                        penicillin_method=metadata.penicillin_method,
                        selection_random=metadata.selection_random,
                        serotype_method=metadata.serotype_method,
                        study_name=metadata.study_name,
                        study_ref=metadata.study_ref,
                        tetracycline=metadata.tetracycline,
                        tetracycline_method=metadata.tetracycline_method,
                        vancomycin=metadata.vancomycin,
                        vancomycin_method=metadata.vancomycin_method
                    )

    def get_download_metadata(self, keys: List[str]) -> List[Metadata]:
        """ Get download metadata for given list of 'sample:lane' keys """

        if len(keys) == 0:
            return []

        results = []
        samples, lanes = self.split_keys(keys)
        lane_ids = tuple(lanes)

        with self.get_connection().connect() as con:
            rs = con.execute(self.SELECT_LANES_SQL, lanes=lane_ids)

            for row in rs:
                results.append(
                    Metadata(
                        sanger_sample_id=row['sample_id'],
                        lane_id=row['lane_id'],
                        submitting_institution=row['submitting_institution_id'],
                        supplier_sample_name=row['supplier_sample_name'],
                        public_name=row['public_name'],
                        host_status=row['host_status'],
                        study_name=row['study_name'],
                        study_ref=row['study_ref'],
                        selection_random=row['selection_random'],
                        country=row['country'],
                        county_state=row['county_state'],
                        city=row['city'],
                        collection_year=row['collection_year'],
                        collection_month=row['collection_month'],
                        collection_day=row['collection_day'],
                        host_species=row['host_species'],
                        gender=row['gender'],
                        age_group=row['age_group'],
                        age_years=row['age_years'],
                        age_months=row['age_years'],
                        age_weeks=row['age_weeks'],
                        age_days=row['age_days'],
                        disease_type=row['disease_type'],
                        disease_onset=row['disease_onset'],
                        isolation_source=row['isolation_source'],
                        serotype=row['serotype'],
                        serotype_method=row['serotype_method'],
                        infection_during_pregnancy=row['infection_during_pregnancy'],
                        maternal_infection_type=row['maternal_infection_type'],
                        gestational_age_weeks=row['gestational_age_weeks'],
                        birth_weight_gram=row['birthweight_gram'],
                        apgar_score=row['apgar_score'],
                        ceftizoxime=row['ceftizoxime'],
                        ceftizoxime_method=row['ceftizoxime_method'],
                        cefoxitin=row['cefoxitin'],
                        cefoxitin_method=row['cefoxitin_method'],
                        cefotaxime=row['cefotaxime'],
                        cefotaxime_method=row['cefotaxime_method'],
                        cefazolin=row['cefazolin'],
                        cefazolin_method=row['cefazolin_method'],
                        ampicillin=row['ampicillin'],
                        ampicillin_method=row['ampicillin_method'],
                        penicillin=row['penicillin'],
                        penicillin_method=row['penicillin_method'],
                        erythromycin=row['erythromycin'],
                        erythromycin_method=row['erythromycin_method'],
                        clindamycin=row['clindamycin'],
                        clindamycin_method=row['clindamycin_method'],
                        tetracycline=row['tetracycline'],
                        tetracycline_method=row['tetracycline_method'],
                        levofloxacin=row['levofloxacin'],
                        levofloxacin_method=row['levofloxacin_method'],
                        ciprofloxacin=row['ciprofloxacin'],
                        ciprofloxacin_method=row['ciprofloxacin_method'],
                        daptomycin=row['daptomycin'],
                        daptomycin_method=row['daptomycin_method'],
                        vancomycin=row['vancomycin'],
                        vancomycin_method=row['vancomycin_method'],
                        linezolid=row['linezolid'],
                        linezolid_method=row['linezolid_method'],
                        additional_metadata=row['additional_metadata']
                    )
                )

        return results
