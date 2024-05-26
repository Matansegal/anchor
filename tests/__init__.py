from spreadsheets_app import DATABASE, APP
# import those to create the routes and the models
from spreadsheets_app import routes, models

APP.config.from_object("config.TestConfig")
DATABASE.init_app(APP)
