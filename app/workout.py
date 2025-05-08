from . import util

import os
import csv
from flask import request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from datetime import datetime

bp_view, bp_api = util.make_module_blueprints("workout")

# csv file path
DATA_FILE = os.path.join("app", "user_data", "activity_log.csv")
UPLOAD_FOLDER = os.path.join("app", "static", "uploads")
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp_view.get("/")
def activity_page():
    return render_template("workout.html")

@bp_api.post("/submit")
def add_activity():
    data = {
        "type": request.form.get("type"),
        "date": request.form.get("date"),
        "duration": request.form.get("duration"),
        "distance": request.form.get("distance"),
        "tags": request.form.get("tags"),
        "visibility": request.form.get("visibility"),
        "description": request.form.get("description"),
        "photo": ""
    }

    # save the uploaded image
    photo_file = request.files.get("photo")
    if photo_file and photo_file.filename != "":
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{photo_file.filename}")
        photo_path = os.path.join(UPLOAD_FOLDER, filename)
        photo_file.save(photo_path)
        data["photo"] = f"/static/uploads/{filename}"

    # write csv file
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

    return redirect(url_for("analytics"))