from typing import Set, Dict
from app.users.models import UserRole

class Permission:
    # Donor permissions
    READ_OWN_PROFILE = "donor:read_own_profile"
    UPDATE_OWN_PROFILE = "donor:update_own_profile"
    VIEW_DONATION_HISTORY = "donor:view_donation_history"
    CREATE_DONATION_APPOINTMENT = "donor:create_appointment"

    # Admin permissions
    VIEW_ALL_USERS = "admin:view_all_users"
    MANAGE_DONORS = "admin:manage_donors"
    MANAGE_ADMINS = "admin:manage_admins"
    VIEW_SYSTEM_AUDIT_LOGS = "admin:view_audit_logs"
    MANAGE_BLOOD_INVENTORY = "admin:manage_blood_inventory"
    APPROVE_BLOOD_REQUESTS = "admin:approve_requests"
    EXPORT_SYSTEM_REPORTS = "admin:export_reports"


class RBACPermissionMatrix:
    """
    Granular Role-Based Access Control (RBAC) Permission Matrix.
    """

    ROLE_PERMISSIONS: Dict[str, Set[str]] = {
        UserRole.DONOR.value: {
            Permission.READ_OWN_PROFILE,
            Permission.UPDATE_OWN_PROFILE,
            Permission.VIEW_DONATION_HISTORY,
            Permission.CREATE_DONATION_APPOINTMENT,
        },
        UserRole.ADMIN.value: {
            Permission.READ_OWN_PROFILE,
            Permission.UPDATE_OWN_PROFILE,
            Permission.VIEW_ALL_USERS,
            Permission.MANAGE_DONORS,
            Permission.MANAGE_ADMINS,
            Permission.VIEW_SYSTEM_AUDIT_LOGS,
            Permission.MANAGE_BLOOD_INVENTORY,
            Permission.APPROVE_BLOOD_REQUESTS,
            Permission.EXPORT_SYSTEM_REPORTS,
        }
    }

    @classmethod
    def has_permission(cls, role: str, permission: str) -> bool:
        """
        Evaluates whether a given role possesses a specific permission.
        """
        permissions = cls.ROLE_PERMISSIONS.get(role, set())
        return permission in permissions

    @classmethod
    def get_role_permissions(cls, role: str) -> Set[str]:
        """
        Returns all permissions assigned to a role.
        """
        return cls.ROLE_PERMISSIONS.get(role, set()).copy()
