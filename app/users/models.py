from enum import Enum

class UserRole(str, Enum):
    """
    Role definitions for the system.
    Strictly enforced - arbitrary role strings are prohibited.
    """
    DONOR = "DONOR"
    ADMIN = "ADMIN"
    REQUESTER = "REQUESTER"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]


class UserStatus(str, Enum):
    """
    Account status lifecycle states.
    """
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    LOCKED = "LOCKED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]


class BloodGroup(str, Enum):
    """
    Standard Human Blood Group Types.
    """
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]


class Gender(str, Enum):
    """
    Gender options for donor profile registration.
    """
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]


class EligibilityStatus(str, Enum):
    """
    Donor blood donation eligibility status.
    """
    ELIGIBLE = "ELIGIBLE"
    TEMPORARILY_INELIGIBLE = "TEMPORARILY_INELIGIBLE"
    PERMANENTLY_INELIGIBLE = "PERMANENTLY_INELIGIBLE"
    UNDER_REVIEW = "UNDER_REVIEW"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]


class AuditActionType(str, Enum):
    """
    Audit and Security Action Log Types.
    """
    USER_REGISTERED = "USER_REGISTERED"
    DONOR_LOGIN_SUCCESS = "DONOR_LOGIN_SUCCESS"
    ADMIN_LOGIN_SUCCESS = "ADMIN_LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    PASSWORD_RESET_REQUESTED = "PASSWORD_RESET_REQUESTED"
    PROFILE_UPDATED = "PROFILE_UPDATED"
    UNAUTHORIZED_ACCESS_ATTEMPT = "UNAUTHORIZED_ACCESS_ATTEMPT"
    SESSION_REVOKED = "SESSION_REVOKED"
    REQUESTER_LOGIN_SUCCESS = "REQUESTER_LOGIN_SUCCESS"
    BLOOD_REQUEST_CREATED = "BLOOD_REQUEST_CREATED"
    BLOOD_REQUEST_UPDATED = "BLOOD_REQUEST_UPDATED"
    BLOOD_REQUEST_STATUS_CHANGED = "BLOOD_REQUEST_STATUS_CHANGED"
