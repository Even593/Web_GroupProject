<<<<<<< HEAD
import datetime
import flask
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from . import db, util, user
=======
import flask
from . import db, util
>>>>>>> master
from .db import WeightRecord

bp_view, bp_api = util.make_module_blueprints("weightchart")
bp_view.name = "weightchart_view"
bp_api.name  = "weightchart_api"


# def read_user_weights(user_id):
#     user_id = flask.g.user._id
#     session = db.db.session
#     qs = session.query(WeightRecord).filter(WeightRecord.user_id == user_id).order_by(WeightRecord.record_date)
#     return [(r.record_date.isoformat(), r.weight_kg) for r in qs.all()]

def summarize_weights(records):
    weights = [w for _, w in records]
    if not weights:
        return {"count": 0, "avg": None, "min": None, "max": None}
    return {
        "count": len(weights),
        "avg": round(sum(weights) / len(weights), 1),
        "min": min(weights),
        "max": max(weights)
    }

<<<<<<< HEAD
@user.route_to_login_if_required
@bp_view.get("/")
=======
@bp_view.get("/")
@util.route_check_login
>>>>>>> master
def view_weight_analysis():
    return flask.render_template("weightchart.html")

@bp_api.get("/data")
def api_weight_analysis_data():
    user_id = flask.g.user._id
    session = db.db.session
    qs = session.query(WeightRecord).filter(WeightRecord.user_id == user_id).order_by(WeightRecord.record_date)
    records = qs.all()
    height = 1.75
    series = []
    for rec in records:
        date = rec.record_date.isoformat()
        weight = rec.weight_kg
        bmi = round(weight / (height ** 2), 1)
        series.append([date, weight, bmi])
    return flask.jsonify({"series": series})