from . import util

import os
import csv
import datetime

import flask

bp_view, bp_api = util.make_module_blueprints("analytics")

ACTIVITY_FILE = os.path.join("app", "user_data", "activity_log.csv")

def read_activities():
    if not os.path.isfile(ACTIVITY_FILE):
        return []
    with open(ACTIVITY_FILE, newline="", encoding="utf-8") as csvfile:
        return list(csv.DictReader(csvfile))

def get_summary():
    activities = read_activities()
    total_distance = 0
    total_duration = 0
    total_calories = 0
    best_5k = None
    longest = 0
    max_cal = 0

    for act in activities:
        try:
            duration = float(act["duration"])
            distance = float(act["distance"] or 0)
            act_type = act["type"]
            total_duration += duration
            total_distance += distance
            kcal = duration * 6 * 55 * 0.0175  # simplified MET algorithm
            total_calories += kcal
            max_cal = max(max_cal, kcal)

            if distance >= 5 and (best_5k is None or duration < best_5k):
                best_5k = duration
            longest = max(longest, distance)
        except:
            continue

    return {
        "total_distance": round(total_distance, 1),
        "total_duration": f"{int(total_duration)//60}h {int(total_duration)%60}m",
        "total_calories": int(total_calories),
        "best_5k": f"{int(best_5k)//60}:{int(best_5k)%60:02}" if best_5k else "—",
        "longest": round(longest, 1),
        "max_cal": int(max_cal)
    }

def get_trend(days=7):
    today = datetime.datetime.today().date()
    history = { (today - datetime.timedelta(days=i)).isoformat(): 0.0 for i in range(days) }
    for act in read_activities():
        try:
            d = datetime.datetime.strptime(act["date"], "%Y-%m-%d").date()
            if (today - d).days < days:
                history[d.isoformat()] += float(act["duration"])
        except:
            continue
    return history

@bp_view.get("/")
def analytics_dashboard():
    return flask.render_template("analytics.html")
