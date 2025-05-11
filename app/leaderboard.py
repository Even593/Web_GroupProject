# app/leaderboard.py

import datetime
import flask
from . import util, user
from . import db
from .workout import WorkoutRecord

# Create view Blueprint for leaderboard
bp_view, _ = util.make_module_blueprints("leaderboard")

@user.route_to_login_if_required
@bp_view.get("/", endpoint="")
def view_leaderboard():

    # Today's date
    today = datetime.date.today()

    # Query today's workout records
    session = db.db.session
    records = (
        session.query(WorkoutRecord)
        .filter(WorkoutRecord.date == today)
        .all()
    )

    # Aggregate calories per user (uid foreign key)
    cal_by_user = {}
    for rec in records:
        uid = rec.uid
        try:
            kcal = float(rec.calories)
        except (TypeError, ValueError):
            continue
        cal_by_user[uid] = cal_by_user.get(uid, 0) + kcal

    # Sort and take top 10
    top10 = sorted(cal_by_user.items(), key=lambda x: x[1], reverse=True)[:10]

    return flask.render_template("leaderboard.html", leaderboard=top10)