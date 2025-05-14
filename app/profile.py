from . import util
from . import account
from flask import render_template

bp_view, bp_api = util.make_module_blueprints("profile")

@bp_view.get("/", endpoint="")
@account.route_to_login_if_required
def view_profile():
    return render_template("profile.html")