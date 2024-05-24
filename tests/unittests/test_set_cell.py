import unittest
from sqlalchemy import select
from spreadsheets_app import METADATA
from spreadsheets_app.utils.create_sheet import create_sheet
from spreadsheets_app.utils.set_cell import set_cell
from tests import APP, DATABASE


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
                    ]
                }
            ):
                breakpoint()

                response, status_code = create_sheet()
                self.assertEqual(status_code, 201)
                self.sheet_id = response.json["sheetId"]

    def tearDown(self):
        with APP.app_context():
            DATABASE.session.remove()
            # drop all table which createad manualy
            METADATA.drop_all(DATABASE.engine)
            # drop table which created with a model
            DATABASE.drop_all()

    def test_set_cell_valid(self):
        # Mock set_cell schema
        with APP.test_request_context(json={
            "sheet_id": self.sheet_id,
            "column_name": "col2",
            "row_number": 1,
            "value": 10
        }):
            
            response, status_code = set_cell()
            # should get empty response
            self.assertEqual(response, "")
            self.assertEqual(status_code, 201)

        # Verify that the data was inserted correctly
        
        with APP.app_context():
            table_name = f"sheet_{self.sheet_id}"
            table = METADATA.tables[table_name]
            result = DATABASE.session.execute(select(table)).fetchall()
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], (1,None,10))
            
        # insert another cell
        with APP.test_request_context(json={
            "sheet_id": self.sheet_id,
            "column_name": "col1",
            "row_number": 1,
            "value": "matan"
        }):
            
            response, status_code = set_cell()
            self.assertEqual(response, "")
            self.assertEqual(status_code, 201)
        
        with APP.app_context():
            result = DATABASE.session.execute(select(table)).fetchall()
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], (1,"matan",10))
            

    # def test_set_cell_invalid_type(self):
    #     # Mock invalid JSON schema for set_cell
    #     response = self.app.post('/sheet/set_cell', json={
    #         "sheet_id": self.sheet_id,
    #         "column_name": "A",
    #         "row_number": 1,
    #         "value": "invalid_value"  # Should be an int
    #     })

    #     # Assert response and status code
    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn("Invalid value 'invalid_value' for column 'A'", response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
