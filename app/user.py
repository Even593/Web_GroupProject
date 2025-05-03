from . import api
from . import db

import re
import enum
import typing
import datetime
import functools

import flask
import flask.typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

bp = flask.Blueprint("user", __name__, url_prefix="/user")

class Gender(enum.IntEnum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2

class Account(db.IdMixin, db.db.Model):
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30), unique=True)
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

@bp.before_app_request
def _load_logged_in_user():
    user_id = flask.session.get("user_id")
    if user_id is None:
        flask.g.user = None
    else:
        flask.g.user = db.db.session.query(Account).filter(Account._id == user_id).scalar()

@bp.get("/login", endpoint="login")
def _login():
    return flask.render_template("login.html")

@bp.get("/register", endpoint="register")
def _register():
    return flask.render_template("register.html")

#TODO(junyu): do not rely on specific date format, and it should be handled in the front end
def __parse_date(s: str) -> datetime.date:
    pieces = re.split(r'\D+', s)
    if len(pieces) == 3:
        year, month, day = map(int, pieces)
        return datetime.date(year, month, day)
    return datetime.datetime.now().date()

@api.post("/user/register")
def _api_register():
    user = db.db.session.scalar(
        sa.insert(Account).returning(Account).values(
            name=flask.request.form["username"],
            password=flask.request.form["password"],
            gender=Gender.MALE,
            birthdate=__parse_date(flask.request.form["birthday"]),
        )
    )
    db.db.session.commit()

    #TODO(junyu): error message
    return flask.redirect(flask.url_for("user.login"))

@api.post("/user/login")
def _api_login():
    user = db.db.session.query(Account).filter(
        Account.name == flask.request.form["username"],
        Account.password == flask.request.form["password"],
    ).scalar()

    if user:
        user = typing.cast(Account, user)
        flask.session.clear()
        flask.session["user_id"] = user._id
        flask.g.user = user
        return flask.redirect(flask.url_for("/"))
    else:
        return "Failed"

@api.post("/user/logout")
def _api_logout():
    flask.g.user = None
    flask.session.clear()
    return flask.redirect(flask.url_for("/"))