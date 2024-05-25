from flask import request, jsonify
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Table, Column, Integer, Boolean, Float, String
from spreadsheets_app import DATABASE, METADATA
from spreadsheets_app.models import SheetsMetaData


TYPE_MAPPING = {
    "boolean": Boolean,
    "int": Integer,
    "double": Float,
    "string": String,
}


def create_sheet():
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
    # dynamically create the table
    table_name = f"sheet_{sheet_id}"

    try:
        table = Table(table_name, METADATA, *columns)
        METADATA.create_all(DATABASE.engine, tables=[table])
    except SQLAlchemyError as err:
        return (
            f"error accur after adding table to the metadata for {schema}; sheet was not created; {err}",
            400,
        )

    return jsonify({"sheetId": sheet_id}), 201


def set_columns_list(schema_columns : List[dict]) -> List[Column]:
    columns = [Column("row_number", Integer, primary_key=True)]
    for col in schema_columns:
        columns.append(Column(col["name"], get_column_type(col["type"]), nullable=True))
    return columns


def save_metadata(columns : List[Column]) -> int:
    sheet = SheetsMetaData(columns)
    DATABASE.session.add(sheet)
    DATABASE.session.commit()
    return sheet.id


def get_column_type(column_type : str) :
    try:
        return TYPE_MAPPING[column_type]
    except KeyError as err:
        raise RuntimeError(f"column type is unrecognized: {err}")