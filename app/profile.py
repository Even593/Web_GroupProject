from . import util
from . import user
from flask import render_template, g
import flask

bp_view, bp_api = util.make_module_blueprints("profile")

@bp_view.get("/", endpoint="")
@user.route_to_login_if_required
def view_profile():
    return render_template("profile.html")