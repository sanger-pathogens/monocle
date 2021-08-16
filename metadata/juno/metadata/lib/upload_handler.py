import pandas
import logging
import re
from typing import List
from pandas_schema import Column, Schema
from pandas_schema.validation import LeadingWhitespaceValidation, TrailingWhitespaceValidation, \
    MatchesPatternValidation, InRangeValidation, InListValidation, CustomElementValidation
from metadata.api.model.metadata import Metadata
from metadata.api.model.in_silico_data import InSilicoData
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition
from metadata.api.database.monocle_database_service import MonocleDatabaseService

logger = logging.getLogger()


class _StringLengthValidation(CustomElementValidation):
    """ A custom validator class for checking the data frame string lengths """
    def __init__(self, message: str, max_length: int):
        self.max_length = max_length
        super().__init__(validation=lambda s: len(s) <= self.max_length, message=message)


class UploadHandler:
    """ Handle processing of upload spreadsheets """

    # Allowed file formats
    file_types = {
        'tab' : getattr(pandas, 'read_csv'),
        'tsv' : getattr(pandas, 'read_csv'),
        'txt' : getattr(pandas, 'read_csv')
    }

    @property
    def data_frame(self):
        return self.__df

    def __init__(self, dao: MonocleDatabaseService, in_def: SpreadsheetDefinition, do_validation: bool) -> None:
        self.__df = None
        self.__dao = dao
        self.__spreadsheet_def = in_def
        self.__do_validation = do_validation
        self.__institutions = None

    @staticmethod
    def allowed_file_types() -> List[str]:
        """ Return a list of allowed file type extensions """
        return [str(key) for key in UploadHandler.file_types.keys()]

    @staticmethod
    def is_valid_file_type(file: str) -> bool:
        """ Check if we can process this file type """
        valid = False
        try:
            if file and '.' in file:
                suffix = file.split('.')[-1]
                if suffix in UploadHandler.allowed_file_types():
                    valid = True
        except Exception as e:
            logger.warning(str(e))

        return valid

    def get_cell_value(self, column_key: str, row):
        """
            Return a cell value given a column name and row object.
            Do any necessary data conversion.
        """
        val = row[self.__spreadsheet_def.get_column_name(column_key)]
        case_setting = self.__spreadsheet_def.get_case(column_key)

        # Do we need to convert case...
        if case_setting:
            if case_setting == 'lower':
                val = val.lower()
            elif case_setting == 'upper':
                val = val.upper()

            preserved_values = self.__spreadsheet_def.get_case_preserve(column_key)
            if preserved_values:
                for p in preserved_values:
                    regex = re.compile(re.escape(p), re.IGNORECASE)
                    val = regex.sub(p, val)

        return val

    def create_schema(self) -> Schema:
        """ Create Pandas schema with all the necessary validation rules read in from config """
        col_list = []
        for column in self.__spreadsheet_def.keys():
            validators = [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()]

            mandatory_field_flag = self.__spreadsheet_def.is_mandatory(column)

            # Special cases for checking institutions/countries...
            if column == 'submitting_institution':
                validators.append(InListValidation([i.name for i in self.__institutions]))
            if column == 'country':
                validators.append(InListValidation([i.country for i in self.__institutions]))
            else:
                # Regex validation
                if self.__spreadsheet_def.get_regex(column):
                    validators.append(
                        MatchesPatternValidation(
                            self.__spreadsheet_def.get_regex(column),
                            message=self.__spreadsheet_def.get_regex_validation_message(column)
                        )
                    )

                # Validate allowed values
                elif self.__spreadsheet_def.get_allowed_values(column):
                    validators.append(
                        InListValidation(self.__spreadsheet_def.get_allowed_values(column), case_sensitive=False)
                    )

                # Field length validation
                max_len = self.__spreadsheet_def.get_max_length(column)
                if max_len and max_len > 0:
                    validators.append(
                        _StringLengthValidation(
                            'field length is greater than {} characters'.format(str(max_len)),
                            max_len
                        )
                    )

            # Mandatory field validation
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

        logger.info('Loading spreadsheet {}...'.format(file_path))

        # Belt and braces file type check
        if not self.is_valid_file_type(file_path):
            raise RuntimeError('Not an allowed file extension')

        # Load the data to a data frame
        suffix = file_path.split(".")[-1]
        data = self.file_types[suffix](
            file_path,
            dtype=str,
            sep='\t',
            header=self.__spreadsheet_def.header_row_position
        )
        data.fillna('', inplace=True)

        # Display spreadsheet contents for debugging if required
        # for key, value in data.iterrows():
        #     logger.debug("{} {}".format(key, value))

        if self.__do_validation:
            # Get a list of valid institutions and cache them
            self.__institutions = self.__dao.get_institutions()
            # Create a validation schema
            schema = self.create_schema()
            # Run the validation
            errors = schema.validate(data, columns=schema.get_column_names())
            if len(errors) > 0:
                formatted_errors = self.format_validation_errors(errors)
                logger.warning("Found {} upload validation errors".format(len(errors)))
                return formatted_errors

        self.__df = pandas.DataFrame(data)
        return errors

    def parse_metadata(self) -> List[Metadata]:
        """ Parse the data frame into dataclasses """
        results = []
        for _, row in self.__df.iterrows():
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
            results.append(metadata)
        return results

    def store_metadata(self):
        if self.__df is not None:
            logger.info("Storing spreadsheet...")
            self.__dao.update_sample_metadata(self.parse_metadata())
        else:
            raise RuntimeError("No spreadsheet is currently loaded. Unable to store.")

    def parse_in_silico_data(self):
        """ Parse in silico data into dataclass """
        results = []
        for _, row in self.__df.iterrows():
            in_silico_data = InSilicoData(
                                lane_id=self.get_cell_value('lane_id', row),
                                cps_type=self.get_cell_value('cps_type', row),
                                ST=self.get_cell_value('ST', row),
                                adhP=self.get_cell_value('adhP', row),
                                pheS=self.get_cell_value('pheS', row),
                                atr=self.get_cell_value('atr', row),
                                glnA=self.get_cell_value('glnA', row),
                                sdhA=self.get_cell_value('sdhA', row),
                                glcK=self.get_cell_value('glcK', row),
                                tkt=self.get_cell_value('tkt', row),
                                twenty_three_S1=self.get_cell_value('twenty_three_S1', row),
                                twenty_three_S3=self.get_cell_value('twenty_three_S3', row),
                                CAT=self.get_cell_value('CAT', row),
                                ERMB=self.get_cell_value('ERMB', row),
                                ERMT=self.get_cell_value('ERMT', row),
                                FOSA=self.get_cell_value('FOSA', row),
                                GYRA=self.get_cell_value('GYRA', row),
                                LNUB=self.get_cell_value('LNUB', row),
                                LSAC=self.get_cell_value('LSAC', row),
                                MEFA=self.get_cell_value('MEFA', row),
                                MPHC=self.get_cell_value('MPHC', row),
                                MSRA=self.get_cell_value('MSRA', row),
                                MSRD=self.get_cell_value('MSRD', row),
                                PARC=self.get_cell_value('PARC', row),
                                RPOBGBS_1=self.get_cell_value('RPOBGBS_1', row),
                                RPOBGBS_2=self.get_cell_value('RPOBGBS_2', row),
                                RPOBGBS_3=self.get_cell_value('RPOBGBS_3', row),
                                RPOBGBS_4=self.get_cell_value('RPOBGBS_4', row),
                                SUL2=self.get_cell_value('SUL2', row),
                                TETB=self.get_cell_value('TETB', row),
                                TETL=self.get_cell_value('TETL', row),
                                TETM=self.get_cell_value('TETM', row),
                                TETO=self.get_cell_value('TETO', row),
                                TETS=self.get_cell_value('TETS', row),
                                ALP1=self.get_cell_value('ALP1', row),
                                ALP23=self.get_cell_value('ALP23', row),
                                ALPHA=self.get_cell_value('ALPHA', row),
                                HVGA=self.get_cell_value('HVGA', row),
                                PI1=self.get_cell_value('PI1', row),
                                PI2A1=self.get_cell_value('PI2A1', row),
                                PI2A2=self.get_cell_value('PI2A2', row),
                                PI2B=self.get_cell_value('PI2B', row),
                                RIB=self.get_cell_value('RIB', row),
                                SRR1=self.get_cell_value('SRR1', row),
                                SRR2=self.get_cell_value('SRR2', row),
                                GYRA_variant=self.get_cell_value('GYRA_variant', row),
                                PARC_variant=self.get_cell_value('PARC_variant', row))
            results.append(in_silico_data)
        return results

    def store_in_silico(self):
        if self.__df is not None:
            logger.info("Storing spreadsheet...")
            self.__dao.update_sample_metadata(self.parse_in_silico_data())
        else:
            raise RuntimeError("No spreadsheet is currently loaded. Unable to store.")
