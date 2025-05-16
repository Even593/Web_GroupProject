from . import util
from flask import render_template

# Register view and API blueprints under the 'profile' module
bp_view, bp_api = util.make_module_blueprints("profile")

# Route: GET /profile/
# This view renders the user's profile page
@bp_view.get("/", endpoint="")
@util.route_check_login
def view_profile():
    return render_template("profile.html")