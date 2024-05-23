from spreadsheets_app import APP, DATABASE
# import those to create the routes and the models
from spreadsheets_app import routes, models

with APP.app_context():
    DATABASE.drop_all()
    DATABASE.create_all()
    
    
if __name__ == '__main__':
    APP.run(host="0.0.0.0", port=int("5000"), debug=True)