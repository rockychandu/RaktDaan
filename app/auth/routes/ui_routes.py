from flask import Blueprint, render_template
from sqlalchemy import func
from app.database.connection import db
from app.database.models.user import User
from app.database.models.donor import DonorProfile
from app.database.models.blood_bank import BloodInventory

ui_bp = Blueprint("ui", __name__)

from flask import jsonify

@ui_bp.route("/api/v1/public/stats", methods=["GET"])
def get_public_stats():
    """Returns REAL live database statistics for Homepage counters."""
    from app.database.models.blood_request import BloodRequest
    from app.database.models.emergency_request import EmergencyRequest

    total_donors = DonorProfile.query.filter_by(is_deleted=False).count()
    total_users = User.query.filter_by(is_deleted=False).count()

    total_units_res = db.session.query(func.sum(BloodInventory.units_available)).scalar()
    total_units = int(total_units_res) if total_units_res else 0

    unique_cities_res = db.session.query(func.count(func.distinct(DonorProfile.city))).scalar()
    total_cities = int(unique_cities_res) if unique_cities_res else 0

    active_br = BloodRequest.query.filter(BloodRequest.status.in_(["SUBMITTED", "UNDER_REVIEW", "VERIFIED", "APPROVED", "MATCHING_DONORS", "DONOR_NOTIFIED", "PARTIALLY_FULFILLED"])).count()
    active_er = EmergencyRequest.query.filter(EmergencyRequest.status.in_(["PENDING", "APPROVED", "ACTIVE"])).count()
    active_requests = active_br + active_er

    total_br = BloodRequest.query.count()
    total_er = EmergencyRequest.query.count()
    total_requests = total_br + total_er

    return jsonify({
        "status": "success",
        "data": {
            "total_donors": total_donors,
            "total_users": total_users,
            "total_units": total_units,
            "total_cities": total_cities,
            "active_requests": active_requests,
            "total_requests": total_requests
        }
    }), 200

@ui_bp.route("/")
def index_page():
    """
    Renders main home landing page with REAL live database statistics counts
    and blood donation quotations.
    """
    from app.database.models.blood_request import BloodRequest
    from app.database.models.emergency_request import EmergencyRequest

    total_donors = DonorProfile.query.filter_by(is_deleted=False).count()
    total_users = User.query.filter_by(is_deleted=False).count()

    total_units_res = db.session.query(func.sum(BloodInventory.units_available)).scalar()
    total_units = int(total_units_res) if total_units_res else 0

    unique_cities_res = db.session.query(func.count(func.distinct(DonorProfile.city))).scalar()
    total_cities = int(unique_cities_res) if unique_cities_res else 0

    active_br = BloodRequest.query.filter(BloodRequest.status.in_(["SUBMITTED", "UNDER_REVIEW", "VERIFIED", "APPROVED", "MATCHING_DONORS", "DONOR_NOTIFIED", "PARTIALLY_FULFILLED"])).count()
    active_er = EmergencyRequest.query.filter(EmergencyRequest.status.in_(["PENDING", "APPROVED", "ACTIVE"])).count()
    active_requests = active_br + active_er

    return render_template(
        "index.html",
        total_donors=total_donors,
        total_users=total_users,
        total_units=total_units,
        total_cities=total_cities,
        active_requests=active_requests
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

# --- Member 4 Requester & Blood Request UI Routes ---
@ui_bp.route("/request-blood")
def request_blood_page():
    """Renders 5-Step Blood Request Workflow Page."""
    return render_template("request_blood.html")

@ui_bp.route("/requester/login")
def requester_login_page():
    """Renders Requester Login UI Page."""
    return render_template("requester_login.html")

@ui_bp.route("/requester/register")
def requester_register_page():
    """Renders Requester Registration UI Page."""
    return render_template("requester_register.html")

@ui_bp.route("/requester/dashboard")
def requester_dashboard_page():
    """Renders Requester Dashboard Page."""
    return render_template("requester_dashboard.html")

@ui_bp.route("/request-tracking/<req_id>")
def request_tracking_page(req_id):
    """Renders Request Progress & Tracking Timeline Page."""
    return render_template("request_tracking.html", req_id=req_id)

@ui_bp.route("/request-history")
def request_history_page():
    """Renders Requester History List Page."""
    return render_template("request_history.html")
