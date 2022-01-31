from typing import Dict, List, Any

from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition
from metadata.api.database.monocle_database_service import MonocleDatabaseService


class DownloadHandler:
    """ Construct API download response message data structures """

    def __init__(self, dao: MonocleDatabaseService, in_def: SpreadsheetDefinition) -> None:
        self.__dao = dao
        self.__spreadsheet_def = in_def
        self.__field_index = 1

    def _append_to_dict(self, response_dict: {}, key: str, value: str) -> None:
        if value is None:
            value = ''

        response_dict[key] = {
                'order': self.__field_index,
                'title': self.__spreadsheet_def.get_column_name(key),
                'value': value
            }

        self.__field_index += 1

    def get_dao(self):
        return self.__dao
