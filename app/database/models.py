from datetime import datetime, timezone
from app.database.connection import db
from app.users.models import UserRole, UserStatus

# Export Base alias for team members who prefer standard SQLAlchemy Base naming
Base = db.Model

class User(db.Model):
    """
    Core User table representing all registered users (Donors and Admins).
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.DONOR.value)
    phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=UserStatus.ACTIVE.value)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # 1-to-1 relationship with DonorProfile
    donor_profile = db.relationship("DonorProfile", backref="user", uselist=False, cascade="all, delete-orphan")

    def to_dict(self, include_profile=True):
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "status": self.status,
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


from app.database.models.donor import DonorProfile  # Re-exported for backwards compatibility
