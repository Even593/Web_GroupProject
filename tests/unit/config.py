import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 所有环境都共享的配置
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    # 开发环境用本地文件
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(basedir, "database.db")
    )

class TestingConfig(Config):
    # 测试环境用内存数据库
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SERVER_NAME = "localhost.localdomain:5000"
    PREFERRED_URL_SCHEME = "http"


config_mapping = {
    "development": DevelopmentConfig,
    "testing":    TestingConfig,
}