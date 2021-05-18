import pandas
import logging
import re
from typing import List
from pandas_schema import Column, Schema
from pandas_schema.validation import LeadingWhitespaceValidation, TrailingWhitespaceValidation, MatchesPatternValidation, InRangeValidation, InListValidation, CustomSeriesValidation
from metadata.api.model.metadata import Metadata
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition
from metadata.api.database.monocle_database_service import MonocleDatabaseService

logger = logging.getLogger()


class UploadHandler:
    """ Handle processing of upload spreadsheets """

    @property
    def data_frame(self):
        return self.__df

    def __init__(self, dao: MonocleDatabaseService, in_def: SpreadsheetDefinition, do_validation: bool) -> None:
        self.__df = None
        self.__dao = dao
        self.__spreadsheet_def = in_def
        self.do_validation = do_validation
        self.__institutions = None

    def get_column_name_for_key(self, key: str):
        """ Given a spreadsheet definition key return the corresponding column title """
        return self.__spreadsheet_def.get_column_name(key)

    def create_schema(self) -> Schema:
        """ Create Pandas schema with all the necessary validation rules read in from config """
        col_list = []
        for column in self.__spreadsheet_def.keys():
            validators = [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()]

            mandatory_field_flag = self.__spreadsheet_def.is_mandatory(column)

            # Special cases for checking institutions/countries...
            if column == 'submitting_institution':
                validators.append(InListValidation([i.name for i in self.__institutions], case_sensitive=False))
            if column == 'country':
                validators.append(InListValidation([i.country for i in self.__institutions], case_sensitive=False))
            else:
                if self.__spreadsheet_def.get_regex(column):
                    validators.append(MatchesPatternValidation(self.__spreadsheet_def.get_regex(column)))

                max_len = self.__spreadsheet_def.get_max_length(column)
                if max_len and max_len > 0:

                    validators.append(
                        CustomSeriesValidation(
                            lambda s: s.str.len() > max_len,
                            'field length is greater than {} characters'.format(str(max_len))
                        )
                    )

                if self.__spreadsheet_def.get_allowed_values(column):
                    validators.append(InListValidation(self.__spreadsheet_def.get_allowed_values(column)))

            col_list.append(
                Column(self.__spreadsheet_def.get_column_name(column), validators, allow_empty=not mandatory_field_flag)
            )

        return Schema(col_list)

    def format_validation_errors(self, errors: list) -> List[str]:
        """
            Format any validation errors.
            Pandas schema does not seem to take notice of where the header row is for its validation error
            row numbering so we need to modify the error messages to correct it.
        """
        results = []
        for error in errors:
            error_text = str(error)
            m = re.match(r"^[{]row: (\d+),", error_text)
            if m:
                row_num_int = int(m[1]) + self.__spreadsheet_def.header_row_position + 2
                error_text = re.sub(r"row: \d+,", "row: {},".format(row_num_int), error_text)
            results.append(error_text)
        return results

    def load(self, file_path: str) -> List[str]:
        """
            Read the spreadsheet to a pandas data frame.
            Returns a list of validation error strings [if any].
        """
        errors = []

        logger.info("Loading spreadsheet...")

        data = pandas.read_excel(file_path, dtype=str, header=self.__spreadsheet_def.header_row_position)
        data.fillna('', inplace=True)

        for key, value in data.iterrows():
            logger.debug("{} {}".format(key, value))

        if self.do_validation:
            # Get a list of valid institutions and cache them
            self.__institutions = self.__dao.get_institutions()
            # Create a validation schema
            schema = self.create_schema()
            # Run the validation
            errors = schema.validate(data, columns=schema.get_column_names())
            if len(errors) > 0:
                return self.format_validation_errors(errors)

        self.__df = pandas.DataFrame(data)
        return errors

    def parse(self) -> List[Metadata]:
        """ Parse the data frame into dataclasses """
        results = []
        for _, row in self.__df.iterrows():
            metadata = Metadata(
                            sanger_sample_id=row[self.get_column_name_for_key('sanger_sample_id')],
                            lane_id=row[self.get_column_name_for_key('lane_id')],
                            submitting_institution=row[self.get_column_name_for_key('submitting_institution')],
                            supplier_sample_name=row[self.get_column_name_for_key('supplier_sample_name')],
                            public_name=row[self.get_column_name_for_key('public_name')],
                            host_status=row[self.get_column_name_for_key('host_status')],
                            study_name=row[self.get_column_name_for_key('study_name')],
                            study_ref=row[self.get_column_name_for_key('study_ref')],
                            selection_random=row[self.get_column_name_for_key('selection_random')],
                            country=row[self.get_column_name_for_key('country')],
                            county_state=row[self.get_column_name_for_key('county_state')],
                            city=row[self.get_column_name_for_key('city')],
                            collection_year=row[self.get_column_name_for_key('collection_year')],
                            collection_month=row[self.get_column_name_for_key('collection_month')],
                            collection_day=row[self.get_column_name_for_key('collection_day')],
                            host_species=row[self.get_column_name_for_key('host_species')],
                            gender=row[self.get_column_name_for_key('gender')],
                            age_group=row[self.get_column_name_for_key('age_group')],
                            age_years=row[self.get_column_name_for_key('age_years')],
                            age_months=row[self.get_column_name_for_key('age_months')],
                            age_weeks=row[self.get_column_name_for_key('age_weeks')],
                            age_days=row[self.get_column_name_for_key('age_days')],
                            disease_type=row[self.get_column_name_for_key('disease_type')],
                            disease_onset=row[self.get_column_name_for_key('disease_onset')],
                            isolation_source=row[self.get_column_name_for_key('isolation_source')],
                            serotype=row[self.get_column_name_for_key('serotype')],
                            serotype_method=row[self.get_column_name_for_key('serotype_method')],
                            infection_during_pregnancy=row[self.get_column_name_for_key('infection_during_pregnancy')],
                            maternal_infection_type=row[self.get_column_name_for_key('maternal_infection_type')],
                            gestational_age_weeks=row[self.get_column_name_for_key('gestational_age_weeks')],
                            birth_weight_gram=row[self.get_column_name_for_key('birth_weight_gram')],
                            apgar_score=row[self.get_column_name_for_key('apgar_score')],
                            ceftizoxime=row[self.get_column_name_for_key('ceftizoxime')],
                            ceftizoxime_method=row[self.get_column_name_for_key('ceftizoxime_method')],
                            cefoxitin=row[self.get_column_name_for_key('cefoxitin')],
                            cefoxitin_method=row[self.get_column_name_for_key('cefoxitin_method')],
                            cefotaxime=row[self.get_column_name_for_key('cefotaxime')],
                            cefotaxime_method=row[self.get_column_name_for_key('cefotaxime_method')],
                            cefazolin=row[self.get_column_name_for_key('cefazolin')],
                            cefazolin_method=row[self.get_column_name_for_key('cefazolin_method')],
                            ampicillin=row[self.get_column_name_for_key('ampicillin')],
                            ampicillin_method=row[self.get_column_name_for_key('ampicillin_method')],
                            penicillin=row[self.get_column_name_for_key('penicillin')],
                            penicillin_method=row[self.get_column_name_for_key('penicillin_method')],
                            erythromycin=row[self.get_column_name_for_key('erythromycin')],
                            erythromycin_method=row[self.get_column_name_for_key('erythromycin_method')],
                            clindamycin=row[self.get_column_name_for_key('clindamycin')],
                            clindamycin_method=row[self.get_column_name_for_key('clindamycin_method')],
                            tetracycline=row[self.get_column_name_for_key('tetracycline')],
                            tetracycline_method=row[self.get_column_name_for_key('tetracycline_method')],
                            levofloxacin=row[self.get_column_name_for_key('levofloxacin')],
                            levofloxacin_method=row[self.get_column_name_for_key('levofloxacin_method')],
                            ciprofloxacin=row[self.get_column_name_for_key('ciprofloxacin')],
                            ciprofloxacin_method=row[self.get_column_name_for_key('ciprofloxacin_method')],
                            daptomycin=row[self.get_column_name_for_key('daptomycin')],
                            daptomycin_method=row[self.get_column_name_for_key('daptomycin_method')],
                            vancomycin=row[self.get_column_name_for_key('vancomycin')],
                            vancomycin_method=row[self.get_column_name_for_key('vancomycin_method')],
                            linezolid=row[self.get_column_name_for_key('linezolid')],
                            linezolid_method=row[self.get_column_name_for_key('linezolid_method')])
            results.append(metadata)
        return results

    def store(self):
        if self.__df is not None:
            logger.info("Storing spreadsheet...")
            self.__dao.update_sample_metadata(self.parse())
        else:
            raise RuntimeError("No spreadsheet is currently loaded. Unable to store.")
