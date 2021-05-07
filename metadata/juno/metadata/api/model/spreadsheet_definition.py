
class SpreadsheetDefinition(dict):
    """ Model class for a spreadsheet definition """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def get_column_name(self, name: str):
        return self[name]['title']

