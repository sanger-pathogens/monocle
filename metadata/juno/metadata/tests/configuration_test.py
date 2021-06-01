import unittest
import tempfile
from flask import Config
from metadata.api.configuration import *
from metadata.api.model.db_connection_config import DbConnectionConfig
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition


class TestConfiguration(unittest.TestCase):
    """ Test class for the configuration module """

    TEST_COL_NAME = 'a_column_name'

    def test_read_database_connection_config(self):
        with tempfile.NamedTemporaryFile('w+t') as tmp:
            tmp.write('[client]\n')
            tmp.write('user = myuser\n')
            tmp.write('password = mypassword\n')
            tmp.write('host = myhost\n')
            tmp.write('port = 1111\n')
            tmp.write('database = mydb')
            tmp.seek(0)
            config = read_database_connection_config(
                Config(None, defaults={'monocle_database_config_file': tmp.name})
            )
            self.assertIsInstance(config, DbConnectionConfig)
            self.assertEqual(config.name, 'monocle')
            self.assertEqual(config.connection_url, 'mysql://myuser:mypassword@myhost:1111/mydb')

    def test_read_database_connection_config_no_password(self):
        with tempfile.NamedTemporaryFile('w+t') as tmp:
            tmp.write('[client]\n')
            tmp.write('user = myuser\n')
            tmp.write('host = myhost\n')
            tmp.write('port = 1111\n')
            tmp.write('database = mydb')
            tmp.seek(0)
            config = read_database_connection_config(
                Config(None, defaults={'monocle_database_config_file': tmp.name})
            )
            self.assertIsInstance(config, DbConnectionConfig)
            self.assertEqual(config.name, 'monocle')
            self.assertEqual(config.connection_url, 'mysql://myuser@myhost:1111/mydb')

    def test_read_spreadsheet_definition_config1(self):
        config = read_spreadsheet_definition_config(
            Config(
                None,
                defaults={
                    "spreadsheet_header_row_position": 2,
                    "spreadsheet_definition": {
                        "a_column_name": {
                            "title": "MyColumn",
                            "regex": "regex1",
                            "allowed_values": ["value1", "value2"],
                            "mandatory": True
                        }
                    }
                }
            )
        )

        self.assertIsInstance(config, SpreadsheetDefinition)
        self.assertEqual(config.header_row_position, 2)
        self.assertEqual(config.get_regex(self.TEST_COL_NAME), 'regex1')
        self.assertEqual(config.get_column_name(self.TEST_COL_NAME), 'MyColumn')
        self.assertEqual(config.get_allowed_values(self.TEST_COL_NAME), ["value1", "value2"])
        self.assertTrue(config.is_mandatory(self.TEST_COL_NAME))

    def test_read_spreadsheet_definition_config2(self):
        """ Check handling of missing json config fields """
        config = read_spreadsheet_definition_config(
            Config(
                None,
                defaults={
                    "spreadsheet_header_row_position": 2,
                    "spreadsheet_definition": {
                        "a_column_name": {
                            "title": "MyColumn"
                        }
                    }
                }
            )
        )

        self.assertIsInstance(config, SpreadsheetDefinition)
        self.assertEqual(config.header_row_position, 2)
        self.assertIsNone(config.get_regex(self.TEST_COL_NAME))
        self.assertEqual(config.get_column_name(self.TEST_COL_NAME), 'MyColumn')
        self.assertIsNone(config.get_allowed_values(self.TEST_COL_NAME))
        self.assertFalse(config.is_mandatory(self.TEST_COL_NAME))

    def test_read_spreadsheet_definition_config3(self):
        """ Check illegal parameter value """
        try:
            read_spreadsheet_definition_config(
                Config(
                    None,
                    defaults={
                        "spreadsheet_header_row_position": "fred",
                        "spreadsheet_definition": {
                            "a_column_name": {
                                "title": "MyColumn"
                            }
                        }
                    }
                )
            )
            self.fail('Expected to get an error raised')
        except ValueError:
            pass
