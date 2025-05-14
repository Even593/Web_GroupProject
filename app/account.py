from __future__ import annotations

from . import db
from . import util

import re
import enum
import json
import typing
import datetime

import flask
import flask.typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

bp_view, bp_api = util.make_module_blueprints("user")

__SESSION_KEY_UID = "user_id"

class Gender(enum.IntEnum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2

class Account(db.BaseModel):
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30), unique=True)
    password: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30))
    gender: sa_orm.Mapped[Gender] = sa_orm.mapped_column(sa.Enum(Gender))
    birthdate: sa_orm.Mapped[datetime.date] = sa_orm.mapped_column(sa.Date)

@bp_view.before_app_request
def _load_logged_in_user():
    uid = flask.session.get(__SESSION_KEY_UID)
    user = None
    if uid:
        user = db.db.session.query(Account).filter(Account.id == uid).scalar()
    util.set_current_user(user)

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
    params = flask.request.get_json(silent=True)
    if params:
        db.db.session.execute(
            sa.insert(Account).returning(Account).values(
                name=params["username"],
                password=params["password"],
                gender=Gender.MALE,
                birthdate=__parse_date("2025-01-01"),
            )
        )
        db.db.session.commit()
        succeed = True

    #TODO(junyu): error message
    return json.dumps({"succeed": succeed})

@bp_api.post("/login")
def _bp_api_login():
    user = None
    params: dict[str, typing.Any] = flask.request.get_json(silent=True)
    if params:
        name = params.get("username")
        password = params.get("password")
        if name and password:
            user = db.db.session.query(Account).where(
                Account.name == name,
                Account.password == password,
            ).scalar()

    if user:
        flask.session.clear()
        flask.session[__SESSION_KEY_UID] = user.id
        util.set_current_user(user)

    return json.dumps({"succeed": (user is not None)})

@bp_api.post("/logout")
def _bp_api_logout():
    util.set_current_user(None)
    flask.session.clear()
    return json.dumps({"succeed": True})
