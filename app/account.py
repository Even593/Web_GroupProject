# Enable forward type annotations (Python 3.7+ compatibility)
from __future__ import annotations

# Import local modules
from . import db
from . import util

# Standard & third-party imports
import re
import enum
import json
import typing
import datetime

import flask
import flask.typing
import werkzeug.security

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

# Register view and API blueprints under "user" module
bp_view, bp_api = util.make_module_blueprints("user")

# Session key used to store logged-in user ID
__SESSION_KEY_UID = "user_id"

# Enum class for gender field
class Gender(enum.IntEnum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2

# User account database model
class Account(db.BaseModel):
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30), unique=True)
    email: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(100), unique=True)
    password: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(128))
    gender: sa_orm.Mapped[Gender] = sa_orm.mapped_column(sa.Enum(Gender))
    birthdate: sa_orm.Mapped[datetime.date] = sa_orm.mapped_column(sa.Date)

# Load logged-in user from session before each request
@bp_view.before_app_request
def _load_logged_in_user():
    uid = flask.session.get(__SESSION_KEY_UID)
    user = None
    if uid:
        user = db.db.session.query(Account).filter(Account.id == uid).scalar()
    util.set_current_user(user)

# Render login page
@bp_view.get("/login", endpoint="login")
def _login():
    return flask.render_template("login.html")

# Render register page
@bp_view.get("/register", endpoint="register")
def _register():
    return flask.render_template("register.html")

# Utility: Parse a date string to a datetime.date object
# TODO: Move date validation to front-end and support more formats
def __parse_date(s: str) -> datetime.date:
    pieces = re.split(r'\D+', s)
    if len(pieces) == 3:
        year, month, day = map(int, pieces)
        return datetime.date(year, month, day)
    return datetime.datetime.now().date()

# Handle user registration via POST /api/register
@bp_api.post("/register")
@util.route_check_csrf
def _bp_api_register():
    succeed = False
    message = ""
    params = flask.request.get_json(silent=True)
    if params:
        name = params.get("username")
        password = params.get("password")
        email = params.get("email")

        import re
        if not name or not password or not email:
            message = "Missing fields"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            message = "Invalid email format"
        elif db.db.session.query(Account).filter_by(name=name).first():
            message = "Username already exists"
        elif db.db.session.query(Account).filter_by(email=email).first():
            message = "Email already registered"
        else:
            db.db.session.execute(
                sa.insert(Account).values(
                    name=name,
                    email=email,
                    password=werkzeug.security.generate_password_hash(password),
                    gender=Gender.UNKNOWN,
                    birthdate=datetime.date.today()
                )
            )
            db.db.session.commit()
            succeed = True

    return flask.jsonify({"succeed": succeed, "message": message})

# Handle user login via POST /api/login
@bp_api.post("/login")
@util.route_check_csrf
def _bp_api_login():
    def __find_and_check_account(name, password):
        if not name or not password:
            return None

        # passwords are not stored in plain text, so we need to check it specially after retrieving
        account = typing.cast(Account, db.db.session.query(Account).where(Account.name == name).scalar())
        if not account or not werkzeug.security.check_password_hash(account.password, password):
            return None
        return account

    succeed = False
    params = flask.request.get_json(silent=True)
    user = __find_and_check_account(params.get("username"), params.get("password"))
    if user:
        succeed = True
        flask.session.clear()
        flask.session[__SESSION_KEY_UID] = user.id
        util.set_current_user(user)

    return util.make_json_response(succeed)

# Handle logout via POST /api/logout
@bp_api.post("/logout")
@util.route_check_csrf
def _bp_api_logout():
    util.set_current_user(None)
    flask.session.clear()
    return json.dumps({"succeed": True})
