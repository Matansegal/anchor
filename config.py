class Config:
    pass


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///sheets.sqlite"


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.sqlite"
