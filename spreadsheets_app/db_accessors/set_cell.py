from flask import request
from sqlalchemy import Table, insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from spreadsheets_app import DATABASE, METADATA
from spreadsheets_app.db_accessors.lookup import lookup
from spreadsheets_app.utils import strict_types


def set_cell():
    schema = request.get_json()
    try:
        sheet_id = schema["sheet_id"]
        column_name = schema["column_name"]
        row_number = schema["row_number"]
        value = schema["value"]
    except KeyError as err:
        return f"invalid request for set cell; could not find key: {err}", 400

    table_name = f"sheet_{sheet_id}"

    # get the relevant table
    try:
        table = Table(table_name, METADATA, autoload_with=DATABASE.engine)
    except SQLAlchemyError as err:
        return f"could not find sheet number {sheet_id}; {err}", 400

    row_number_exist_condition = table.c.row_number == row_number

    # breakpoint()
    # check for look up call:
    if isinstance(value, str) and value.startswith("LOOKUP"):
        try:
            value = lookup(
                table=table,
                sheet_id=sheet_id,
                dest_row_number=row_number,
                dest_col=column_name,
                lookup_string=value,
            )
        except ValueError as err:
            return f"{err}", 400

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
            return f"{err}", 400

        try:
            conn.execute(statement)
            conn.commit()
        except SQLAlchemyError as err:
            return (
                f"could not insert row: {row} into sheet nunmber: {sheet_id}; {err}",
                400,
            )

    return "", 201
