from __future__ import annotations

import os
import hmac
import json
import typing
import hashlib
import functools

import flask
import itsdangerous

__CSRF_TIME_LIMIT = 3600
__CSRF_GLOBAL_NAME = "csrf_token"
__CSRF_SESSION_NAME = "csrf_token"
__CSRF_HEADER_NAME = "X-CSRFToken"

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

def route_check_login(view: flask.typing.RouteCallable):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not get_current_user():
            return flask.redirect(flask.url_for("user.login"))
        return view(**kwargs)
    return typing.cast(flask.typing.RouteCallable, wrapped_view)

def __csrf_get_serializer():
    return itsdangerous.URLSafeTimedSerializer(flask.current_app.secret_key, salt="wtf-csrf-token")

def csrf_ensure_token():
    def __make_random_hash():
        return hashlib.sha1(os.urandom(64)).hexdigest()

    # reimplement CSRF token from the flask-wtf
    # https://github.com/pallets-eco/flask-wtf/blob/f09a03177bd3c527d6c5c0b4b7c675089063e40e/src/flask_wtf/csrf.py#L23

    if __CSRF_SESSION_NAME not in flask.session:
        flask.session[__CSRF_SESSION_NAME] = __make_random_hash()

    if __CSRF_GLOBAL_NAME not in flask.g:
        s = __csrf_get_serializer()
        try:
            token = s.dumps(flask.session[__CSRF_SESSION_NAME])
        except TypeError:
            flask.session[__CSRF_SESSION_NAME] = __make_random_hash()
            token = s.dumps(flask.session[__CSRF_SESSION_NAME])
        setattr(flask.g, __CSRF_GLOBAL_NAME, token)

    return flask.g.get(__CSRF_GLOBAL_NAME)

def csrf_validate_token(data) -> bool:
    if not data or __CSRF_SESSION_NAME not in flask.session:
        return False

    # the reverse process of token generation
    # https://github.com/pallets-eco/flask-wtf/blob/f09a03177bd3c527d6c5c0b4b7c675089063e40e/src/flask_wtf/csrf.py#L66
    try:
        token = __csrf_get_serializer().loads(data, max_age=__CSRF_TIME_LIMIT)
        return hmac.compare_digest(flask.session[__CSRF_SESSION_NAME], token)
    except (itsdangerous.BadData, itsdangerous.SignatureExpired):
        return False

def route_check_csrf(api: flask.typing.RouteCallable):
    @functools.wraps(api)
    def wrapped_api(**kwargs):
        token = flask.request.headers.get(__CSRF_HEADER_NAME)
        if not csrf_validate_token(token):
            return make_json_response(False)
        return api(**kwargs)
    return typing.cast(flask.typing.RouteCallable, wrapped_api)

def make_json_response(succeed: bool, **kwargs) -> str:
    result = dict()
    result["succeed"] = succeed
    if kwargs:
        result.update(kwargs)
    return json.dumps(result)
