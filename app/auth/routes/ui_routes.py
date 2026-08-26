from flask import Blueprint, render_template
from sqlalchemy import func
from app.database.connection import db
from app.database.models.user import User
from app.database.models.donor import DonorProfile
from app.database.models.blood_bank import BloodInventory

ui_bp = Blueprint("ui", __name__)

@ui_bp.route("/")
def index_page():
    """
    Renders main home landing page with REAL live database statistics counts
    and blood donation quotations.
    """
    total_donors = DonorProfile.query.filter_by(is_deleted=False).count()
    total_users = User.query.filter_by(is_deleted=False).count()
    
    # Calculate sum of available blood units from database
    total_units_res = db.session.query(func.sum(BloodInventory.units_available)).scalar()
    total_units = int(total_units_res) if total_units_res else 0

    # Calculate count of unique donor cities from database
    unique_cities_res = db.session.query(func.count(func.distinct(DonorProfile.city))).scalar()
    total_cities = int(unique_cities_res) if unique_cities_res else 0

    return render_template(
        "index.html",
        total_donors=total_donors,
        total_users=total_users,
        total_units=total_units,
        total_cities=total_cities
    )

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
