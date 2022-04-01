from typing import List

import pandas

from metadata.api.model.in_silico_data import InSilicoData
from metadata.api.model.metadata import Metadata
from metadata.lib.upload_handler import UploadHandler, logger


class UploadMetadataHandler(UploadHandler):
    def parse(self) -> List[Metadata]:
        """Parse the data frame into dataclasses"""
        results = []
        df = self.data_frame()
        for _, row in df.iterrows():
            metadata = Metadata(
                sanger_sample_id=self.get_cell_value("sanger_sample_id", row),
                lane_id=self.get_cell_value("lane_id", row),
                submitting_institution=self.get_cell_value("submitting_institution", row),
                supplier_sample_name=self.get_cell_value("supplier_sample_name", row),
                public_name=self.get_cell_value("public_name", row),
                host_status=self.get_cell_value("host_status", row),
                study_name=self.get_cell_value("study_name", row),
                study_ref=self.get_cell_value("study_ref", row),
                selection_random=self.get_cell_value("selection_random", row),
                country=self.get_cell_value("country", row),
                county_state=self.get_cell_value("county_state", row),
                city=self.get_cell_value("city", row),
                collection_year=self.get_cell_value("collection_year", row),
                collection_month=self.get_cell_value("collection_month", row),
                collection_day=self.get_cell_value("collection_day", row),
                host_species=self.get_cell_value("host_species", row),
                gender=self.get_cell_value("gender", row),
                age_group=self.get_cell_value("age_group", row),
                age_years=self.get_cell_value("age_years", row),
                age_months=self.get_cell_value("age_months", row),
                age_weeks=self.get_cell_value("age_weeks", row),
                age_days=self.get_cell_value("age_days", row),
                disease_type=self.get_cell_value("disease_type", row),
                disease_onset=self.get_cell_value("disease_onset", row),
                isolation_source=self.get_cell_value("isolation_source", row),
                serotype=self.get_cell_value("serotype", row),
                serotype_method=self.get_cell_value("serotype_method", row),
                infection_during_pregnancy=self.get_cell_value("infection_during_pregnancy", row),
                maternal_infection_type=self.get_cell_value("maternal_infection_type", row),
                gestational_age_weeks=self.get_cell_value("gestational_age_weeks", row),
                birth_weight_gram=self.get_cell_value("birth_weight_gram", row),
                apgar_score=self.get_cell_value("apgar_score", row),
                ceftizoxime=self.get_cell_value("ceftizoxime", row),
                ceftizoxime_method=self.get_cell_value("ceftizoxime_method", row),
                cefoxitin=self.get_cell_value("cefoxitin", row),
                cefoxitin_method=self.get_cell_value("cefoxitin_method", row),
                cefotaxime=self.get_cell_value("cefotaxime", row),
                cefotaxime_method=self.get_cell_value("cefotaxime_method", row),
                cefazolin=self.get_cell_value("cefazolin", row),
                cefazolin_method=self.get_cell_value("cefazolin_method", row),
                ampicillin=self.get_cell_value("ampicillin", row),
                ampicillin_method=self.get_cell_value("ampicillin_method", row),
                penicillin=self.get_cell_value("penicillin", row),
                penicillin_method=self.get_cell_value("penicillin_method", row),
                erythromycin=self.get_cell_value("erythromycin", row),
                erythromycin_method=self.get_cell_value("erythromycin_method", row),
                clindamycin=self.get_cell_value("clindamycin", row),
                clindamycin_method=self.get_cell_value("clindamycin_method", row),
                tetracycline=self.get_cell_value("tetracycline", row),
                tetracycline_method=self.get_cell_value("tetracycline_method", row),
                levofloxacin=self.get_cell_value("levofloxacin", row),
                levofloxacin_method=self.get_cell_value("levofloxacin_method", row),
                ciprofloxacin=self.get_cell_value("ciprofloxacin", row),
                ciprofloxacin_method=self.get_cell_value("ciprofloxacin_method", row),
                daptomycin=self.get_cell_value("daptomycin", row),
                daptomycin_method=self.get_cell_value("daptomycin_method", row),
                vancomycin=self.get_cell_value("vancomycin", row),
                vancomycin_method=self.get_cell_value("vancomycin_method", row),
                linezolid=self.get_cell_value("linezolid", row),
                linezolid_method=self.get_cell_value("linezolid_method", row),
            )
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
            in_silico_data = InSilicoData(
                lane_id=self.get_cell_value("lane_id", row),
                cps_type=self.get_cell_value("cps_type", row),
                ST=self.get_cell_value("ST", row),
                adhP=self.get_cell_value("adhP", row),
                pheS=self.get_cell_value("pheS", row),
                atr=self.get_cell_value("atr", row),
                glnA=self.get_cell_value("glnA", row),
                sdhA=self.get_cell_value("sdhA", row),
                glcK=self.get_cell_value("glcK", row),
                tkt=self.get_cell_value("tkt", row),
                twenty_three_S1=self.get_cell_value("twenty_three_S1", row),
                twenty_three_S3=self.get_cell_value("twenty_three_S3", row),
                AAC6APH2=self.get_cell_value("AAC6APH2", row),
                AADECC=self.get_cell_value("AADECC", row),
                ANT6=self.get_cell_value("ANT6", row),
                APH3III=self.get_cell_value("APH3III", row),
                APH3OTHER=self.get_cell_value("APH3OTHER", row),
                CATPC194=self.get_cell_value("CATPC194", row),
                CATQ=self.get_cell_value("CATQ", row),
                ERMA=self.get_cell_value("ERMA", row),
                ERMB=self.get_cell_value("ERMB", row),
                ERMT=self.get_cell_value("ERMT", row),
                LNUB=self.get_cell_value("LNUB", row),
                LNUC=self.get_cell_value("LNUC", row),
                LSAC=self.get_cell_value("LSAC", row),
                MEFA=self.get_cell_value("MEFA", row),
                MPHC=self.get_cell_value("MPHC", row),
                MSRA=self.get_cell_value("MSRA", row),
                MSRD=self.get_cell_value("MSRD", row),
                FOSA=self.get_cell_value("FOSA", row),
                GYRA=self.get_cell_value("GYRA", row),
                PARC=self.get_cell_value("PARC", row),
                RPOBGBS_1=self.get_cell_value("RPOBGBS_1", row),
                RPOBGBS_2=self.get_cell_value("RPOBGBS_2", row),
                RPOBGBS_3=self.get_cell_value("RPOBGBS_3", row),
                RPOBGBS_4=self.get_cell_value("RPOBGBS_4", row),
                SUL2=self.get_cell_value("SUL2", row),
                TETB=self.get_cell_value("TETB", row),
                TETL=self.get_cell_value("TETL", row),
                TETM=self.get_cell_value("TETM", row),
                TETO=self.get_cell_value("TETO", row),
                TETS=self.get_cell_value("TETS", row),
                ALP1=self.get_cell_value("ALP1", row),
                ALP23=self.get_cell_value("ALP23", row),
                ALPHA=self.get_cell_value("ALPHA", row),
                HVGA=self.get_cell_value("HVGA", row),
                PI1=self.get_cell_value("PI1", row),
                PI2A1=self.get_cell_value("PI2A1", row),
                PI2A2=self.get_cell_value("PI2A2", row),
                PI2B=self.get_cell_value("PI2B", row),
                RIB=self.get_cell_value("RIB", row),
                SRR1=self.get_cell_value("SRR1", row),
                SRR2=self.get_cell_value("SRR2", row),
                twenty_three_S1_variant=self.get_cell_value("twenty_three_S1_variant", row),
                twenty_three_S3_variant=self.get_cell_value("twenty_three_S3_variant", row),
                GYRA_variant=self.get_cell_value("GYRA_variant", row),
                PARC_variant=self.get_cell_value("PARC_variant", row),
                RPOBGBS_1_variant=self.get_cell_value("RPOBGBS_1_variant", row),
                RPOBGBS_2_variant=self.get_cell_value("RPOBGBS_2_variant", row),
                RPOBGBS_3_variant=self.get_cell_value("RPOBGBS_3_variant", row),
                RPOBGBS_4_variant=self.get_cell_value("RPOBGBS_4_variant", row),
            )
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
