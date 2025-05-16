from . import util
from flask import render_template

# Register view and API blueprints under the 'profile' module
bp_view, bp_api = util.make_module_blueprints("profile")

# Route: GET /profile/
# This view renders the user's profile page
@bp_view.get("/", endpoint="")
@util.route_check_login
def view_profile():
    return render_template("profile.html")

# Route: GET /profile/friends
# This view renders the user's friends list page
@bp_view.get("/friends", endpoint="friends")
@util.route_check_login
def view_friends():
    """
    Render the friends list page for the current user.
    """
    from . import db
    user_id = util.get_current_user().id
    # Query all friends (mutual relationships)
    friendships = db.db.session.execute(
        db.sa.select(db.Friendship.friend_id)
        .where(db.Friendship.user_id == user_id)
    ).scalars().all()
    # Get friend user info
    friends = []
    if friendships:
        from .account import Account
        friends = db.db.session.query(Account).filter(Account.id.in_(friendships)).all()
    return render_template("friends.html", friends=friends)

# Route: GET /profile/messages
# This view renders the private message page for the current user
@bp_view.get("/messages", endpoint="messages")
@util.route_check_login
def view_messages():
    """
    Render the private messages page for the current user.
    """
    from . import db
    user_id = util.get_current_user().id
    # Query all conversations (distinct friend ids)
    sent = db.db.session.query(db.PrivateMessage.receiver_id).filter(db.PrivateMessage.sender_id == user_id)
    received = db.db.session.query(db.PrivateMessage.sender_id).filter(db.PrivateMessage.receiver_id == user_id)
    friend_ids = set([fid for fid, in sent] + [fid for fid, in received])
    from .account import Account
    friends = db.db.session.query(Account).filter(Account.id.in_(friend_ids)).all() if friend_ids else []
    return render_template("messages.html", friends=friends)