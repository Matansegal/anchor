from flask import request
from sqlalchemy import Table, insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from spreadsheets_app import DATABASE, METADATA


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


# type decorator for strict type checking
# I need it since I dont have sqlite>=3.37 where they have the STRICT operator,
# and it looks like sqlalchemy dont support it yet.
# more info https://github.com/sqlalchemy/sqlalchemy/issues/7398
def strict_types(row, table):
    for col_name, value in row.items():
        col_type = table.c[col_name].type.python_type
        if not isinstance(value, col_type):
            raise ValueError(
                f"Invalid value '{value}' for column '{col_name}'. Must be of type {col_type}."
            )
