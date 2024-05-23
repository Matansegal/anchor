from sqlalchemy import Table
from sqlalchemy.exc import SQLAlchemyError
from spreadsheets_app import DATABASE, METADATA


def get_sheet_by_id(sheet_id):
    table_name = f"sheet_{sheet_id}"

    # get the relevant table
    try:
        table = Table(table_name, METADATA, autoload_with=DATABASE.engine)
    except SQLAlchemyError as err:
        return f"could not find sheet number {sheet_id}; {err}", 400
