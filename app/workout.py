from . import db
from . import util

import flask
import datetime

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

# Register front-end and API blueprints for workout module
bp_view, bp_api = util.make_module_blueprints("workout")

# Database model for user workout records
class WorkoutRecord(db.UidMixin, db.BaseModel):
    date: sa_orm.Mapped[datetime.date] = sa_orm.mapped_column(sa.Date)
    notes: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.UnicodeText)
    duration: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer)
    calories: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer)

# Route: GET /workout/ → Render main workout tracking page
@bp_view.get("/", endpoint="")
@util.route_check_login
def _view_workout():
    return flask.render_template("workout.html")

# Route: GET /workout/shared → Render page showing records shared with the user
@bp_view.get("/shared")
def view_shared_workouts():
    return flask.render_template("workout_shared.html")

# Route: POST /workout/record/insert → Add new workout record
@bp_api.post("/record/insert")
@util.route_check_csrf
def _bp_api_workout_insert():
    return db.handle_api_insert(WorkoutRecord, flask.request)

# Route: GET /workout/record/query → Query all workout records of current user
@bp_api.get("/record/query")
@util.route_check_csrf
def _bp_api_workout_query():
    return db.handle_api_query(WorkoutRecord, flask.request)

# Route: POST /workout/record/delete → Delete selected workout records
@bp_api.post("/record/delete")
@util.route_check_csrf
def _bp_api_workout_delete():
    return db.handle_api_delete(WorkoutRecord, flask.request)

# Route: POST /workout/record/share → Share a record with another user
@bp_api.post("/record/share")
def share_workout():
    data = flask.request.get_json()
    from_user = flask.g.user.id
    record_id = data.get("record_id")
    to_user_name = data.get("to_username")
    
    # Lazy import to avoid circular dependency
    from .account import Account  
    to_user = db.db.session.query(Account).filter_by(name=to_user_name).first()
    if not to_user:
        return flask.jsonify({"succeed": False, "error": "User not found"})

    share = db.SharedWorkout(
        from_user_id=from_user,
        to_user_id=to_user.id,
        record_id=record_id
    )
    db.db.session.add(share)
    db.db.session.commit()
    return flask.jsonify({"succeed": True})

# Route: GET /workout/record/shared-with-me → Fetch records others shared with current user
@bp_api.get("/record/shared-with-me")
def shared_with_me():
    user_id = flask.g.user.id

    # Get record IDs shared to this user
    shared_ids = db.db.session.query(db.SharedWorkout.record_id).filter_by(to_user_id=user_id).all()
    record_ids = [sid[0] for sid in shared_ids]

    # Query the actual workout records (skip user-based filtering!)
    records = db.db.session.query(WorkoutRecord).filter(WorkoutRecord.id.in_(record_ids)).all()
    
    # Query the actual workout records (skip user-based filtering!)
    result = []
    for r in records:
        result.append({
            "id": r.id,
            "date": r.date.strftime("%Y-%m-%d"),
            "duration": r.duration,
            "calories": r.calories,
            "notes": r.notes
        })

    return flask.jsonify({"succeed": True, "result": result})
