from spreadsheets_app import APP, DATABASE

# import those to create the routes and the models
from spreadsheets_app import routes, models


def main():
    APP.config.from_object("config.DevConfig")
    DATABASE.init_app(APP)
    with APP.app_context():
        DATABASE.create_all()

    APP.run(host="0.0.0.0", port=int("5000"), debug=True)


if __name__ == "__main__":
    main()
