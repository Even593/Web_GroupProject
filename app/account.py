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

# Handle logout via POST /api/user/logout
@bp_api.post("/logout")
@util.route_check_csrf
def _bp_api_logout():
    util.set_current_user(None)
    flask.session.clear()
    return json.dumps({"succeed": True})

# API endpoint to add a friend (mutual friendship)
@bp_api.post("/add-friend")
@util.route_check_csrf
def api_add_friend():
    """
    Add a friend by username. If both users add each other, friendship is mutual.
    """
    try:
<<<<<<< Updated upstream
=======
        from . import db
>>>>>>> Stashed changes
        params = flask.request.get_json(silent=True)
        if not params or not params.get("username"):
            return flask.jsonify({"succeed": False, "message": "Missing username"})
        current_user = util.get_current_user()
        friend = db.db.session.query(Account).filter_by(name=params["username"]).first()
        if not friend or friend.id == current_user.id:
            return flask.jsonify({"succeed": False, "message": "User not found or invalid"})
        exists = db.db.session.query(db.Friendship).filter_by(user_id=current_user.id, friend_id=friend.id).first()
        if exists:
            return flask.jsonify({"succeed": False, "message": "Already friends or pending mutual"})
        db.db.session.add(db.Friendship(user_id=current_user.id, friend_id=friend.id))
        db.db.session.commit()
        return flask.jsonify({"succeed": True})
    except Exception as e:
        import traceback; traceback.print_exc()
        return flask.jsonify({"succeed": False, "message": str(e)})

# API endpoint to remove a friend
@bp_api.post("/remove-friend")
@util.route_check_csrf
def api_remove_friend():
    """
    Remove a friend by friend_id. Removes both directions if mutual.
    """
    params = flask.request.get_json(silent=True)
    if not params or not params.get("friend_id"):
        return flask.jsonify({"succeed": False, "message": "Missing friend_id"})
    current_user = util.get_current_user()
    friend_id = params["friend_id"]
    # Remove both directions
    db.db.session.query(db.Friendship).filter(
        ((db.Friendship.user_id == current_user.id) & (db.Friendship.friend_id == friend_id)) |
        ((db.Friendship.user_id == friend_id) & (db.Friendship.friend_id == current_user.id))
    ).delete(synchronize_session=False)
    db.db.session.commit()
    return flask.jsonify({"succeed": True})

# API endpoint to get messages with a friend
@bp_api.get("/messages")
@util.route_check_csrf
def api_get_messages():
    """
    Get all messages between the current user and a friend.
    """
    from . import db
    user = util.get_current_user()
    friend_id = flask.request.args.get("friend_id", type=int)
    if not friend_id:
        return flask.jsonify({"succeed": False, "messages": []})
    msgs = db.db.session.query(db.PrivateMessage).filter(
        ((db.PrivateMessage.sender_id == user.id) & (db.PrivateMessage.receiver_id == friend_id)) |
        ((db.PrivateMessage.sender_id == friend_id) & (db.PrivateMessage.receiver_id == user.id))
    ).order_by(db.PrivateMessage.sent_at.asc()).all()
    result = [
        {"content": m.content, "sent_at": m.sent_at.strftime("%Y-%m-%d %H:%M"), "is_me": m.sender_id == user.id}
        for m in msgs
    ]
    return flask.jsonify({"succeed": True, "messages": result})

# API endpoint to send a private message
@bp_api.post("/send-message")
@util.route_check_csrf
def api_send_message():
    """
    Send a private message to a friend.
    """
    from . import db
    user = util.get_current_user()
    params = flask.request.get_json(silent=True)
    receiver_id = params.get("receiver_id")
    content = params.get("content")
    if not receiver_id or not content:
        return flask.jsonify({"succeed": False})
    # Only allow sending to friends
    is_friend = db.db.session.query(db.Friendship).filter_by(user_id=user.id, friend_id=receiver_id).first() and \
                db.db.session.query(db.Friendship).filter_by(user_id=receiver_id, friend_id=user.id).first()
    if not is_friend:
        return flask.jsonify({"succeed": False, "message": "Not friends"})
    msg = db.PrivateMessage(sender_id=user.id, receiver_id=receiver_id, content=content)
    db.db.session.add(msg)
    db.db.session.commit()
    return flask.jsonify({"succeed": True})
