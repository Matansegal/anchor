import unittest
from sqlalchemy import select
from spreadsheets_app import METADATA
from spreadsheets_app.requests_handlers.create_sheet import create_sheet
from spreadsheets_app.requests_handlers.set_cell import set_cell
from spreadsheets_app.requests_handlers.get_sheet import get_sheet_by_id
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
            with APP.test_request_context(
                json={
                    "sheet_id": self.sheet_id,
                    "column_name": "col2",
                    "row_number": 1,
                    "value": 10,
                }
            ):

                response, status_code = set_cell()
                self.assertEqual(status_code, 201)

            with APP.test_request_context(
                json={
                    "sheet_id": self.sheet_id,
                    "column_name": "col1",
                    "row_number": 2,
                    "value": "matan",
                }
            ):

                response, status_code = set_cell()
                self.assertEqual(status_code, 201)

    def tearDown(self):
        with APP.app_context():
            DATABASE.session.remove()
            # drop table which created with a model
            DATABASE.drop_all()
            # drop all table which createad manualy
            METADATA.drop_all(DATABASE.engine)
            METADATA.clear()

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
