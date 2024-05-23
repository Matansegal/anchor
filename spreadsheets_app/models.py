from spreadsheets_app import DATABASE


class SheetsMetaData(DATABASE.Model):
    id = DATABASE.Column(DATABASE.Integer, primary_key=True)
    schema = DATABASE.Column(DATABASE.JSON)

    def __init__(self, schema):
        self.schema = schema
