"""
Unit Tests for Custom Admin Account Provisioning Service & API.
"""

from app.services.admin_account_management_service import AdminAccountManagementService


def test_custom_admin_account_creation(app):
    with app.app_context():
        # Create custom admin account
        admin = AdminAccountManagementService.create_admin_account(
            name="Dr. Vikram Sharma",
            email="vikram.sharma@raktdaan.com",
            password="Password@123",
            phone="9876543210",
            role="SUPER_ADMIN",
            department="Executive Office",
            employee_id="EMP-2026-099"
        )

        assert admin["name"] == "Dr. Vikram Sharma"
        assert admin["email"] == "vikram.sharma@raktdaan.com"
        assert admin["role"] == "SUPER_ADMIN"
        assert admin["department"] == "Executive Office"
        assert admin["status"] == "ACTIVE"

        # Verify in admin list
        admins = AdminAccountManagementService.list_admin_accounts()
        emails = [a["email"] for a in admins]
        assert "vikram.sharma@raktdaan.com" in emails
