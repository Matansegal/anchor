from flask import request, jsonify, Response
from typing import Tuple
from sqlalchemy.exc import SQLAlchemyError
from spreadsheets_app.db_accessors.sheets import (
    save_metadata,
    create_table,
    set_columns_list,
)


def create_sheet() -> Tuple[Response, int]:
    schema = request.get_json()

    if "columns" not in schema or not isinstance(schema["columns"], list):
        return "Invalid schema", 400

    schema_columns = schema["columns"]

    # first make sure columns propertly structured
    try:
        columns = set_columns_list(schema_columns)

    except KeyError as err:
        return f"Error creating {schema}; Column should have `name` and `type`.", 400

    except (SQLAlchemyError, RuntimeError) as err:
        return f"Error creating {schema}; {err}", 400

    sheet_id = save_metadata(schema_columns)
    try:
        create_table(sheet_id, columns)
    except SQLAlchemyError as err:
        return (
            f"error accur after adding table to the metadata for {schema}; sheet was not created; {err}",
            400,
        )

    return jsonify({"sheetId": sheet_id}), 201
