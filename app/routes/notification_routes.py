"""
Internal Notification Center REST API Blueprints (Member 4).
Endpoints: /api/v1/notifications
"""

from flask import Blueprint, request, jsonify
from app.auth.dependencies import require_login, require_admin, get_current_user
from app.services.notification_service import NotificationService

notification_api_bp = Blueprint("notification_api", __name__, url_prefix="/api/v1/notifications")


@notification_api_bp.route("", methods=["GET"])
@require_login
def list_notifications():
    """List and paginate internal notifications."""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    res = NotificationService.get_all_notifications(page, per_page)
    return jsonify(res), 200


@notification_api_bp.route("/unread", methods=["GET"])
@require_login
def get_unread_notifications():
    """Get unread high-priority notifications."""
    notifs = NotificationService.get_unread_notifications()
    return jsonify({"unread_notifications": notifs}), 200


@notification_api_bp.route("/<int:notification_id>/read", methods=["PATCH"])
@require_login
def mark_notification_read(notification_id: int):
    """Mark a notification as read."""
    notif = NotificationService.mark_as_read(notification_id)
    return jsonify(notif.to_dict() if notif else {}), 200


@notification_api_bp.route("/<int:notification_id>/acknowledge", methods=["PATCH"])
@require_admin
def acknowledge_notification(notification_id: int):
    """Acknowledge an alert notification."""
    user = get_current_user()
    notif = NotificationService.acknowledge_notification(notification_id, user.id)
    return jsonify(notif.to_dict() if notif else {}), 200
