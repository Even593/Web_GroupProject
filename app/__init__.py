import flask
import flask_sqlalchemy
import sqlalchemy.orm as sa_orm

class __ModelBase(sa_orm.DeclarativeBase):
    pass

db = flask_sqlalchemy.SQLAlchemy(model_class=__ModelBase)
api = flask.Blueprint("api", __name__, url_prefix="/api")

def create_app() -> flask.Flask:
    app = flask.Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    db.init_app(app)

    app.register_blueprint(api)

    with app.app_context():
        db.create_all()

    @app.route("/", endpoint="/")
    def __index():
        return "Hello World"

    return app