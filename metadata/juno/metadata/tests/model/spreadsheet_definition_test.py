import unittest
import json
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition


class TestSpreadsheetDefinition(unittest.TestCase):
    """ Unit test class for the SpreadsheetDefinition class """

    def setUp(self) -> None:
        # Create a test spreadsheet definition using JSON that conforms to the API config file format
        self.under_test = SpreadsheetDefinition(
            2,
            json.loads(
                """
                    {
                        "column_1": {
                            "title": "Column 1 Name",
                            "mandatory": true,
                            "max_length": 10,
                            "regex": "Regex_1",
                            "regex_validation_message": "Validation message 1",
                            "convert_case": {
                                "case": "lower"
                            }
                        },
                        "column_2": {
                            "title": "Column 2 Name",
                            "max_length": 100,
                            "allowed_values": ["val_1", "val_2", "val_3", "val_4"],
                            "convert_case": {
                                "case": "upper",
                                "preserve": ["val_1", "val_3"]
                            }
                        },
                        "column_3": {
                            "title": "Column 3 Name",
                            "mandatory": false
                        }
                    }
                """
            )
        )

    def test_header_row_position(self) -> None:
        self.assertEqual(self.under_test.header_row_position, 2)

    def test_get_column_name(self) -> None:
        self.assertEqual(self.under_test.get_column_name('column_1'), 'Column 1 Name')
        self.assertEqual(self.under_test.get_column_name('column_2'), 'Column 2 Name')
        self.assertEqual(self.under_test.get_column_name('column_3'), 'Column 3 Name')

    def test_get_regex(self) -> None:
        self.assertEqual(self.under_test.get_regex('column_1'), 'Regex_1')
        self.assertIsNone(self.under_test.get_regex('column_2'))

    def test_get_allowed_values(self) -> None:
        self.assertIsNone(self.under_test.get_allowed_values('column_1'))
        self.assertEqual(self.under_test.get_allowed_values('column_2'), ['val_1', 'val_2', 'val_3', 'val_4'])

    def test_get_max_length(self) -> None:
        self.assertEqual(self.under_test.get_max_length('column_1'), 10)
        self.assertEqual(self.under_test.get_max_length('column_2'), 100)

    def test_get_case(self) -> None:
        self.assertEqual(self.under_test.get_case('column_1'), 'lower')
        self.assertEqual(self.under_test.get_case('column_2'), 'upper')
        self.assertIsNone(self.under_test.get_case('column_3'))

    def test_get_case_preserve(self) -> None:
        self.assertEqual(self.under_test.get_case_preserve('column_1'), [])
        self.assertEqual(self.under_test.get_case_preserve('column_2'), ['val_1', 'val_3'])

    def test_get_regex_validation_message(self) -> None:
        self.assertEqual(self.under_test.get_regex_validation_message('column_1'), 'Validation message 1')
        self.assertIsNone(self.under_test.get_regex_validation_message('column_2'))

    def test_is_mandatory(self) -> None:
        self.assertTrue(self.under_test.is_mandatory('column_1'))
        self.assertFalse(self.under_test.is_mandatory('column_2'))
        self.assertFalse(self.under_test.is_mandatory('column_3'))
