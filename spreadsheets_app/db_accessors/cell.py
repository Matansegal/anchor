from sqlalchemy import Table, select, insert, update
from sqlalchemy.exc import SQLAlchemyError
from typing import Any
from spreadsheets_app import DATABASE
from spreadsheets_app.utils import strict_types

def update_cell(table : Table, sheet_id : int, row_number : int, column_name : str, value : Any):
    row_number_exist_condition = table.c.row_number == row_number
    
    with DATABASE.engine.connect() as conn:
        # check if row_numer exsits
        select_statement = select(table).where(row_number_exist_condition)
        result = conn.execute(select_statement)
        existing_row = result.fetchone()

        if existing_row:
            # if row exists, update it
            row = {column_name: value}
            statement = update(table).values(row).where(row_number_exist_condition)

        else:
            # insert new row
            row = {"row_number": row_number, column_name: value}
            statement = insert(table).values(row)

        try:
            strict_types(row, table)
        except ValueError as err:
            raise ValueError(f"{err}")

        try:
            conn.execute(statement)
            conn.commit()
        except SQLAlchemyError as err:
            raise SQLAlchemyError(f"could not insert row: {row} into sheet nunmber: {sheet_id}; {err}")