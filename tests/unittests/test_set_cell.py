import unittest
from spreadsheets_app.requests_handlers.create_sheet import create_sheet
from spreadsheets_app.requests_handlers.set_cell import set_cell
from tests import APP, DATABASE
from tests.utils import get_cell_from_database, tear_down_database


class TestSetCell(unittest.TestCase):
    def setUp(self):

        # set up the database
        with APP.app_context():
            DATABASE.create_all()

        # create a sheet
        with APP.test_request_context(
            json={
                "columns": [
                    {"name": "col1", "type": "string"},
                    {"name": "col2", "type": "int"},
                    {"name": "col3", "type": "boolean"},
                ]
            }
        ):

            response, status_code = create_sheet()
            self.assertEqual(status_code, 201)
            self.sheet_id = response.json["sheetId"]

    def tearDown(self):
        tear_down_database()

    def test_set_cell_valid(self):
        # Mock set_cell schema
        with APP.test_request_context(
            json={
                "sheet_id": self.sheet_id,
                "column_name": "col2",
                "row_number": 1,
                "value": 10,
            }
        ):

            response, status_code = set_cell()
            # should get empty response
            self.assertEqual(response, "")
            self.assertEqual(status_code, 201)

        # verify that the data was inserted correctly
        result = get_cell_from_database(self.sheet_id, "col2", 1)
        self.assertEqual(result, 10)

        # insert another cell
        with APP.test_request_context(
            json={
                "sheet_id": self.sheet_id,
                "column_name": "col1",
                "row_number": 1,
                "value": "matan",
            }
        ):

            response, status_code = set_cell()
            self.assertEqual(response, "")
            self.assertEqual(status_code, 201)

        # check again that the new cell updated
        result = get_cell_from_database(self.sheet_id, "col1", 1)
        self.assertEqual(result, "matan")
        
        # insert another cell
        with APP.test_request_context(
            json={
                "sheet_id": self.sheet_id,
                "column_name": "col3",
                "row_number": 1,
                "value": True,
            }
        ):

            response, status_code = set_cell()
            self.assertEqual(response, "")
            self.assertEqual(status_code, 201)

        # check again that the new cell updated
        result = get_cell_from_database(self.sheet_id, "col3", 1)
        self.assertEqual(result, True)

    def test_set_cell_invalid_type(self):
        # Mock invalid JSON schema for set_cell
        with APP.test_request_context(
            json={
                "sheet_id": self.sheet_id,
                "column_name": "col2",
                "row_number": 1,
                "value": "invalid_value",  # Should be an int
            }
        ):

            response, status_code = set_cell()

            # Assert response and status code
            self.assertEqual(status_code, 400)
            self.assertIn("Invalid value 'invalid_value' for column", response)

    def test_set_cell_invalid_sheet_id(self):
        # Mock invalid JSON schema for set_cell
        with APP.test_request_context(
            json={
                "sheet_id": self.sheet_id + 100,
                "column_name": "col1",
                "row_number": 1,
                "value": "matan",
            }
        ):

            response, status_code = set_cell()

            # Assert response and status code
            self.assertEqual(status_code, 400)
            self.assertIn("could not find sheet number", response)


if __name__ == "__main__":
    unittest.main()
