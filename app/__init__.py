import flask

def create_app(config_name: str = "development") -> flask.Flask:

    from . import db
    api = flask.Blueprint("api", __name__, url_prefix="/api")
    app = flask.Flask(__name__)
    from tests.unit.config import config_mapping
    config_class = config_mapping.get(config_name)
    if config_class is None:
        raise ValueError(f"Unknown config name '{config_name}'")
    app.config.from_object(config_class)
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

    return app
