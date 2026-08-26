from datetime import datetime, timezone
from app.database.connection import db
from app.database.base import BaseModelMixin
from app.users.models import UserRole, UserStatus

class User(db.Model, BaseModelMixin):
    """
    Core User Account Entity representing all registered users (Donors and Admins).
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.DONOR.value, index=True)
    phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=UserStatus.ACTIVE.value, index=True)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime(timezone=True), nullable=True)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    donor_profile = db.relationship("DonorProfile", backref="user", uselist=False, cascade="all, delete-orphan")
    sessions = db.relationship("UserSession", backref="user", cascade="all, delete-orphan")
    audit_logs = db.relationship("UserAuditLog", backref="user", cascade="all, delete-orphan")
    password_histories = db.relationship("PasswordHistory", backref="user", cascade="all, delete-orphan")

    def to_dict(self, include_profile=True):
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "status": self.status,
            "failed_login_attempts": self.failed_login_attempts,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_profile and self.donor_profile:
            data["donor_profile"] = self.donor_profile.to_dict()
        else:
            data["donor_profile"] = None
        return data

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}' role='{self.role}'>"


class UserSession(db.Model, BaseModelMixin):
    """
    Active User Session Tracking Table.
    """
    __tablename__ = "user_sessions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token_jti = db.Column(db.String(255), unique=True, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class UserAuditLog(db.Model, BaseModelMixin):
    """
    User Action Audit Logging Table.
    """
    __tablename__ = "user_audit_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    action_type = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    metadata_json = db.Column(db.Text, nullable=True)


class PasswordHistory(db.Model, BaseModelMixin):
    """
    Password History Tracking to prevent password recycling.
    """
    __tablename__ = "password_histories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)


class SecurityQuestion(db.Model, BaseModelMixin):
    """
    Security Questions for Account Recovery.
    """
    __tablename__ = "security_questions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question = db.Column(db.String(255), nullable=False)
    answer_hash = db.Column(db.String(255), nullable=False)
