from __future__ import annotations

import typing

import flask

def make_module_blueprints(name: str) -> tuple[flask.Blueprint, flask.Blueprint]:
    def __make(n: str):
        prefix = "/" + name
        return flask.Blueprint(n, __name__, url_prefix=prefix)
    return __make(name), __make(name)

def set_current_user(user):
    flask.g.user = user

def get_current_user():
    from . import account
    return typing.cast(account.Account, flask.g.user)