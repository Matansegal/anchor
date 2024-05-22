from spreadsheets_app import APP
from spreadsheets_app.utils.create_sheet import create_sheet
        

@APP.route('/sheet', methods=['POST'])
def create_sheet_endpoint():
    return create_sheet()