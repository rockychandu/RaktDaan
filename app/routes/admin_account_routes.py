"""
Admin Account Management & Provisioning REST API Blueprint.
"""

import logging
from flask import Blueprint, request, jsonify

from app.schemas.admin_account_schemas import AdminCreateSchema
from app.services.admin_account_management_service import AdminAccountManagementService

logger = logging.getLogger(__name__)

admin_account_api_bp = Blueprint("admin_account_api_bp", __name__, url_prefix="/api/v1/admin-accounts")


@admin_account_api_bp.route("", methods=["GET"])
def list_admins():
    admins = AdminAccountManagementService.list_admin_accounts()
    return jsonify({
        "status": "success",
        "count": len(admins),
        "data": admins
    }), 200


@admin_account_api_bp.route("", methods=["POST"])
def create_admin():
    payload = request.get_json() or {}
    try:
        schema = AdminCreateSchema(**payload)
        admin = AdminAccountManagementService.create_admin_account(
            name=schema.name,
            email=schema.email,
            password=schema.password,
            phone=schema.phone,
            role=schema.role,
            department=schema.department,
            employee_id=schema.employee_id
        )
        return jsonify({
            "status": "success",
            "message": f"New Admin account '{schema.email}' created successfully with role '{schema.role}'.",
            "data": admin
        }), 201
    except Exception as e:
        logger.error(f"Error creating admin account: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@admin_account_api_bp.route("/<int:user_id>/status", methods=["PATCH"])
def update_admin_status(user_id):
    payload = request.get_json() or {}
    status = payload.get("status", "ACTIVE")
    try:
        admin = AdminAccountManagementService.update_admin_status(user_id, status)
        return jsonify({
            "status": "success",
            "message": f"Admin account status updated to '{status}'.",
            "data": admin
        }), 200
    except Exception as e:
        logger.error(f"Error updating admin status: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400
