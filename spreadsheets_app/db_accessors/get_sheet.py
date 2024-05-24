from flask import jsonify
from sqlalchemy import Table, select
from sqlalchemy.exc import SQLAlchemyError
from spreadsheets_app import DATABASE, METADATA


def get_sheet_by_id(sheet_id):
    table_name = f"sheet_{sheet_id}"

    # get the relevant table
    try:
        table = Table(table_name, METADATA, autoload_with=DATABASE.engine)
    except SQLAlchemyError as err:
        return f"could not find sheet number {sheet_id}; {err}", 400

    with DATABASE.engine.connect() as conn:
        # get the whoel sheet order by row number
        select_statement = select(table).order_by("row_number")
        result = conn.execute(select_statement).fetchall()

        # structure sheet in dict
        sheet = {
            table.name: [
                {col: val for col, val in zip(table.columns.keys(), row)}
                for row in result
            ]
        }

    return jsonify(sheet), 201
