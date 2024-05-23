from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData


APP = Flask(__name__)
DATABASE_URI = "sqlite:///sheets.sqlite"
APP.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
DATABASE = SQLAlchemy(APP)
METADATA = MetaData()