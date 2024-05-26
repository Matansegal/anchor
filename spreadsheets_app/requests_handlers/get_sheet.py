from flask import jsonify, Response
from typing import Tuple
from sqlalchemy.exc import SQLAlchemyError
from spreadsheets_app.db_accessors.sheets import get_sheet, select_all_from_sheet


def get_sheet_by_id(sheet_id) -> Tuple[Response, int]:

    # get the relevant table
    try:
        table = get_sheet(sheet_id)
    except SQLAlchemyError as err:
        return f"could not find sheet number {sheet_id}; {err}", 400

    sheet_data = select_all_from_sheet(table)

    # structure sheet in dict
    sheet = {
        table.name: [
            {col: val for col, val in zip(table.columns.keys(), row)}
            for row in sheet_data
        ]
    }

    return jsonify(sheet), 201
