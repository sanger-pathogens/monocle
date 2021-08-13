import os
import logging
from flask import Config
from injector import singleton, Module, provider
from metadata.api.configuration import *
from metadata.api.model.metadata import Metadata
from metadata.lib.upload_handler import UploadHandler
from metadata.api.download_handler import DownloadHandler
from metadata.api.database.monocle_database_service import MonocleDatabaseService
from metadata.api.database.monocle_database_service_impl import MonocleDatabaseServiceImpl, Connector
from metadata.api.database.monocle_database_service_noop_impl import MonocleDatabaseServiceNoOpImpl

logger = logging.getLogger()


class MetadataApiModule(Module):
    """ Dependency injection handler for this API """

    API_TEST_MODE = False

    def __init__(self) -> None:
        try:
            self.API_TEST_MODE = os.environ['API_TEST_MODE'].lower() == 'true'
        except KeyError:
            pass

    @provider
    @singleton
    def metadata_dao(self, config: Config) -> MonocleDatabaseService:
        if not self.API_TEST_MODE:
            return MonocleDatabaseServiceImpl(Connector(read_database_connection_config(config)))
        else:
            logger.info('Using mock database back end')
            return MonocleDatabaseServiceNoOpImpl(read_mock_database_connection_config(config))

    @provider
    def upload_handler(self, config: Config, metadata_dao: MonocleDatabaseService) -> UploadHandler:
        do_validation = False
        try:
            do_validation = config['upload_validation_enabled']
        except KeyError:
            pass
        metadata = Metadata(
                        sanger_sample_id=self.get_cell_value('sanger_sample_id', row),
                        lane_id=self.get_cell_value('lane_id', row),
                        submitting_institution=self.get_cell_value('submitting_institution', row),
                        supplier_sample_name=self.get_cell_value('supplier_sample_name', row),
                        public_name=self.get_cell_value('public_name', row),
                        host_status=self.get_cell_value('host_status', row),
                        study_name=self.get_cell_value('study_name', row),
                        study_ref=self.get_cell_value('study_ref', row),
                        selection_random=self.get_cell_value('selection_random', row),
                        country=self.get_cell_value('country', row),
                        county_state=self.get_cell_value('county_state', row),
                        city=self.get_cell_value('city', row),
                        collection_year=self.get_cell_value('collection_year', row),
                        collection_month=self.get_cell_value('collection_month', row),
                        collection_day=self.get_cell_value('collection_day', row),
                        host_species=self.get_cell_value('host_species', row),
                        gender=self.get_cell_value('gender', row),
                        age_group=self.get_cell_value('age_group', row),
                        age_years=self.get_cell_value('age_years', row),
                        age_months=self.get_cell_value('age_months', row),
                        age_weeks=self.get_cell_value('age_weeks', row),
                        age_days=self.get_cell_value('age_days', row),
                        disease_type=self.get_cell_value('disease_type', row),
                        disease_onset=self.get_cell_value('disease_onset', row),
                        isolation_source=self.get_cell_value('isolation_source', row),
                        serotype=self.get_cell_value('serotype', row),
                        serotype_method=self.get_cell_value('serotype_method', row),
                        infection_during_pregnancy=self.get_cell_value('infection_during_pregnancy', row),
                        maternal_infection_type=self.get_cell_value('maternal_infection_type', row),
                        gestational_age_weeks=self.get_cell_value('gestational_age_weeks', row),
                        birth_weight_gram=self.get_cell_value('birth_weight_gram', row),
                        apgar_score=self.get_cell_value('apgar_score', row),
                        ceftizoxime=self.get_cell_value('ceftizoxime', row),
                        ceftizoxime_method=self.get_cell_value('ceftizoxime_method', row),
                        cefoxitin=self.get_cell_value('cefoxitin', row),
                        cefoxitin_method=self.get_cell_value('cefoxitin_method', row),
                        cefotaxime=self.get_cell_value('cefotaxime', row),
                        cefotaxime_method=self.get_cell_value('cefotaxime_method', row),
                        cefazolin=self.get_cell_value('cefazolin', row),
                        cefazolin_method=self.get_cell_value('cefazolin_method', row),
                        ampicillin=self.get_cell_value('ampicillin', row),
                        ampicillin_method=self.get_cell_value('ampicillin_method', row),
                        penicillin=self.get_cell_value('penicillin', row),
                        penicillin_method=self.get_cell_value('penicillin_method', row),
                        erythromycin=self.get_cell_value('erythromycin', row),
                        erythromycin_method=self.get_cell_value('erythromycin_method', row),
                        clindamycin=self.get_cell_value('clindamycin', row),
                        clindamycin_method=self.get_cell_value('clindamycin_method', row),
                        tetracycline=self.get_cell_value('tetracycline', row),
                        tetracycline_method=self.get_cell_value('tetracycline_method', row),
                        levofloxacin=self.get_cell_value('levofloxacin', row),
                        levofloxacin_method=self.get_cell_value('levofloxacin_method', row),
                        ciprofloxacin=self.get_cell_value('ciprofloxacin', row),
                        ciprofloxacin_method=self.get_cell_value('ciprofloxacin_method', row),
                        daptomycin=self.get_cell_value('daptomycin', row),
                        daptomycin_method=self.get_cell_value('daptomycin_method', row),
                        vancomycin=self.get_cell_value('vancomycin', row),
                        vancomycin_method=self.get_cell_value('vancomycin_method', row),
                        linezolid=self.get_cell_value('linezolid', row),
                        linezolid_method=self.get_cell_value('linezolid_method', row))
        upload_metadata_handler = UploadHandler(metadata_dao, read_spreadsheet_definition_config(config), metadata, do_validation)
        return upload_metadata_handler

    @provider
    def download_handler(self, config: Config, metadata_dao: MonocleDatabaseService) -> DownloadHandler:
        return DownloadHandler(metadata_dao, read_spreadsheet_definition_config(config))
