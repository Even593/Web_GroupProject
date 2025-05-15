from . import util
from flask import render_template

bp_view, bp_api = util.make_module_blueprints("profile")

@bp_view.get("/", endpoint="")
@util.route_check_login
def view_profile():
    return render_template("profile.html")