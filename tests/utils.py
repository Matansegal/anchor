from typing import Any, Tuple
from sqlalchemy import select
from tests import APP, DATABASE
from spreadsheets_app import METADATA
from spreadsheets_app.requests_handlers.set_cell import set_cell

def send_test_set_cell_request(sheet_id: int, col : str, row: int, value: Any) -> Tuple:
    with APP.test_request_context(
        json={
            "sheet_id": sheet_id,
            "column_name": col,
            "row_number": row,
            "value": value,
        }
    ):
        return set_cell()
    
def get_cell_from_database(sheet_id: int, col : str, row : int) -> Any:
    with APP.app_context():
        table_name = f"sheet_{sheet_id}"
        table = METADATA.tables[table_name]
        [result] = DATABASE.session.execute(select(table.c[col]).where(table.c.row_number == row)).fetchone()
        return result

def tear_down_database():
    with APP.app_context():
        DATABASE.session.remove()
        # drop table which created with a model
        DATABASE.drop_all()
        # drop all table which createad manualy
        METADATA.drop_all(DATABASE.engine)
        METADATA.clear()