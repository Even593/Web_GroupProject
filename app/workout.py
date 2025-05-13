from . import db
from . import util
from . import user

import flask
import datetime

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

bp_view, bp_api = util.make_module_blueprints("workout")

class WorkoutRecord(db.UidMixin, db.BaseModel):
    date: sa_orm.Mapped[datetime.date] = sa_orm.mapped_column(sa.Date)
    notes: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.UnicodeText)
    duration: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer)
    calories: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer)

@user.route_to_login_if_required
@bp_view.get("/", endpoint="")
def _view_workout():
    return flask.render_template("workout.html")

@bp_view.get("/shared")
def view_shared_workouts():
    return flask.render_template("workout_shared.html")

@bp_api.post("/record/insert")
def _bp_api_workout_insert():
    return db.handle_api_insert(WorkoutRecord, flask.request)

@bp_api.get("/record/query")
def _bp_api_workout_query():
    return db.handle_api_query(WorkoutRecord, flask.request)

@bp_api.post("/record/delete")
def _bp_api_workout_delete():
    return db.handle_api_delete(WorkoutRecord, flask.request)

@bp_api.post("/record/share")
def share_workout():
    data = flask.request.get_json()
    from_user = flask.g.user._id
    record_id = data.get("record_id")
    to_user_name = data.get("to_username")

    from .user import Account  # 避免循环引用
    to_user = db.db.session.query(Account).filter_by(name=to_user_name).first()
    if not to_user:
        return flask.jsonify({"succeed": False, "error": "User not found"})

    share = db.SharedWorkout(
        from_user_id=from_user,
        to_user_id=to_user._id,
        record_id=record_id
    )
    db.db.session.add(share)
    db.db.session.commit()
    return flask.jsonify({"succeed": True})

@bp_api.get("/record/shared-with-me")
def shared_with_me():
    user_id = flask.g.user._id

    # 获取所有别人分享给我的 record_id
    shared_ids = db.db.session.query(db.SharedWorkout.record_id).filter_by(to_user_id=user_id).all()
    record_ids = [sid[0] for sid in shared_ids]

    # 查询这些记录，不要再加 uid 筛选了（否则会排除掉别人分享的数据）
    records = db.db.session.query(WorkoutRecord).filter(WorkoutRecord._id.in_(record_ids)).all()

    result = []
    for r in records:
        result.append({
            "id": r._id,
            "date": r.date.strftime("%Y-%m-%d"),
            "duration": r.duration,
            "calories": r.calories,
            "notes": r.notes
        })

    return flask.jsonify({"succeed": True, "result": result})