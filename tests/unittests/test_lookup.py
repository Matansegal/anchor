import unittest
from spreadsheets_app.requests_handlers.create_sheet import create_sheet
from tests.utils import send_test_set_cell_request, get_cell_from_database, tear_down_database
from tests import APP, DATABASE


class TestLookup(unittest.TestCase):
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
            

    def test_set_cell_lookup_valid(self):
        
        response, status_code = send_test_set_cell_request(self.sheet_id, "col2", 3, "LOOKUP(col2,1)")
        # should get empty response
        self.assertEqual(response, "")
        self.assertEqual(status_code, 201)

        # verify data in cell are matched
        result_row_3 = get_cell_from_database(self.sheet_id,"col2",3)
        result_row_1 = get_cell_from_database(self.sheet_id,"col2",1)
        self.assertEqual(result_row_3, result_row_1, 10)
        
        # change value in row 1 which will change in row 3 as well
        response, status_code = send_test_set_cell_request(self.sheet_id, "col2", 1, 11)
        self.assertEqual(status_code, 201)
        
        # verify data in cell are matched
        result_row_3 = get_cell_from_database(self.sheet_id,"col2",3)
        result_row_1 = get_cell_from_database(self.sheet_id,"col2",1)
        self.assertEqual(result_row_3, result_row_1, 11)
        
        # make cell in row 4 depends on row 3, 
        response, status_code = send_test_set_cell_request(self.sheet_id, "col2", 4, "LOOKUP(col2,3)")
        self.assertEqual(status_code, 201)
        result_row_4 = get_cell_from_database(self.sheet_id,"col2",4)
        result_row_1 = get_cell_from_database(self.sheet_id,"col2",1)
        self.assertEqual(result_row_4, result_row_1, 11)
        
        # change value in row 1 which will change in row 3 and 4, test backtracking
        response, status_code = send_test_set_cell_request(self.sheet_id, "col2", 1, 12)
        self.assertEqual(status_code, 201)
        
        # verify data in cell are matched
        result_row_4 = get_cell_from_database(self.sheet_id,"col2",4)
        result_row_3 = get_cell_from_database(self.sheet_id,"col2",3)
        result_row_1 = get_cell_from_database(self.sheet_id,"col2",1)
        self.assertEqual(result_row_4,result_row_3)
        self.assertEqual(result_row_3, result_row_1, 12)
        
        
    def test_set_cell_lookup_wrong_pattern(self):
        
        response, status_code = send_test_set_cell_request(self.sheet_id, "col2", 3, "LOOKUP(col2)")
        self.assertIn("string starts with 'LOOKUP' but does not match the pattern", response)
        self.assertEqual(status_code, 400)  
        
        response, status_code = send_test_set_cell_request(self.sheet_id, "col2", 3, "LOOKUP(col2,1,2)")
        # will take the second arg as string if "1,2"
        self.assertIn("Given row number in LOOKUP(col,row_number) is not an int.", response)
        self.assertEqual(status_code, 400)  
        
        response, status_code = send_test_set_cell_request(self.sheet_id, "col2", 3, "LOOKUP(col2,1")
        self.assertIn("string starts with 'LOOKUP' but does not match the pattern", response)
        self.assertEqual(status_code, 400)  
          
        
    def test_set_cell_lookup_with_diff_type(self):
        
        # try to make col2 (int) to lookup for cell in col1 (string) 
        response, status_code = send_test_set_cell_request(self.sheet_id, "col2", 3, "LOOKUP(col1,2)")
        self.assertIn("not the same as source column type", response)
        self.assertEqual(status_code, 400)
        
        response, status_code = send_test_set_cell_request(self.sheet_id, "col1", 3, "LOOKUP(col2,1)")
        self.assertIn("not the same as source column type", response)
        self.assertEqual(status_code, 400)
        
        
    def test_set_cell_lookup_with_cyclict_dependent(self):
        _ , status_code = send_test_set_cell_request(self.sheet_id, "col2", 3, "LOOKUP(col2,1)")
        self.assertEqual(status_code, 201)
        _ , status_code = send_test_set_cell_request(self.sheet_id, "col2", 4, "LOOKUP(col2,3)")
        self.assertEqual(status_code, 201)
        # will make (col2,1) -> (col2,3) -> (col2,4) -> (col2,1)
        response , status_code = send_test_set_cell_request(self.sheet_id, "col2", 1, "LOOKUP(col2,4)")
        self.assertEqual(status_code, 400)
        self.assertIn("the given LOOKUP call creates a cyclic path",response)
        



if __name__ == "__main__":
    unittest.main()
