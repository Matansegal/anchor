from flask import Flask
from flask_sqlalchemy import SQLAlchemy


APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sheets.sqlite'
DATABASE = SQLAlchemy(APP)