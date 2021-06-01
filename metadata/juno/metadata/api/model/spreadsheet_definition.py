
class SpreadsheetDefinition(dict):
    """ Model class for a spreadsheet definition """

    def __init__(self, spreadsheet_header_row_position: int, *args, **kwargs):
        self.spreadsheet_header_row_position = spreadsheet_header_row_position
        dict.__init__(self, *args, **kwargs)

    @property
    def header_row_position(self) -> int:
        return self.spreadsheet_header_row_position

    def get_column_name(self, name: str) -> str:
        return self[name]['title']

    def get_regex(self, name: str) -> str:
        try:
            return self[name]['regex']
        except KeyError:
            return None

    def get_allowed_values(self, name: str) -> list:
        try:
            return self[name]['allowed_values']
        except KeyError:
            return None

    def get_max_length(self, name: str) -> int:
        try:
            return int(self[name]['max_length'])
        except KeyError:
            return None

    def get_case(self, name: str) -> str:
        try:
            return self[name]['convert_case']["case"]
        except KeyError:
            return None

    def get_case_preserve(self, name: str) -> list:
        try:
            return self[name]['convert_case']["preserve"]
        except KeyError:
            return []

    def get_regex_validation_message(self, name: str) -> str:
        try:
            return self[name]['regex_validation_message']
        except KeyError:
            return None

    def is_mandatory(self, name: str) -> bool:
        try:
            return self[name]['mandatory']
        except KeyError:
            return False

