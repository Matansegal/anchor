from spreadsheets_app import DATABASE, APP

APP.config.from_object("config.TestConfig")
DATABASE.init_app(APP)
