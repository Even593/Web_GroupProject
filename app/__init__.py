import flask

<<<<<<< Updated upstream
def create_app(config_name: str = "development") -> flask.Flask:

=======
# def create_app() -> flask.Flask:
#     from . import db
#     api = flask.Blueprint("api", __name__, url_prefix="/api")
#     app = flask.Flask(__name__)
#     app.config["SECRET_KEY"] = "dev"
#     app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
#     db.db.init_app(app)

def create_app(config_name: str = "development") -> flask.Flask:

>>>>>>> Stashed changes
    from . import db
    api = flask.Blueprint("api", __name__, url_prefix="/api")
    app = flask.Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    db.db.init_app(app)

    from . import account
    from . import weight
    from . import workout
    from . import analytics
    from . import profile
    from . import weightchart
    from . import leaderboard
    api.register_blueprint(account.bp_api)
    app.register_blueprint(account.bp_view)
    app.register_blueprint(weight.bp_view)
    api.register_blueprint(workout.bp_api)
    app.register_blueprint(workout.bp_view)
    api.register_blueprint(analytics.bp_api)
    app.register_blueprint(analytics.bp_view)
    api.register_blueprint(weightchart.bp_api)
    app.register_blueprint(weightchart.bp_view)
    app.register_blueprint(leaderboard.bp_view)
    app.register_blueprint(api)
    app.register_blueprint(profile.bp_view)

    with app.app_context():
        db.db.create_all()

    # inject CSRF token into all templates via meta tag
    @app.context_processor
    def inject_csrf():
        from .util import csrf_ensure_token
        return {"csrf_token": csrf_ensure_token()}

    @app.route("/", endpoint="/")
    def __index():
        return flask.render_template("index.html")

    @app.errorhandler(Exception)
    def handle_all_exceptions(e):
        import traceback
        traceback.print_exc()
        return flask.jsonify({"succeed": False, "message": str(e)}), 500

    return app
