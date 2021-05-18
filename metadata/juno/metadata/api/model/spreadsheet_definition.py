
class SpreadsheetDefinition(dict):
    """ Model class for a spreadsheet definition """

    def __init__(self, spreadsheet_header_row_position: int, *args, **kwargs):
        self.spreadsheet_header_row_position = spreadsheet_header_row_position
        dict.__init__(self, *args, **kwargs)

    @property
    def header_row_position(self):
        return self.spreadsheet_header_row_position

    def get_column_name(self, name: str):
        return self[name]['title']

    def get_regex(self, name: str):
        try:
            return self[name]['regex']
        except KeyError:
            return None

    def get_allowed_values(self, name: str):
        try:
            return self[name]['allowed_values']
        except KeyError:
            return None

    def get_max_length(self, name: str):
        try:
            return int(self[name]['max_length'])
        except KeyError:
            return None

    def is_mandatory(self, name: str):
        try:
            return self[name]['mandatory']
        except KeyError:
            return False

