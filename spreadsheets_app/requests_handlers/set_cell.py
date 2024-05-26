from flask import request
from typing import Tuple
from sqlalchemy.exc import SQLAlchemyError
from spreadsheets_app.db_accessors.lookup import lookup, remove_dependency, backtracking
from spreadsheets_app.db_accessors.cell import update_cell
from spreadsheets_app.db_accessors.sheets import get_sheet


def set_cell() -> Tuple[str, int]:
    schema = request.get_json()
    try:
        sheet_id = schema["sheet_id"]
        column_name = schema["column_name"]
        row_number = schema["row_number"]
        value = schema["value"]
    except KeyError as err:
        return f"invalid request for set cell; could not find key: {err}", 400

    # get the relevant table
    try:
        table = get_sheet(sheet_id)
    except SQLAlchemyError as err:
        return f"could not find sheet number {sheet_id}; {err}", 400

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

    else:
        # check for remove dependency
        remove_dependency(sheet_id, row_number, column_name)

    try:
        update_cell(table, row_number, column_name, value)
        # backtrack for update all dependents
        backtracking(
            sheet=table,
            sheet_id=sheet_id,
            source_row=row_number,
            source_col=column_name,
            value=value,
        )

    except (ValueError, SQLAlchemyError) as err:
        return f"{err}", 400

    return "", 201
