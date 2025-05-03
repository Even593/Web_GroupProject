import flask

api = flask.Blueprint("api", __name__, url_prefix="/api")

def create_app() -> flask.Flask:
    from . import db
    app = flask.Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    db.db.init_app(app)

    from . import user
    app.register_blueprint(api)
    app.register_blueprint(user.bp)

    with app.app_context():
        db.db.create_all()

    @app.route("/", endpoint="/")
    @user.route_to_login_if_required
    def __index():
        return flask.render_template("index.html")

    return app
