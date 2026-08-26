from flask import Blueprint, render_template

ui_bp = Blueprint("ui", __name__)

@ui_bp.route("/")
def index_page():
    """Renders main home portal select page."""
    return render_template("index.html")

@ui_bp.route("/donor/login")
def donor_login_page():
    """Renders Donor Login UI page."""
    return render_template("donor_login.html")

@ui_bp.route("/admin/login")
def admin_login_page():
    """Renders Admin Login UI page."""
    return render_template("admin_login.html")

@ui_bp.route("/register")
def register_page():
    """Renders Donor Registration UI page."""
    return render_template("register.html")

@ui_bp.route("/donor/dashboard")
def donor_dashboard_page():
    """Renders Donor Dashboard UI page."""
    return render_template("donor_dashboard.html")

@ui_bp.route("/admin/dashboard")
def admin_dashboard_page():
    """Renders Admin Dashboard UI page."""
    return render_template("admin_dashboard.html")
