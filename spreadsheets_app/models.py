from sqlalchemy import Table, Column, Integer, Boolean, Float, String, JSON
from spreadsheets_app import DATABASE


class SheetsMetaData(DATABASE.Model):
    """
    This table saves the ids of sheet with their schema.
    Technically, we dont use the schema from herer but it is nice to have.
    we could also store the table name, but I think it is simple to keep as sheet_{id}
    """
    id = Column(Integer, primary_key=True)
    schema = Column(JSON)

    def __init__(self, schema: dict):
        self.schema = schema


class Dependancy(DATABASE.Model):
    """
    This table keep depandancy of the llop up functionality.
    it will be unique by sheet_id, destination row and col, so each cell will be
    depands on max of one other cell.
    """
    sheet_id = Column(Integer, primary_key=True)
    dest_row = Column(Integer, primary_key=True)
    dest_col = Column(String, primary_key=True)
    source_row = Column(Integer)
    source_col = Column(String)

    def __init__(
        self,
        sheet_id: int,
        dest_row: int,
        dest_col: str,
        source_row: int,
        source_col: str,
    ):
        self.sheet_id = sheet_id
        self.dest_row = dest_row
        self.dest_col = dest_col
        self.source_row = source_row
        self.source_col = source_col
        
class ReverseDependent(DATABASE.Model):
    """
    Here we will store cell which other cells depends on.
    This is usefull for case where we change the value of source cell and 
    instead of going over the whole Depandancy table, we can just use one row here.
    It is important to keep those two synchronized. 
    """
    sheet_id = Column(Integer, primary_key=True)
    source_row = Column(Integer, primary_key=True)
    source_col = Column(String, primary_key=True)
    dependents = Column(JSON) # structured as: {row : [cols]}

    def __init__(self, sheet_id : int, source_row : int, source_col : str, dependents : dict):
        self.sheet_id = sheet_id
        self.source_row = source_row
        self.source_col = source_col
        self.dependents = dependents
