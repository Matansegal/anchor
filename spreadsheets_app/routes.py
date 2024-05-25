from spreadsheets_app import APP
from spreadsheets_app.requests_handlers.create_sheet import create_sheet
from spreadsheets_app.requests_handlers.set_cell import set_cell
from spreadsheets_app.requests_handlers.get_sheet import get_sheet_by_id


@APP.route("/sheet/createSheet", methods=["POST"])
def create_sheet_endpoint():
    return create_sheet()


@APP.route("/sheet/setCell", methods=["POST"])
def set_cell_endpoint():
    return set_cell()


@APP.route("/sheet/<int:sheetId>", methods=["GET"])
def get_sheet_by_id_endpoint(sheetId):
    return get_sheet_by_id(sheetId)
