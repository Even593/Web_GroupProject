import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # general config
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLE = True

class DevelopmentConfig(Config):
    # Developing
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(basedir, "database.db")
    )

class TestingConfig(Config):
    # Config for testing
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SERVER_NAME = "localhost.localdomain:5000"
    PREFERRED_URL_SCHEME = "http"
    CSRF_ENABLE = False


config_mapping = {
    "development": DevelopmentConfig,
    "testing":    TestingConfig,
}