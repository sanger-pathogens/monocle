import logging
import re
from typing import List

import pandas
from flask import current_app as application
from flask import request
from metadata.api.database.monocle_database_service import MonocleDatabaseService
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition
from pandas_schema import Column, Schema
from pandas_schema.validation import (
    CustomElementValidation,
    InListValidation,
    LeadingWhitespaceValidation,
    MatchesPatternValidation,
    TrailingWhitespaceValidation,
)

logger = logging.getLogger()


class _StringLengthValidation(CustomElementValidation):
    """A custom validator class for checking the data frame string lengths"""

    def __init__(self, message: str, max_length: int):
        self.max_length = max_length
        super().__init__(validation=lambda s: len(s) <= self.max_length, message=message)


class UploadHandler:
    """Handle processing of upload spreadsheets"""

    # Allowed file formats
    file_types = {
        "tab": getattr(pandas, "read_csv"),
        "tsv": getattr(pandas, "read_csv"),
        "txt": getattr(pandas, "read_csv"),
    }

    def __init__(self, dao: MonocleDatabaseService, in_def: SpreadsheetDefinition, do_validation: bool) -> None:
        self.__df = None
        self.__dao = dao
        self.__spreadsheet_def = in_def
        self.__do_validation = do_validation
        self.__institutions = None
        self.application = application
        # validation will fail if file extension isn't as expected, when this flag is true
        self.check_file_extension = True
        self.file_delimiter = "\t"

    def data_frame(self):
        return self.__df

    def get_dao(self):
        return self.__dao

    @staticmethod
    def allowed_file_types() -> List[str]:
        """Return a list of allowed file type extensions"""
        return [str(key) for key in UploadHandler.file_types.keys()]

    def is_valid_file_type(self, file: str) -> bool:
        """Check if we can process this file type"""

        # immediately return true if this check is disabled
        if not self.check_file_extension:
            logger.debug("file extension checking disabled")
            return True

        valid = False
        try:
            if file and "." in file:
                suffix = file.split(".")[-1]
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
            if case_setting == "lower":
                val = val.lower()
            elif case_setting == "upper":
                val = val.upper()

            preserved_values = self.__spreadsheet_def.get_case_preserve(column_key)
            if preserved_values:
                for p in preserved_values:
                    regex = re.compile(re.escape(p), re.IGNORECASE)
                    val = regex.sub(p, val)

        return val

    def create_schema(self) -> Schema:
        """Create Pandas schema with all the necessary validation rules read in from config"""
        col_list = []
        for column in self.__spreadsheet_def.keys():
            validators = [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()]

            mandatory_field_flag = self.__spreadsheet_def.is_mandatory(column)

            # Special cases for checking institutions/countries...
            if column == "submitting_institution":
                validators.append(InListValidation([i.name for i in self.__institutions]))
            if column == "country":
                validators.append(InListValidation([i.country for i in self.__institutions]))
            else:
                # Regex validation
                if self.__spreadsheet_def.get_regex(column):
                    validators.append(
                        MatchesPatternValidation(
                            self.__spreadsheet_def.get_regex(column),
                            message=self.__spreadsheet_def.get_regex_validation_message(column),
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
                            "field length is greater than {} characters".format(str(max_len)), max_len
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

        logger.info("Loading spreadsheet {}...".format(file_path))

        # Belt and braces file type check
        if not self.is_valid_file_type(file_path):
            raise RuntimeError("Not an allowed file extension")

        # Load the data to a data frame
        if self.check_file_extension:
            suffix = file_path.split(".")[-1]
            data = self.file_types[suffix](
                file_path, dtype=str, sep=self.file_delimiter, header=self.__spreadsheet_def.header_row_position
            )
        else:
            data = pandas.read_csv(
                file_path, dtype=str, sep=self.file_delimiter, header=self.__spreadsheet_def.header_row_position
            )
        data.fillna("", inplace=True)

        logger.info("Loaded spreadsheet:\n{}".format(data.head()))

        # Display spreadsheet contents for debugging if required
        # for key, value in data.iterrows():
        #     logger.debug("{} {}".format(key, value))

        if self.__do_validation:
            # Get a list of valid institutions and cache them
            self.__institutions = self.__dao.get_institutions(request)
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
