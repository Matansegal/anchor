import unittest
from unittest.mock import patch
from sqlalchemy import Column, Integer, MetaData, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from spreadsheets_app.routes import create_sheet

METADATA = MetaData()
engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# dummy functions
def get_column_type(column_type):
    pass

def save_metadata(schema_columns):
    return 1

class TestCreateSheet(unittest.TestCase):
    def test_create_sheet_invalid_schema(self):
        # Test case for invalid schema
        schema = {}
        response = create_sheet(schema)
        self.assertEqual(response, ('Invalid schema', 400))
        
        schema = {"columns" : "matan"}
        response = create_sheet(schema)
        self.assertEqual(response, ('Invalid schema', 400))

    def test_create_sheet_missing_column_keys(self):
        # Test case for missing column keys
        schema = {'columns': [{'name': 'column1'}]}
        response, status_code = create_sheet(schema)
        self.assertIn("Column should have `name` and `type`.", response)
        self.assertEqual(status_code, 400)

    # @patch('spreadsheets_app.routes.get_column_type')
    @patch('spreadsheets_app.routes.save_metadata', return_value=1)
    def test_create_sheet_success(self, mock_save_metadata):
        # Test case for successful sheet creation
        schema = {'columns': [{'name': 'column1', 'type': 'string'}, {'name': 'column2', 'type': 'int'}]}
        # mock_get_column_type.side_effect = lambda column_type: Integer if column_type == 'integer' else None
        response = create_sheet(schema)
        self.assertEqual(response, ({'sheetId': 1}, 201))

    # @patch('spreadsheets_app.routes.get_column_type')
    # @patch('spreadsheets_app.routes.save_metadata')
    # def test_create_sheet_sqlalchemy_error(self, mock_save_metadata, mock_get_column_type):
    #     # Test case for SQLAlchemy error
    #     schema = {'columns': [{'name': 'column1', 'type': 'string'}, {'name': 'column2', 'type': 'integer'}]}
    #     mock_save_metadata.return_value = 1
    #     mock_get_column_type.side_effect = lambda column_type: Integer if column_type == 'integer' else None
    #     with patch('sqlalchemy.MetaData.create_all') as mock_create_all:
    #         mock_create_all.side_effect = SQLAlchemyError('Test SQLAlchemy error')
    #         response = create_sheet(schema)
    #         self.assertIn('error accur after adding table to the metadata for', response)

if __name__ == '__main__':
    unittest.main()