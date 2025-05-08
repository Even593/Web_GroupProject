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

@bp_api.post("/record/insert")
def _bp_api_workout_insert():
    return db.handle_api_insert(WorkoutRecord, flask.request)

@bp_api.get("/record/query")
def _bp_api_workout_query():
    return db.handle_api_query(WorkoutRecord, flask.request)

@bp_api.post("/record/delete")
def _bp_api_workout_delete():
    return db.handle_api_delete(WorkoutRecord, flask.request)
