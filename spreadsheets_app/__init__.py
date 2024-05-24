from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData


APP = Flask(__name__)
DATABASE = SQLAlchemy()
METADATA = MetaData()