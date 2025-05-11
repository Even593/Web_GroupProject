import datetime
import flask
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from . import db
from . import user
from . import db, util, user
from .db import WeightRecord

bp_view, bp_api = util.make_module_blueprints("weightchart")
bp_view.name = "weightchart_view"
bp_api.name  = "weightchart_api"


def read_user_weights(user_id):
    user_id = flask.g.user._id
    session = db.db.session
    qs = session.query(WeightRecord).filter(WeightRecord.user_id == user_id).order_by(WeightRecord.record_date)
    return [(r.record_date.isoformat(), r.weight_kg) for r in qs.all()]

def summarize_weights(records):
    """
    计算总记录数、平均体重、最大最小值
    """
    weights = [w for _, w in records]
    if not weights:
        return {"count": 0, "avg": None, "min": None, "max": None}
    return {
        "count": len(weights),
        "avg": round(sum(weights) / len(weights), 1),
        "min": min(weights),
        "max": max(weights)
    }

@user.route_to_login_if_required
@bp_view.get("/")
def view_weight_analysis():
    return flask.render_template("weightchart.html")

@bp_api.get("/data")
def api_weight_analysis_data():
    user_id = flask.g.user._id
    records = read_user_weights(user_id)
    summary = summarize_weights(records)
    return flask.jsonify({
        "series": records,
        "summary": summary
    })