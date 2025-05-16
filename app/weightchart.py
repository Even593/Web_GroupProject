import flask
from . import db
from . import util
from . import weight

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

@bp_view.get("/")
@util.route_check_login
def view_weight_analysis():
    return flask.render_template("weightchart.html")

@bp_api.get("/data")
def api_weight_analysis_data():
    uid = util.get_current_user().id
    session = db.db.session
    qs = session.query(weight.WeightRecord)\
        .filter(weight.WeightRecord.uid == uid)\
        .order_by(weight.WeightRecord.date)
    records = qs.all()
    height = 1.75
    series = []
    for rec in records:
        date = rec.date.isoformat()
        bmi = round(rec.weight / (height ** 2), 1)
        series.append([date, rec.weight, bmi])
    return flask.jsonify({"series": series})
