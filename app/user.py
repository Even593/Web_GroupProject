from . import db
from . import util

import re
import enum
import json
import typing
import datetime
import functools

import flask
import flask.typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy import and_

bp_view, bp_api = util.make_module_blueprints("user")

class Gender(enum.IntEnum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2

class Account(db.BaseModel):
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30), unique=True)
    email: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(100), unique=True)
    password: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30))
    gender: sa_orm.Mapped[Gender] = sa_orm.mapped_column(sa.Enum(Gender))
    birthdate: sa_orm.Mapped[datetime.date] = sa_orm.mapped_column(sa.Date)

def route_to_login_if_required(view: flask.typing.RouteCallable):

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if flask.g.user is None:
            return flask.redirect(flask.url_for("user.login"))
        return view(**kwargs)

    return typing.cast(flask.typing.RouteCallable, wrapped_view)

@bp_view.before_app_request
def _load_logged_in_user():
    user_id = flask.session.get("user_id")
    if user_id is None:
        flask.g.user = None
    else:
        flask.g.user = db.db.session.query(Account).filter(Account._id == user_id).scalar()

@bp_view.get("/login", endpoint="login")
def _login():
    return flask.render_template("login.html")

@bp_view.get("/register", endpoint="register")
def _register():
    return flask.render_template("register.html")

#TODO(junyu): do not rely on specific date format, and it should be handled in the front end
def __parse_date(s: str) -> datetime.date:
    pieces = re.split(r'\D+', s)
    if len(pieces) == 3:
        year, month, day = map(int, pieces)
        return datetime.date(year, month, day)
    return datetime.datetime.now().date()

@bp_api.post("/register")
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
                    password=password,
                    gender=Gender.UNKNOWN,
                    birthdate=datetime.date.today()
                )
            )
            db.db.session.commit()
            succeed = True

    return flask.jsonify({"succeed": succeed, "message": message})

@bp_api.post("/login")
def _bp_api_login():
    user: Account | None = None
    params: dict[str, typing.Any] = flask.request.get_json(silent=True)
    if params:
        name = params.get("username")
        password = params.get("password")
        if name and password:
            user = db.db.session.query(Account).where(
                and_(
                    Account.name == name,
                    Account.password == password,
                )
            ).scalar()

    if user:
        flask.session.clear()
        flask.session["user_id"] = user._id
        flask.g.user = user

    return json.dumps({"succeed": (user is not None)})

@bp_api.post("/logout")
def _bp_api_logout():
    flask.g.user = None
    flask.session.clear()
    return json.dumps({"succeed": True})
