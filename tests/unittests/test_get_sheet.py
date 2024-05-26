import unittest
from spreadsheets_app.requests_handlers.create_sheet import create_sheet
from spreadsheets_app.requests_handlers.get_sheet import get_sheet_by_id
from tests.utils import send_test_set_cell_request, tear_down_database
from tests import APP, DATABASE


class TestGetSheet(unittest.TestCase):
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
                ]
            }
        ):

            response, status_code = create_sheet()
            self.assertEqual(status_code, 201)
            self.sheet_id = response.json["sheetId"]

        # add two cells in two different rows
        response, status_code = send_test_set_cell_request(self.sheet_id, "col2", 1, 10)
        self.assertEqual(status_code, 201)
        response, status_code = send_test_set_cell_request(self.sheet_id, "col1", 2, "matan")
        self.assertEqual(status_code, 201)

    def tearDown(self):
        tear_down_database()

    def test_get_sheet_valid(self):

        with APP.app_context():
            response, status_code = get_sheet_by_id(self.sheet_id)
            sheet = response.json
            expected_result = {
                f"sheet_{self.sheet_id}": [
                    {"col1": None, "col2": 10, "row_number": 1},
                    {"col1": "matan", "col2": None, "row_number": 2},
                ]
            }

            self.assertEqual(status_code, 201)
            self.assertEqual(sheet, expected_result)

    def test_get_invalid_sheet_id(self):

        with APP.app_context():
            response, status_code = get_sheet_by_id(self.sheet_id + 100)

            # Assert response and status code
            self.assertEqual(status_code, 400)
            self.assertIn("could not find sheet number", response)


if __name__ == "__main__":
    unittest.main()
