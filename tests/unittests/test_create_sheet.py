import unittest
from spreadsheets_app import DATABASE, APP
from spreadsheets_app.utils.create_sheet import create_sheet


class TestCreateSheet(unittest.TestCase):
    def setUp(self):
        APP.testing = True
        APP.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"

        # Create all tables in the test database
        with APP.app_context():
            DATABASE.create_all()

    def tearDown(self):
        # Drop all tables in the test database
        with APP.app_context():
            DATABASE.session.remove()
            DATABASE.drop_all()

    def test_create_sheet_success(self):
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
            self.assertEqual(response.json, {"sheetId": 1})

            response, status_code = create_sheet()
            self.assertEqual(status_code, 201)
            self.assertEqual(response.json, {"sheetId": 2})

    def test_create_sheet_invalid_schema(self):
        # no columns
        with APP.test_request_context(json={}):
            response, status_code = create_sheet()
            self.assertEqual(status_code, 400)
            self.assertEqual(response, "Invalid schema")

        # columns not a list
        with APP.test_request_context(json={"columns": "matan"}):
            response, status_code = create_sheet()
            self.assertEqual(status_code, 400)
            self.assertEqual(response, "Invalid schema")

    def test_create_sheet_key_error(self):
        # no column name
        with APP.test_request_context(json={"columns": [{"type": "String"}]}):
            response, status_code = create_sheet()
            self.assertEqual(status_code, 400)
            self.assertIn("Column should have `name` and `type`.", response)


if __name__ == "__main__":
    unittest.main()
