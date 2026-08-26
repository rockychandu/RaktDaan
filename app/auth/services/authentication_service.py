from datetime import datetime, timedelta, timezone
from app.config import Config
from app.database.connection import db
from app.database.models.user import User, UserSession, UserAuditLog
from app.users.models import UserRole, UserStatus, AuditActionType
from app.users.exceptions import SecurityException, AccountLockedException, UnauthorizedRoleException
from app.security.password_policy import PasswordPolicyEngine
from app.security.jwt_manager import JWTManager

class AuthenticationService:
    """
    Enterprise Authentication Service enforcing separate Donor and Admin login workflows,
    failure counter tracking, lockout rules, and audit logging.
    """

    @classmethod
    def authenticate_user(cls, email: str, password: str, expected_role: str, ip_address: str = None, user_agent: str = None) -> dict:
        """
        Authenticates user credentials and role.
        """
        email_clean = email.strip().lower()
        user = User.query.filter_by(email=email_clean, is_deleted=False).first()

        generic_error = SecurityException("Invalid email or password.", status_code=401)

        if not user:
            cls._log_audit_attempt(None, AuditActionType.LOGIN_FAILED.value, f"Failed login attempt for non-existent email: {email_clean}", ip_address)
            raise generic_error

        # Check Lockout status
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise AccountLockedException(f"Account locked due to multiple failed attempts. Try again after {user.locked_until.strftime('%H:%M:%S UTC')}.")

        # Check Account Status
        if user.status != UserStatus.ACTIVE.value:
            raise SecurityException("Account is inactive or suspended. Contact administrator.", status_code=403)

        # Verify Password
        if not PasswordPolicyEngine.verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= Config.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=Config.ACCOUNT_LOCKOUT_MINUTES)
                cls._log_audit_attempt(user.id, AuditActionType.ACCOUNT_LOCKED.value, "Account locked due to brute force threshold reached.", ip_address)
            db.session.commit()
            raise generic_error

        # Role Verification (Donor attempting Admin Login or vice versa)
        if user.role != expected_role:
            cls._log_audit_attempt(user.id, AuditActionType.UNAUTHORIZED_ACCESS_ATTEMPT.value, f"User role mismatch. Attempted {expected_role} login but role is {user.role}.", ip_address)
            raise UnauthorizedRoleException(f"Unauthorized access. Account is not registered as {expected_role.lower()}.")

        # Reset failed login counter on success
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()

        # Issue JWT Token Pair
        tokens = JWTManager.generate_token_pair(user.id, user.role, user.email)

        # Record Active Session
        session_payload = JWTManager.decode_and_verify(tokens["access_token"])
        session = UserSession(
            user_id=user.id,
            session_token_jti=session_payload["jti"],
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.fromtimestamp(session_payload["exp"], tz=timezone.utc)
        )
        db.session.add(session)

        # Audit Log
        action = AuditActionType.DONOR_LOGIN_SUCCESS.value if user.role == UserRole.DONOR.value else AuditActionType.ADMIN_LOGIN_SUCCESS.value
        cls._log_audit_attempt(user.id, action, f"Successful {user.role} login for {user.email}", ip_address)
        db.session.commit()

        return {
            "tokens": tokens,
            "user": user
        }

    @classmethod
    def _log_audit_attempt(cls, user_id: int, action_type: str, description: str, ip_address: str):
        audit = UserAuditLog(
            user_id=user_id,
            action_type=action_type,
            description=description,
            ip_address=ip_address
        )
        db.session.add(audit)
        db.session.commit()
