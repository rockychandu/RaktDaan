"""
Volunteer Applications & Blood Drive Registrations REST API.
"""

from flask import Blueprint, request, jsonify
from app.database.connection import db
from app.database.models.notification import InternalNotification
from app.common.constants import NotificationCategory, NotificationPriority

volunteer_api_bp = Blueprint("volunteer_api", __name__, url_prefix="/api/v1")


@volunteer_api_bp.route("/volunteers", methods=["POST"])
def submit_volunteer_application():
    """Submits a new volunteer application."""
    data = request.get_json(silent=True) or {}
    name = data.get("full_name")
    email = data.get("email")
    role = data.get("role", "Blood Drive Volunteer")

    if not name or not email:
        return jsonify({"status": "error", "message": "Full Name and Email are required."}), 400

    notif = InternalNotification(
        title=f"New Volunteer Application: {name}",
        message=f"Volunteer {name} ({email}) applied for role '{role}'.",
        category=NotificationCategory.SYSTEM_ALERT.value,
        priority=NotificationPriority.LOW.value
    )
    db.session.add(notif)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"Thank you {name}! Your volunteer application for '{role}' has been submitted successfully."
    }), 201


@volunteer_api_bp.route("/drives/register", methods=["POST"])
def register_for_blood_drive():
    """Registers a participant for an upcoming donation camp drive."""
    data = request.get_json(silent=True) or {}
    name = data.get("full_name")
    email = data.get("email")
    drive_name = data.get("drive_name", "Voluntary Blood Drive")

    if not name or not email:
        return jsonify({"status": "error", "message": "Full Name and Email are required."}), 400

    notif = InternalNotification(
        title=f"Drive Registration: {name}",
        message=f"Participant {name} ({email}) registered for '{drive_name}'.",
        category=NotificationCategory.IMPORTANT_EVENT.value,
        priority=NotificationPriority.MEDIUM.value
    )
    db.session.add(notif)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"Registration confirmed! See you at '{drive_name}', {name}."
    }), 200
