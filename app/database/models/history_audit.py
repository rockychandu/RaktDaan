"""
Donor History Timeline & Event Sourcing Audit Database Models.
Tracks complete chronological history of health checkups, eligibility transitions,
donation statuses, blood bag linking, and admin verifications.
"""

from datetime import datetime, timezone
from app.database.connection import db
from app.database.base import BaseModelMixin


class DonorHistoryTimeline(db.Model, BaseModelMixin):
    """
    Chronological Event History Ledger for Donors.
    Stores immutable records of every checkup, donation state change, and admin verification.
    """
    __tablename__ = "donor_history_timelines"
    __table_args__ = {'extend_existing': True}


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("donor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False, index=True) # HEALTH_CHECKUP, DONATION_REGISTRATION, COLLECTION, BLOOD_BAG_CREATED, STAFF_VERIFICATION
    event_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    health_checkup_result = db.Column(db.String(20), nullable=True) # PASSED, FAILED
    eligibility_status = db.Column(db.String(30), nullable=False) # ELIGIBLE, TEMPORARILY_DEFERRED, PERMANENTLY_DEFERRED
    reasons_summary = db.Column(db.Text, nullable=True)
    next_eligible_date = db.Column(db.Date, nullable=True)
    
    # Linked Entities
    donation_id = db.Column(db.Integer, db.ForeignKey("donation_records.id", ondelete="SET NULL"), nullable=True, index=True)
    blood_bag_id = db.Column(db.Integer, db.ForeignKey("blood_bags.id", ondelete="SET NULL"), nullable=True, index=True)
    blood_bag_code = db.Column(db.String(50), nullable=True)
    
    # Status Management
    donation_status = db.Column(db.String(40), nullable=False, default="SCREENING_COMPLETED")
    staff_verifier_user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    staff_verification_status = db.Column(db.String(30), default="UNVERIFIED", nullable=False) # UNVERIFIED, VERIFIED, REJECTED
    remarks = db.Column(db.Text, nullable=True)

    # Relationships
    donor_profile = db.relationship("DonorProfile", backref=db.backref("history_timelines", lazy=True, cascade="all, delete-orphan"))

    def to_dict(self):
        return {
            "id": self.id,
            "donor_id": self.donor_id,
            "donor_name": self.donor_profile.user.name if (self.donor_profile and self.donor_profile.user) else None,
            "blood_group": self.donor_profile.blood_group if self.donor_profile else None,
            "event_type": self.event_type,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "health_checkup_result": self.health_checkup_result,
            "eligibility_status": self.eligibility_status,
            "reasons_summary": self.reasons_summary,
            "next_eligible_date": self.next_eligible_date.isoformat() if self.next_eligible_date else None,
            "donation_id": self.donation_id,
            "blood_bag_id": self.blood_bag_id,
            "blood_bag_code": self.blood_bag_code,
            "donation_status": self.donation_status,
            "staff_verifier_user_id": self.staff_verifier_user_id,
            "staff_verification_status": self.staff_verification_status,
            "remarks": self.remarks,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
