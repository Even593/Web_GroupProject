import flask

from app import leaderboard


def create_app() -> flask.Flask:
    from . import db
    api = flask.Blueprint("api", __name__, url_prefix="/api")
    app = flask.Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    db.db.init_app(app)

    from . import user
    from . import weight
    from . import workout
    from . import analytics
    from . import profile
    from . import weightchart
    api.register_blueprint(user.bp_api)
    app.register_blueprint(user.bp_view)
    api.register_blueprint(weight.bp_api)
    app.register_blueprint(weight.bp_view)
    api.register_blueprint(workout.bp_api)
    app.register_blueprint(workout.bp_view)
    api.register_blueprint(analytics.bp_api)
    app.register_blueprint(analytics.bp_view)
    app.register_blueprint(weightchart.bp_api)
    app.register_blueprint(weightchart.bp_view)
    app.register_blueprint(leaderboard.bp_view)
    app.register_blueprint(api)
    app.register_blueprint(profile.bp_view)

    with app.app_context():
        db.db.create_all()

    @app.route("/", endpoint="/")
    @user.route_to_login_if_required
    def __index():
        return flask.render_template("index.html")

    return app
