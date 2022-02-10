import logging
import json
import urllib.parse
import urllib.request
from flask import request
from typing import List, Dict
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
from metadata.api.model.metadata import Metadata
from metadata.api.model.in_silico_data import InSilicoData
from metadata.api.model.qc_data import QCData
from metadata.api.model.institution import Institution
from metadata.api.model.db_connection_config import DbConnectionConfig
from metadata.api.database.monocle_database_service import MonocleDatabaseService

logger = logging.getLogger()

class ProtocolError(Exception):
    pass

class Connector:
    """ Provide SQL Alchemy connections """
    def __init__(self, config: DbConnectionConfig) -> None:
        self.connection_url = config.connection_url
        self.engine = create_engine(self.connection_url)

    def get_connection(self) -> object:
        """ Get a SQL Alchemy database connection """
        return self.engine.connect()

    def get_transactional_connection(self) -> object:
        """ Get a SQL Alchemy transactional database connection """
        return self.engine.begin()


class MonocleDatabaseServiceImpl(MonocleDatabaseService):
    """ DAO for metadata,in silico data and QC data access """

    DASHBOARD_API_ENDPOINT = "http://dash-api:5000/dashboard-api/get_user_details"
    DASHBOARD_API_SWAGGER = "http://dash-api:5000/dashboard-api/ui/"

    DELETE_ALL_SAMPLES_SQL = text("""delete from api_sample""")

    INSERT_OR_UPDATE_SAMPLE_SQL = text(""" \
            INSERT INTO api_sample (
                sanger_sample_id, lane_id, supplier_sample_name, public_name, host_status, serotype, submitting_institution,
                age_days, age_group, age_months, age_weeks, age_years, ampicillin,
                ampicillin_method, apgar_score, birth_weight_gram, cefazolin, cefazolin_method, cefotaxime,
                cefotaxime_method, cefoxitin, cefoxitin_method, ceftizoxime, ceftizoxime_method,
                ciprofloxacin, ciprofloxacin_method, city, clindamycin, clindamycin_method, collection_day,
                collection_month, collection_year, country, county_state, daptomycin, daptomycin_method, disease_onset,
                disease_type, erythromycin, erythromycin_method, gender, gestational_age_weeks,
                host_species, infection_during_pregnancy, isolation_source, levofloxacin, levofloxacin_method,
                linezolid, linezolid_method, maternal_infection_type, penicillin, penicillin_method,
                selection_random, serotype_method, study_name, study_ref, tetracycline, tetracycline_method,
                vancomycin, vancomycin_method
            ) VALUES (
                :sanger_sample_id, :lane_id, :supplier_sample_name, :public_name, :host_status, :serotype, :submitting_institution,
                :age_days, :age_group, :age_months, :age_weeks, :age_years, :ampicillin,
                :ampicillin_method, :apgar_score, :birth_weight_gram, :cefazolin, :cefazolin_method, :cefotaxime,
                :cefotaxime_method, :cefoxitin, :cefoxitin_method, :ceftizoxime, :ceftizoxime_method,
                :ciprofloxacin, :ciprofloxacin_method, :city, :clindamycin, :clindamycin_method, :collection_day,
                :collection_month, :collection_year, :country, :county_state, :daptomycin, :daptomycin_method, :disease_onset,
                :disease_type, :erythromycin, :erythromycin_method, :gender, :gestational_age_weeks,
                :host_species, :infection_during_pregnancy, :isolation_source, :levofloxacin, :levofloxacin_method,
                :linezolid, :linezolid_method, :maternal_infection_type, :penicillin, :penicillin_method,
                :selection_random, :serotype_method, :study_name, :study_ref, :tetracycline, :tetracycline_method,
                :vancomycin, :vancomycin_method
            ) ON DUPLICATE KEY UPDATE
                lane_id = :lane_id,
                supplier_sample_name = :supplier_sample_name,
                public_name = :public_name,
                host_status = :host_status,
                serotype = :serotype,
                submitting_institution = :submitting_institution,
                age_days = :age_days,
                age_group = :age_group,
                age_months = :age_months,
                age_weeks = :age_weeks,
                age_years = :age_years,
                ampicillin = :ampicillin,
                ampicillin_method = :ampicillin_method,
                apgar_score = :apgar_score,
                birth_weight_gram = :birth_weight_gram,
                cefazolin = :cefazolin,
                cefazolin_method = :cefazolin_method,
                cefotaxime = :cefotaxime,
                cefotaxime_method = :cefotaxime_method,
                cefoxitin = :cefoxitin,
                cefoxitin_method = :cefoxitin_method,
                ceftizoxime = :ceftizoxime,
                ceftizoxime_method = :ceftizoxime_method,
                ciprofloxacin = :ciprofloxacin,
                ciprofloxacin_method = :ciprofloxacin_method,
                city = :city,
                clindamycin = :clindamycin,
                clindamycin_method = :clindamycin_method,
                collection_day = :collection_day,
                collection_month = :collection_month,
                collection_year = :collection_year,
                country = :country,
                county_state = :county_state,
                daptomycin = :daptomycin,
                daptomycin_method = :daptomycin_method,
                disease_onset = :disease_onset,
                disease_type = :disease_type,
                erythromycin = :erythromycin,
                erythromycin_method = :erythromycin_method,
                gender = :gender,
                gestational_age_weeks = :gestational_age_weeks,
                host_species = :host_species,
                infection_during_pregnancy = :infection_during_pregnancy,
                isolation_source = :isolation_source,
                levofloxacin = :levofloxacin,
                levofloxacin_method = :levofloxacin_method,
                linezolid = :linezolid,
                linezolid_method = :linezolid_method,
                maternal_infection_type = :maternal_infection_type,
                penicillin = :penicillin,
                penicillin_method = :penicillin_method,
                selection_random = :selection_random,
                serotype_method = :serotype_method,
                study_name = :study_name,
                study_ref = :study_ref,
                tetracycline = :tetracycline,
                tetracycline_method = :tetracycline_method,
                vancomycin = :vancomycin,
                vancomycin_method = :vancomycin_method
            """)

    SELECT_SAMPLES_SQL = text(""" \
            SELECT
                sanger_sample_id, lane_id, supplier_sample_name, public_name, host_status, serotype, submitting_institution,
                age_days, age_group, age_months, age_weeks, age_years, ampicillin,
                ampicillin_method, apgar_score, birth_weight_gram, cefazolin, cefazolin_method, cefotaxime,
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
                sanger_sample_id IN :samples""")

    SELECT_INSTITUTIONS_SQL = text(""" \
                SELECT name, country, latitude, longitude
                FROM api_institution
                ORDER BY name""")

    SELECT_INSTITUTION_NAMES_SQL = text(""" \
                SELECT name
                FROM api_institution
                ORDER BY name""")

    SELECT_ALL_SAMPLES_SQL = text(""" \
                SELECT sanger_sample_id, lane_id, supplier_sample_name, public_name, host_status, serotype, submitting_institution,
                age_days, age_group, age_months, age_weeks, age_years, ampicillin,
                ampicillin_method, apgar_score, birth_weight_gram, cefazolin, cefazolin_method, cefotaxime,
                cefotaxime_method, cefoxitin, cefoxitin_method, ceftizoxime, ceftizoxime_method,
                ciprofloxacin, ciprofloxacin_method, city, clindamycin, clindamycin_method, collection_day,
                collection_month, collection_year, country, county_state, daptomycin, daptomycin_method, disease_onset,
                disease_type, erythromycin, erythromycin_method, gender, gestational_age_weeks,
                host_species, infection_during_pregnancy, isolation_source, levofloxacin, levofloxacin_method,
                linezolid, linezolid_method, maternal_infection_type, penicillin, penicillin_method,
                selection_random, serotype_method, study_name, study_ref, tetracycline, tetracycline_method,
                vancomycin, vancomycin_method
                FROM api_sample
                ORDER BY sanger_sample_id""")

    SELECT_ALL_IN_SILICO_SQL = text(""" \
                SELECT lane_id, cps_type, ST, adhP, pheS, atr, glnA, sdhA, glcK, tkt, twenty_three_S1, twenty_three_S3, AAC6APH2, AADECC, ANT6, APH3III, APH3OTHER,
                CATPC194, CATQ, ERMA, ERMB, ERMT, LNUB, LNUC, LSAC, MEFA, MPHC, MSRA, MSRD, FOSA, GYRA, PARC, RPOBGBS_1, RPOBGBS_2, RPOBGBS_3, RPOBGBS_4,
                SUL2, TETB, TETL, TETM, TETO, TETS, ALP1, ALP23, ALPHA, HVGA, PI1, PI2A1, PI2A2, PI2B, RIB, SRR1, SRR2, twenty_three_S1_variant,
                twenty_three_S3_variant, GYRA_variant, PARC_variant, RPOBGBS_1_variant, RPOBGBS_2_variant, RPOBGBS_3_variant, RPOBGBS_4_variant
                FROM in_silico
                ORDER BY lane_id""")
    
    FILTER_SAMPLES_IN_SQL = """ \
            SELECT sanger_sample_id, lane_id, supplier_sample_name, public_name, host_status, serotype, submitting_institution,
            age_days, age_group, age_months, age_weeks, age_years, ampicillin,
            ampicillin_method, apgar_score, birth_weight_gram, cefazolin, cefazolin_method, cefotaxime,
            cefotaxime_method, cefoxitin, cefoxitin_method, ceftizoxime, ceftizoxime_method,
            ciprofloxacin, ciprofloxacin_method, city, clindamycin, clindamycin_method, collection_day,
            collection_month, collection_year, country, county_state, daptomycin, daptomycin_method, disease_onset,
            disease_type, erythromycin, erythromycin_method, gender, gestational_age_weeks,
            host_species, infection_during_pregnancy, isolation_source, levofloxacin, levofloxacin_method,
            linezolid, linezolid_method, maternal_infection_type, penicillin, penicillin_method,
            selection_random, serotype_method, study_name, study_ref, tetracycline, tetracycline_method,
            vancomycin, vancomycin_method
            FROM api_sample
            WHERE {} IN :values"""

    IN_SILICO_FILTER_LANES_IN_SQL = """ \
            SELECT lane_id, cps_type, ST, adhP, pheS, atr, glnA, sdhA, glcK, tkt, twenty_three_S1, twenty_three_S3, AAC6APH2, AADECC, ANT6, APH3III, APH3OTHER,
            CATPC194, CATQ, ERMA, ERMB, ERMT, LNUB, LNUC, LSAC, MEFA, MPHC, MSRA, MSRD, FOSA, GYRA, PARC, RPOBGBS_1, RPOBGBS_2, RPOBGBS_3, RPOBGBS_4,
            SUL2, TETB, TETL, TETM, TETO, TETS, ALP1, ALP23, ALPHA, HVGA, PI1, PI2A1, PI2A2, PI2B, RIB, SRR1, SRR2, twenty_three_S1_variant,
            twenty_three_S3_variant, GYRA_variant, PARC_variant, RPOBGBS_1_variant, RPOBGBS_2_variant, RPOBGBS_3_variant, RPOBGBS_4_variant
            FROM in_silico
            WHERE {} IN :values"""

    #DISTINCT_FIELD_VALUES_SQL = text(""" \
            #SELECT DISTINCT :field FROM api_sample WHERE submitting_institution IN :institutions""")
    DISTINCT_FIELD_VALUES_SQL = """ \
            SELECT DISTINCT {} FROM api_sample WHERE submitting_institution IN :institutions"""

    DISTINCT_IN_SILICO_FIELD_VALUES_SQL = """ \
            SELECT DISTINCT {} FROM in_silico"""

    DISTINCT_QC_DATA_FIELD_VALUES_SQL = """ \
            SELECT DISTINCT {} FROM qc_data"""

    INSERT_OR_UPDATE_IN_SILICO_SQL = text(""" \
            INSERT INTO in_silico (
                lane_id, cps_type, ST, adhP, pheS, atr, glnA, sdhA, glcK, tkt, twenty_three_S1, twenty_three_S3, AAC6APH2, AADECC, ANT6, APH3III, APH3OTHER,
                CATPC194, CATQ, ERMA, ERMB, ERMT, LNUB, LNUC, LSAC, MEFA, MPHC, MSRA, MSRD, FOSA, GYRA, PARC, RPOBGBS_1, RPOBGBS_2, RPOBGBS_3, RPOBGBS_4,
                SUL2, TETB, TETL, TETM, TETO, TETS, ALP1, ALP23, ALPHA, HVGA, PI1, PI2A1, PI2A2, PI2B, RIB, SRR1, SRR2, twenty_three_S1_variant,
                twenty_three_S3_variant, GYRA_variant, PARC_variant, RPOBGBS_1_variant, RPOBGBS_2_variant, RPOBGBS_3_variant, RPOBGBS_4_variant
            ) VALUES (
                :lane_id, :cps_type, :ST, :adhP, :pheS, :atr, :glnA, :sdhA, :glcK, :tkt, :twenty_three_S1, :twenty_three_S3, :AAC6APH2, :AADECC, :ANT6, :APH3III, :APH3OTHER,
                :CATPC194, :CATQ, :ERMA, :ERMB, :ERMT, :LNUB, :LNUC, :LSAC, :MEFA, :MPHC, :MSRA, :MSRD, :FOSA, :GYRA, :PARC, :RPOBGBS_1, :RPOBGBS_2, :RPOBGBS_3, :RPOBGBS_4,
                :SUL2, :TETB, :TETL, :TETM, :TETO, :TETS, :ALP1, :ALP23, :ALPHA, :HVGA, :PI1, :PI2A1, :PI2A2, :PI2B, :RIB, :SRR1, :SRR2, :twenty_three_S1_variant,
                :twenty_three_S3_variant, :GYRA_variant, :PARC_variant, :RPOBGBS_1_variant, :RPOBGBS_2_variant, :RPOBGBS_3_variant, :RPOBGBS_4_variant
            ) ON DUPLICATE KEY UPDATE
                lane_id = :lane_id,
                cps_type = :cps_type,
                ST = :ST,
                adhP = :adhP,
                pheS = :pheS,
                atr = :atr,
                glnA = :glnA,
                sdhA = :sdhA,
                glcK = :glcK,
                tkt = :tkt,
                twenty_three_S1 = :twenty_three_S1,
                twenty_three_S3 = :twenty_three_S3,
                AAC6APH2 = :AAC6APH2,
                AADECC = :AADECC,
                ANT6 = :ANT6,
                APH3III = :APH3III,
                APH3OTHER = :APH3OTHER,
                CATPC194 = :CATPC194,
                CATQ = :CATQ,
                ERMA = :ERMA,
                ERMB = :ERMB,
                ERMT = :ERMT,
                LNUB = :LNUB,
                LNUC = :LNUC,
                LSAC = :LSAC,
                MEFA = :MEFA,
                MPHC = :MPHC,
                MSRA = :MSRA,
                MSRD = :MSRD,
                FOSA = :FOSA,
                GYRA = :GYRA,
                PARC = :PARC,
                RPOBGBS_1 = :RPOBGBS_1,
                RPOBGBS_2 = :RPOBGBS_2,
                RPOBGBS_3 = :RPOBGBS_3,
                RPOBGBS_4 = :RPOBGBS_4,
                SUL2 = :SUL2,
                TETB = :TETB,
                TETL = :TETL,
                TETM = :TETM,
                TETO = :TETO,
                TETS = :TETS,
                ALP1 = :ALP1,
                ALP23 = :ALP23,
                ALPHA = :ALPHA,
                HVGA = :HVGA,
                PI1 = :PI1,
                PI2A1 = :PI2A1,
                PI2A2 = :PI2A2,
                PI2B = :PI2B,
                RIB = :RIB,
                SRR1 = :SRR1,
                SRR2 = :SRR2,
                twenty_three_S1_variant = :twenty_three_S1_variant,
                twenty_three_S3_variant = :twenty_three_S3_variant,
                GYRA_variant = :GYRA_variant,
                PARC_variant = :PARC_variant,
                RPOBGBS_1_variant = :RPOBGBS_1_variant,
                RPOBGBS_2_variant = :RPOBGBS_2_variant,
                RPOBGBS_3_variant = :RPOBGBS_3_variant,
                RPOBGBS_4_variant = :RPOBGBS_4_variant
            """)

    SELECT_LANES_IN_SILICO_SQL = text(""" \
            SELECT
                lane_id, cps_type, ST, adhP, pheS, atr, glnA, sdhA, glcK, tkt, twenty_three_S1, twenty_three_S3, AAC6APH2, AADECC, ANT6, APH3III, APH3OTHER,
                CATPC194, CATQ, ERMA, ERMB, ERMT, LNUB, LNUC, LSAC, MEFA, MPHC, MSRA, MSRD, FOSA, GYRA, PARC, RPOBGBS_1, RPOBGBS_2, RPOBGBS_3, RPOBGBS_4,
                SUL2, TETB, TETL, TETM, TETO, TETS, ALP1, ALP23, ALPHA, HVGA, PI1, PI2A1, PI2A2, PI2B, RIB, SRR1, SRR2, twenty_three_S1_variant,
                twenty_three_S3_variant, GYRA_variant, PARC_variant, RPOBGBS_1_variant, RPOBGBS_2_variant, RPOBGBS_3_variant, RPOBGBS_4_variant
            FROM in_silico
            WHERE
                lane_id IN :lanes""")

    DELETE_ALL_QC_DATA_SQL = text("""delete from qc_data""")
    
    INSERT_OR_UPDATE_QC_DATA_SQL = text(""" \
            INSERT INTO qc_data (
                lane_id, rel_abun_sa
            ) VALUES (
                :lane_id, :rel_abun_sa
            ) ON DUPLICATE KEY UPDATE
                lane_id = :lane_id,
                rel_abun_sa = :rel_abun_sa
            """)
    
    SELECT_LANES_QC_DATA_SQL = text(""" \
            SELECT
                lane_id, rel_abun_sa
            FROM qc_data
            WHERE
                lane_id IN :lanes""")

    def __init__(self, connector: Connector) -> None:
        self.connector = connector


    def get_authenticated_username(self, req_obj: request):
        # TODO: Make this a separate service
        """ Return the request authenticated user name """
        username = None
        try:
            username = req_obj.headers['X-Remote-User']
            logging.info('X-Remote-User header = {}'.format(username))
        except KeyError:
            pass

        return username

    def convert_string(self, val: str) -> str:
        """ If a given string is empty return None """
        return val if val else None

    def convert_int(self, val: str) -> int:
        """ If a given string is empty then return None else try to convert to int """
        if not val:
            return None

        try:
            int_val = int(val)
        except ValueError:
            logger.error("ERROR: Expected value {} to be an int!".format(val))
            raise

        return int_val

    def make_request(self, endpoint, request_headers, post_data=None):
        request_url       = endpoint
        request_data      = None
        # if POST data were passed, convert to a UTF-8 JSON string
        if post_data is not None:
            assert ( isinstance(post_data, dict) or isinstance(post_data, list) ), "{}.make_request() requires post_data as a dict or a list, not {}".format(__class__.__name__,post_data)
            request_data = str(json.dumps(post_data))
            logging.debug("POST data for Monocle Download API: {}".format(request_data))
            request_data = request_data.encode('utf-8')
        try:
            logging.info("request to Monocle Download: {}".format(request_url))
            http_request = urllib.request.Request(request_url, data = request_data, headers = request_headers)
            with urllib.request.urlopen( http_request ) as this_response:
                response_as_string = this_response.read().decode('utf-8')
                logging.debug("response from Monocle Download: {}".format(response_as_string))
        except urllib.error.HTTPError as e:
            if 404 == e.code:
                logging.info("HTTP response status {} (no data found) during Monocle Download request {}".format(e.code,request_url))
            else:
                logging.error("HTTP status {} during Monocle Download request {}".format(e.code,request_url))
            raise
        return response_as_string

    def parse_response(self, response_as_string, required_keys=[]):
        results_data = json.loads(response_as_string)
        if not isinstance(results_data, dict):
            error_message = "request to '{}' did not return a dict as expected (see API documentation at {})".format(self.DASHBOARD_API_ENDPOINT, self.DASHBOARD_API_SWAGGER)
            raise ProtocolError(error_message)
        for required_key in required_keys:
            try:
                results_data[required_key]
            except KeyError:
                error_message = "response data did not contain the expected key '{}' (see API documentation at {})".format(self.DASHBOARD_API_ENDPOINT, self.DASHBOARD_API_SWAGGER)
                raise ProtocolError(error_message)
        return results_data

    def get_institutions(self, username) -> List[Institution]:
        """ Return a list of allowed institutions """
        endpoint = self.DASHBOARD_API_ENDPOINT
        request_headers = {'Content-type': 'application/json;charset=utf-8', 'X-Remote-User': username}
        logging.debug("{}.get_institutions() using endpoint {} for username {}".format(__class__.__name__, endpoint, username))
        response_as_string = self.make_request(endpoint, request_headers)
        logging.debug("{}.get_institutions() returned {}".format(__class__.__name__, response_as_string))
        results_as_dict = self.parse_response(response_as_string, required_keys = ['user_details'])

        results = []
        for item in results_as_dict['user_details']['memberOf']:
            for country_name in item['country_names']:
                results.append(
                    Institution(item['inst_name'], country_name)
                    )

        return results

    def get_institution_names(self) -> List[Institution]:
        """ Returns a list of all instiution names """
        results = []
        with self.connector.get_connection() as con:
            rs = con.execute(self.SELECT_INSTITUTIONS_SQL)

        for row in rs:
            results.append(row['name'])

        return results

    def get_samples_filtered_by_metadata(self, filters: dict) -> List:
        """ Get sample ids where their columns' values are in specified filters """
        # TODO: Also consider other filters such as greater than/less than...

        sanger_sample_ids = []
        with self.connector.get_connection() as con:
            if len(filters) > 0:
                for filter, values in filters.items():
                  new_sanger_sample_ids = []
                  try:
                    rs = con.execute(text(self.FILTER_SAMPLES_IN_SQL.format(filter)), values = tuple(values))
                    new_sanger_sample_ids.extend([row['sanger_sample_id'] for row in rs])
                    if len(sanger_sample_ids) > 0:
                      tmp_ids = [id for id in new_sanger_sample_ids if id in sanger_sample_ids]
                      sanger_sample_ids = tmp_ids
                    else:
                      sanger_sample_ids = new_sanger_sample_ids
                  except OperationalError as e:
                    if 'Unknown column' in str(e):
                      logging.error("attempted to apply filter to unknown field \"{}\"".format(filter))
                      return None
                    else:
                      raise e
            else:
                rs = con.execute(self.SELECT_ALL_SAMPLES_SQL)
                sanger_sample_ids = [row['sanger_sample_id'] for row in rs]

        return sanger_sample_ids

    def get_lanes_filtered_by_in_silico_data(self, filters: dict) -> List:
        """ Get lane ids from in silico data that match the specified filters """
        # TODO: Also consider other filters such as greater than/less than...

        lane_ids = []
        with self.connector.get_connection() as con:
            if len(filters) > 0:
                for filter, values in filters.items():
                  new_lane_ids = []
                  try:
                    rs = con.execute(text(self.IN_SILICO_FILTER_LANES_IN_SQL.format(filter)), values = tuple(values))
                    new_lane_ids.extend([row['lane_id'] for row in rs])
                    if len(lane_ids) > 0:
                      tmp_ids = [id for id in new_lane_ids if id in lane_ids]
                      lane_ids = tmp_ids
                    else:
                      lane_ids = new_lane_ids
                  except OperationalError as e:
                    if 'Unknown column' in str(e):
                      logging.error("attempted to apply filter to unknown field \"{}\"".format(filter))
                      return None
                    else:
                      raise e
            else:
                rs = con.execute(self.SELECT_ALL_IN_SILICO_SQL)
                lane_ids = [row['lane_id'] for row in rs]

        return lane_ids

    def get_distinct_values(self, field_type: str, fields: list, institutions: list) -> Dict:
        """
        Return distinct values found in db for each field name passed,
        from samples from certain instititons.
        Pass the field type ('metadata', 'in silico' or 'qc data');
        a list of names of the fields of interest; and a list of institution
        names.
        If any of the field names passed are non-existent, returns None
        """
        sql_query =  {  'metadata':    self.DISTINCT_FIELD_VALUES_SQL,
                        'in silico':   self.DISTINCT_IN_SILICO_FIELD_VALUES_SQL,
                        'qc data':     self.DISTINCT_QC_DATA_FIELD_VALUES_SQL
                        }
        if field_type not in sql_query.keys():
          raise ValueError("{} must be passed one of {}, not {}".format(__class__.__name__, ', '.join(sql_query.keys()), field_type))
        distinct_values = []
        with self.connector.get_connection() as con:
          for this_field in fields:
            try:
              rs = con.execute( text(sql_query[field_type].format(this_field)), institutions = tuple(institutions) )
              these_distinct_values = []
              for row in rs:
                if row[this_field] is None:
                  these_distinct_values.append('NULL')
                else:
                  these_distinct_values.append(str(row[this_field]))
              if len(these_distinct_values) > 0:
                distinct_values.append({  "name": this_field,
                                          "values": sorted(these_distinct_values)
                                          }
                                       )
              
            except OperationalError as e:
              if 'Unknown column' in str(e):
                logging.error("attempted to get distinct values from unknown field \"{}\"".format(this_field))
                return None
              else:
                raise e
          logging.info("distinct {} values: {}".format(field_type, 'distinct_values'))
        return distinct_values

    def get_samples(self) -> List[Metadata]:
        """ Retrieve all sample records """
        results = []

        with self.connector.get_connection() as con:
            rs = con.execute(self.SELECT_ALL_SAMPLES_SQL)
        for row in rs:
            results.append(
               Metadata(
                  sanger_sample_id=row['sanger_sample_id'],
                  lane_id=row['lane_id'],
                  submitting_institution=row['submitting_institution'],
                  supplier_sample_name=row['supplier_sample_name'],
                  public_name=row['public_name'],
                  host_status=row['host_status'],
                  study_name=row['study_name'],
                  study_ref=row['study_ref'],
                  selection_random=row['selection_random'],
                  country=row['country'],
                  county_state=row['county_state'],
                  city=row['city'],
                  collection_year=str(row['collection_year']),
                  collection_month=str(row['collection_month']),
                  collection_day=str(row['collection_day']),
                  host_species=row['host_species'],
                  gender=row['gender'],
                  age_group=row['age_group'],
                  age_years=str(row['age_years']),
                  age_months=str(row['age_months']),
                  age_weeks=str(row['age_weeks']),
                  age_days=str(row['age_days']),
                  disease_type=row['disease_type'],
                  disease_onset=row['disease_onset'],
                  isolation_source=row['isolation_source'],
                  serotype=row['serotype'],
                  serotype_method=row['serotype_method'],
                  infection_during_pregnancy=row['infection_during_pregnancy'],
                  maternal_infection_type=row['maternal_infection_type'],
                  gestational_age_weeks=str(row['gestational_age_weeks']),
                  birth_weight_gram=str(row['birth_weight_gram']),
                  apgar_score=str(row['apgar_score']),
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
                  linezolid_method=row['linezolid_method']
               )
            )

        return results

    def update_sample_metadata(self, metadata_list: List[Metadata]) -> None:
        """ Update sample metadata in the database """

        if not metadata_list:
            return

        logger.info(
            "update_sample_metadata: About to write {} upload samples to the database...".format(len(metadata_list))
        )

        # Use a transaction...
        with self.connector.get_transactional_connection() as con:
            for metadata in metadata_list:
                con.execute(
                    self.INSERT_OR_UPDATE_SAMPLE_SQL,
                    sanger_sample_id=metadata.sanger_sample_id,
                    lane_id=self.convert_string(metadata.lane_id),
                    supplier_sample_name=metadata.supplier_sample_name,
                    public_name=metadata.public_name,
                    host_status=self.convert_string(metadata.host_status),
                    serotype=self.convert_string(metadata.serotype),
                    submitting_institution=metadata.submitting_institution,
                    age_days=self.convert_int(metadata.age_days),
                    age_group=self.convert_string(metadata.age_group),
                    age_months=self.convert_int(metadata.age_months),
                    age_weeks=self.convert_int(metadata.age_weeks),
                    age_years=self.convert_int(metadata.age_years),
                    ampicillin=self.convert_string(metadata.ampicillin),
                    ampicillin_method=self.convert_string(metadata.ampicillin_method),
                    apgar_score=self.convert_int(metadata.apgar_score),
                    birth_weight_gram=self.convert_int(metadata.birth_weight_gram),
                    cefazolin=self.convert_string(metadata.cefazolin),
                    cefazolin_method=self.convert_string(metadata.cefazolin_method),
                    cefotaxime=self.convert_string(metadata.cefotaxime),
                    cefotaxime_method=self.convert_string(metadata.cefotaxime_method),
                    cefoxitin=self.convert_string(metadata.cefoxitin),
                    cefoxitin_method=self.convert_string(metadata.cefoxitin_method),
                    ceftizoxime=self.convert_string(metadata.ceftizoxime),
                    ceftizoxime_method=self.convert_string(metadata.ceftizoxime_method),
                    ciprofloxacin=self.convert_string(metadata.ciprofloxacin),
                    ciprofloxacin_method=self.convert_string(metadata.ciprofloxacin_method),
                    city=self.convert_string(metadata.city),
                    clindamycin=self.convert_string(metadata.clindamycin),
                    clindamycin_method=self.convert_string(metadata.clindamycin_method),
                    collection_day=self.convert_int(metadata.collection_day),
                    collection_month=self.convert_int(metadata.collection_month),
                    collection_year=self.convert_int(metadata.collection_year),
                    country=self.convert_string(metadata.country),
                    county_state=self.convert_string(metadata.county_state),
                    daptomycin=self.convert_string(metadata.daptomycin),
                    daptomycin_method=self.convert_string(metadata.daptomycin_method),
                    disease_onset=self.convert_string(metadata.disease_onset),
                    disease_type=self.convert_string(metadata.disease_type),
                    erythromycin=self.convert_string(metadata.erythromycin),
                    erythromycin_method=self.convert_string(metadata.erythromycin_method),
                    gender=self.convert_string(metadata.gender),
                    gestational_age_weeks=self.convert_int(metadata.gestational_age_weeks),
                    host_species=self.convert_string(metadata.host_species),
                    infection_during_pregnancy=self.convert_string(metadata.infection_during_pregnancy),
                    isolation_source=self.convert_string(metadata.isolation_source),
                    levofloxacin=self.convert_string(metadata.levofloxacin),
                    levofloxacin_method=self.convert_string(metadata.levofloxacin_method),
                    linezolid=self.convert_string(metadata.linezolid),
                    linezolid_method=self.convert_string(metadata.linezolid_method),
                    maternal_infection_type=self.convert_string(metadata.maternal_infection_type),
                    penicillin=self.convert_string(metadata.penicillin),
                    penicillin_method=self.convert_string(metadata.penicillin_method),
                    selection_random=self.convert_string(metadata.selection_random),
                    serotype_method=self.convert_string(metadata.serotype_method),
                    study_name=self.convert_string(metadata.study_name),
                    study_ref=self.convert_string(metadata.study_ref),
                    tetracycline=self.convert_string(metadata.tetracycline),
                    tetracycline_method=self.convert_string(metadata.tetracycline_method),
                    vancomycin=self.convert_string(metadata.vancomycin),
                    vancomycin_method=self.convert_string(metadata.vancomycin_method)
                )

        logger.info("update_sample_metadata completed")

    def update_lane_in_silico_data(self, in_silico_data_list: List[InSilicoData]) -> None:
        """ Update sample in silico data in the database """

        if not in_silico_data_list:
            return

        logger.info(
            "update_lane_in_silico_data: About to write {} upload samples to the database...".format(len(in_silico_data_list))
        )

        # Use a transaction...
        with self.connector.get_transactional_connection() as con:
            for in_silico_data in in_silico_data_list:
                con.execute(
                    self.INSERT_OR_UPDATE_IN_SILICO_SQL,
                    lane_id=self.convert_string(in_silico_data.lane_id),
                    cps_type=self.convert_string(in_silico_data.cps_type),
                    ST=self.convert_string(in_silico_data.ST),
                    adhP=self.convert_string(in_silico_data.adhP),
                    pheS=self.convert_string(in_silico_data.pheS),
                    atr=self.convert_string(in_silico_data.atr),
                    glnA=self.convert_string(in_silico_data.glnA),
                    sdhA=self.convert_string(in_silico_data.sdhA),
                    glcK=self.convert_string(in_silico_data.glcK),
                    tkt=self.convert_string(in_silico_data.tkt),
                    twenty_three_S1=self.convert_string(in_silico_data.twenty_three_S1),
                    twenty_three_S3=self.convert_string(in_silico_data.twenty_three_S3),
                    AAC6APH2=self.convert_string(in_silico_data.AAC6APH2),
                    AADECC=self.convert_string(in_silico_data.AADECC),
                    ANT6=self.convert_string(in_silico_data.ANT6),
                    APH3III=self.convert_string(in_silico_data.APH3III),
                    APH3OTHER=self.convert_string(in_silico_data.APH3OTHER),
                    CATPC194=self.convert_string(in_silico_data.CATPC194),
                    CATQ=self.convert_string(in_silico_data.CATQ),
                    ERMA=self.convert_string(in_silico_data.ERMA),
                    ERMB=self.convert_string(in_silico_data.ERMB),
                    ERMT=self.convert_string(in_silico_data.ERMT),
                    LNUB=self.convert_string(in_silico_data.LNUB),
                    LNUC=self.convert_string(in_silico_data.LNUC),
                    LSAC=self.convert_string(in_silico_data.LSAC),
                    MEFA=self.convert_string(in_silico_data.MEFA),
                    MPHC=self.convert_string(in_silico_data.MPHC),
                    MSRA=self.convert_string(in_silico_data.MSRA),
                    MSRD=self.convert_string(in_silico_data.MSRD),
                    FOSA=self.convert_string(in_silico_data.FOSA),
                    GYRA=self.convert_string(in_silico_data.GYRA),
                    PARC=self.convert_string(in_silico_data.PARC),
                    RPOBGBS_1=self.convert_string(in_silico_data.RPOBGBS_1),
                    RPOBGBS_2=self.convert_string(in_silico_data.RPOBGBS_2),
                    RPOBGBS_3=self.convert_string(in_silico_data.RPOBGBS_3),
                    RPOBGBS_4=self.convert_string(in_silico_data.RPOBGBS_4),
                    SUL2=self.convert_string(in_silico_data.SUL2),
                    TETB=self.convert_string(in_silico_data.TETB),
                    TETL=self.convert_string(in_silico_data.TETL),
                    TETM=self.convert_string(in_silico_data.TETM),
                    TETO=self.convert_string(in_silico_data.TETO),
                    TETS=self.convert_string(in_silico_data.TETS),
                    ALP1=self.convert_string(in_silico_data.ALP1),
                    ALP23=self.convert_string(in_silico_data.ALP23),
                    ALPHA=self.convert_string(in_silico_data.ALPHA),
                    HVGA=self.convert_string(in_silico_data.HVGA),
                    PI1=self.convert_string(in_silico_data.PI1),
                    PI2A1=self.convert_string(in_silico_data.PI2A1),
                    PI2A2=self.convert_string(in_silico_data.PI2A2),
                    PI2B=self.convert_string(in_silico_data.PI2B),
                    RIB=self.convert_string(in_silico_data.RIB),
                    SRR1=self.convert_string(in_silico_data.SRR1),
                    SRR2=self.convert_string(in_silico_data.SRR2),
                    twenty_three_S1_variant=self.convert_string(in_silico_data.twenty_three_S1_variant),
                    twenty_three_S3_variant=self.convert_string(in_silico_data.twenty_three_S3_variant),
                    GYRA_variant=self.convert_string(in_silico_data.GYRA_variant),
                    PARC_variant=self.convert_string(in_silico_data.PARC_variant),
                    RPOBGBS_1_variant=self.convert_string(in_silico_data.RPOBGBS_1_variant),
                    RPOBGBS_2_variant=self.convert_string(in_silico_data.RPOBGBS_2_variant),
                    RPOBGBS_3_variant=self.convert_string(in_silico_data.RPOBGBS_3_variant),
                    RPOBGBS_4_variant=self.convert_string(in_silico_data.RPOBGBS_4_variant)
                )

        logger.info("update_lane_in_silico_data completed")

    def update_lane_qc_data(self, qc_data_list: List[QCData]) -> None:
        """ Update sample QC data in the database """

        if not qc_data_list:
            return

        logger.info(
            "update_lane_qc_data: About to write {} upload samples to the database...".format(len(qc_data_list))
        )

        # Use a transaction...
        with self.connector.get_transactional_connection() as con:
            for qc_data in qc_data_list:
                con.execute(
                    self.INSERT_OR_UPDATE_QC_DATA_SQL,
                    lane_id=self.convert_string(qc_data.lane_id),
                    rel_abun_sa=self.convert_string(qc_data.rel_abun_sa)
                )

        logger.info("update_lane_qc_data completed")

    def get_download_metadata(self, keys: List[str]) -> List[Metadata]:
        """ Get download metadata for given list of samples """

        if len(keys) == 0:
            return []

        results = []
        sanger_sample_ids = tuple(keys)

        logger.info(
            "get_download_metadata: About to pull {} sample records from the database...".format(len(sanger_sample_ids))
        )
        logger.debug(
            "get_download_metadata: Pulling sample ids {} from the database...".format(sanger_sample_ids)
        )

        with self.connector.get_connection() as con:
            rs = con.execute(self.SELECT_SAMPLES_SQL, samples=sanger_sample_ids)

        for row in rs:
            results.append(
               Metadata(
                  sanger_sample_id=row['sanger_sample_id'],
                  lane_id=row['lane_id'],
                  submitting_institution=row['submitting_institution'],
                  supplier_sample_name=row['supplier_sample_name'],
                  public_name=row['public_name'],
                  host_status=row['host_status'],
                  study_name=row['study_name'],
                  study_ref=row['study_ref'],
                  selection_random=row['selection_random'],
                  country=row['country'],
                  county_state=row['county_state'],
                  city=row['city'],
                  collection_year=str(row['collection_year']),
                  collection_month=str(row['collection_month']),
                  collection_day=str(row['collection_day']),
                  host_species=row['host_species'],
                  gender=row['gender'],
                  age_group=row['age_group'],
                  age_years=str(row['age_years']),
                  age_months=str(row['age_months']),
                  age_weeks=str(row['age_weeks']),
                  age_days=str(row['age_days']),
                  disease_type=row['disease_type'],
                  disease_onset=row['disease_onset'],
                  isolation_source=row['isolation_source'],
                  serotype=row['serotype'],
                  serotype_method=row['serotype_method'],
                  infection_during_pregnancy=row['infection_during_pregnancy'],
                  maternal_infection_type=row['maternal_infection_type'],
                  gestational_age_weeks=str(row['gestational_age_weeks']),
                  birth_weight_gram=str(row['birth_weight_gram']),
                  apgar_score=str(row['apgar_score']),
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
                  linezolid_method=row['linezolid_method']
               )
            )
        logger.debug(
            "get_download_metadata: Pulled records of samples {} from the database...".format(results)
        )

        return results

    def get_download_in_silico_data(self, keys: List[str]) -> List[InSilicoData]:
        """ Get download in silico data for given list of lane keys """

        if len(keys) == 0:
            return []

        results = []
        lane_ids = tuple(keys)

        with self.connector.get_connection() as con:
            rs = con.execute(self.SELECT_LANES_IN_SILICO_SQL, lanes=lane_ids)

        for row in rs:
            results.append(
               InSilicoData(
                  lane_id=row['lane_id'],
                  cps_type=row['cps_type'],
                  ST=row['ST'],
                  adhP=row['adhP'],
                  pheS=row['pheS'],
                  atr=row['atr'],
                  glnA=row['glnA'],
                  sdhA=row['sdhA'],
                  glcK=row['glcK'],
                  tkt=row['tkt'],
                  twenty_three_S1=row['twenty_three_S1'],
                  twenty_three_S3=row['twenty_three_S3'],
                  AAC6APH2=row['AAC6APH2'],
                  AADECC=row['AADECC'],
                  ANT6=row['ANT6'],
                  APH3III=row['APH3III'],
                  APH3OTHER=row['APH3OTHER'],
                  CATPC194=row['CATPC194'],
                  CATQ=row['CATQ'],
                  ERMA=row['ERMA'],
                  ERMB=row['ERMB'],
                  ERMT=row['ERMT'],
                  LNUB=row['LNUB'],
                  LNUC=row['LNUC'],
                  LSAC=row['LSAC'],
                  MEFA=row['MEFA'],
                  MPHC=row['MPHC'],
                  MSRA=row['MSRA'],
                  MSRD=row['MSRD'],
                  FOSA=row['FOSA'],
                  GYRA=row['GYRA'],
                  PARC=row['PARC'],
                  RPOBGBS_1=row['RPOBGBS_1'],
                  RPOBGBS_2=row['RPOBGBS_2'],
                  RPOBGBS_3=row['RPOBGBS_3'],
                  RPOBGBS_4=row['RPOBGBS_4'],
                  SUL2=row['SUL2'],
                  TETB=row['TETB'],
                  TETL=row['TETL'],
                  TETM=row['TETM'],
                  TETO=row['TETO'],
                  TETS=row['TETS'],
                  ALP1=row['ALP1'],
                  ALP23=row['ALP23'],
                  ALPHA=row['ALPHA'],
                  HVGA=row['HVGA'],
                  PI1=row['PI1'],
                  PI2A1=row['PI2A1'],
                  PI2A2=row['PI2A2'],
                  PI2B=row['PI2B'],
                  RIB=row['RIB'],
                  SRR1=row['SRR1'],
                  SRR2=row['SRR2'],
                  twenty_three_S1_variant=row['twenty_three_S1_variant'],
                  twenty_three_S3_variant=row['twenty_three_S3_variant'],
                  GYRA_variant=row['GYRA_variant'],
                  PARC_variant=row['PARC_variant'],
                  RPOBGBS_1_variant=row['RPOBGBS_1_variant'],
                  RPOBGBS_2_variant=row['RPOBGBS_2_variant'],
                  RPOBGBS_3_variant=row['RPOBGBS_3_variant'],
                  RPOBGBS_4_variant=row['RPOBGBS_4_variant']
               )
            )

        return results

    def get_download_qc_data(self, keys: List[str]) -> List[QCData]:
        """ Get download QC data for given list of lane keys """

        if len(keys) == 0:
            return []

        results = []
        lane_ids = tuple(keys)

        with self.connector.get_connection() as con:
            rs = con.execute(self.SELECT_LANES_QC_DATA_SQL, lanes=lane_ids)

        for row in rs:
            results.append(
               QCData(
                  lane_id=row['lane_id'],
                  rel_abun_sa=row['rel_abun_sa']
               )
            )

        return results

    def delete_all_qc_data(self):
        """ Delete all QC data """
        with self.connector.get_connection() as con:
            rs = con.execute(self.DELETE_ALL_QC_DATA_SQL)
