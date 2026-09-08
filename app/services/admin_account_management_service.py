"""
Admin Account Management & Provisioning Service Layer.
Handles custom admin account creation, role assignments, password security hashing,
and account status management.
"""

import logging
import bcrypt
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.user import User, UserAuditLog
from app.users.exceptions import DuplicateUserException, UserNotFoundException

logger = logging.getLogger(__name__)



class AdminAccountManagementService:
    """
    Business Logic Layer for Custom Admin Account Provisioning & Management.
    """

    @staticmethod
    def create_admin_account(
        name: str,
        email: str,
        password: str,
        phone: str,
        role: str = "ADMIN",
        department: Optional[str] = "Blood Inventory",
        employee_id: Optional[str] = None,
        created_by_user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Creates a new Admin user account with custom parameters.
        """
        email_clean = email.lower().strip()

        # Check existing user
        existing = User.query.filter_by(email=email_clean).first()
        if existing:
            raise DuplicateUserException(f"User with email '{email_clean}' already exists.")


        # Hash password using bcrypt
        salt = bcrypt.gensalt()
        pw_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

        new_admin = User(
            name=name.strip(),
            email=email_clean,
            password_hash=pw_hash,
            phone=phone.strip(),
            role=role.upper().strip(),
            status="ACTIVE"
        )
        db.session.add(new_admin)
        db.session.flush()

        # Log Security Audit
        audit = UserAuditLog(
            user_id=new_admin.id,
            action_type="ADMIN_ACCOUNT_CREATED",
            description=f"New Admin Account '{email_clean}' created with role '{role}' (Department: '{department}', EmpID: '{employee_id}')",
            metadata_json=f'{{"role": "{role}", "department": "{department}", "employee_id": "{employee_id}", "created_by": {created_by_user_id}}}'
        )
        db.session.add(audit)
        db.session.commit()

        logger.info(f"Successfully created Admin Account '{email_clean}' (Role: {role}, ID: {new_admin.id})")

        res = new_admin.to_dict()
        res["department"] = department
        res["employee_id"] = employee_id
        return res

    @staticmethod
    def list_admin_accounts() -> List[Dict[str, Any]]:
        """
        Lists all administrative users (ADMIN, SUPER_ADMIN, LAB_STAFF, INVENTORY_MANAGER).
        """
        admin_roles = ["ADMIN", "SUPER_ADMIN", "LAB_STAFF", "INVENTORY_MANAGER"]
        admins = User.query.filter(User.role.in_(admin_roles)).order_by(User.created_at.desc()).all()
        return [a.to_dict() for a in admins]

    @staticmethod
    def update_admin_status(user_id: int, new_status: str) -> Dict[str, Any]:
        """
        Updates account status (ACTIVE, SUSPENDED, DEACTIVATED).
        """
        user = User.query.get(user_id)
        if not user:
            raise UserNotFoundException(f"Admin User ID {user_id} not found.")

        user.status = new_status.upper().strip()
        db.session.commit()
        logger.info(f"Updated Admin User ID {user_id} status to '{user.status}'")
        return user.to_dict()
