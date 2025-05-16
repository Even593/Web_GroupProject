from __future__ import annotations

import os
import hmac
import json
import typing
import hashlib
import functools

import flask
import itsdangerous

# CSRF configuration constants
__CSRF_TIME_LIMIT = 3600
__CSRF_GLOBAL_NAME = "csrf_token"
__CSRF_SESSION_NAME = "csrf_token"
__CSRF_HEADER_NAME = "X-CSRFToken"

# Create a pair of Flask Blueprints (view, api) under a given module name
def make_module_blueprints(name: str) -> tuple[flask.Blueprint, flask.Blueprint]:
    def __make(n: str):
        prefix = "/" + name
        return flask.Blueprint(n, __name__, url_prefix=prefix)
    return __make(name), __make(name)

# Store the currently logged-in user in Flask's request context (g)
def set_current_user(user):
    flask.g.user = user

# Retrieve the current user from context, cast to Account model
def get_current_user():
    from . import account
    return typing.cast(account.Account, flask.g.user)

# Decorator to ensure user is logged in; otherwise redirect to login page
def route_check_login(view: flask.typing.RouteCallable):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not get_current_user():
            return flask.redirect(flask.url_for("user.login"))
        return view(**kwargs)
    return typing.cast(flask.typing.RouteCallable, wrapped_view)

# Generate a timed serializer for CSRF tokens
def __csrf_get_serializer():
    return itsdangerous.URLSafeTimedSerializer(flask.current_app.secret_key, salt="wtf-csrf-token")

# Generate or reuse the CSRF token for current session
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

# Verify that the CSRF token is valid and not expired
def csrf_validate_token(data) -> bool:
    # disable CSRF token checking in unit testing
    if not flask.current_app.config.get("CSRF_ENABLE", True):
        return True

    # disable CSRF token in unit testing
    if not flask.g.get("csrf_disable", False):
        return True

    if not data or __CSRF_SESSION_NAME not in flask.session:
        return False

    # the reverse process of token generation
    # https://github.com/pallets-eco/flask-wtf/blob/f09a03177bd3c527d6c5c0b4b7c675089063e40e/src/flask_wtf/csrf.py#L66
    try:
        token = __csrf_get_serializer().loads(data, max_age=__CSRF_TIME_LIMIT)
        return hmac.compare_digest(flask.session[__CSRF_SESSION_NAME], token)
    except (itsdangerous.BadData, itsdangerous.SignatureExpired):
        return False

# Decorator to enforce CSRF token validation on API routes
def route_check_csrf(api: flask.typing.RouteCallable):
    @functools.wraps(api)
    def wrapped_api(**kwargs):
        token = flask.request.headers.get(__CSRF_HEADER_NAME)
        if not csrf_validate_token(token):
            return make_json_response(False)
        return api(**kwargs)
    return typing.cast(flask.typing.RouteCallable, wrapped_api)

# Utility to create a unified JSON response with 'succeed' status
def make_json_response(succeed: bool, **kwargs) -> str:
    result = dict()
    result["succeed"] = succeed
    if kwargs:
        result.update(kwargs)
    return json.dumps(result)
