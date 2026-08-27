"""
Serology & Nucleic Acid Testing (NAT) Database Models (Member 3 & Member 4).
"""

from datetime import datetime, timezone
from app.database.connection import db
from app.database.base import BaseModelMixin


class SerologyTestRecord(db.Model, BaseModelMixin):
    """
    Laboratory Serology & Transfusion Transmissible Infection (TTI) Testing Log.
    """
    __tablename__ = "serology_test_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    bag_id = db.Column(db.Integer, db.ForeignKey("blood_bags.id", ondelete="CASCADE"), nullable=False, index=True)
    hiv_result = db.Column(db.String(20), nullable=False, default="NON_REACTIVE") # NON_REACTIVE, REACTIVE, INDETERMINATE
    hbsag_result = db.Column(db.String(20), nullable=False, default="NON_REACTIVE") # Hepatitis B
    hcv_result = db.Column(db.String(20), nullable=False, default="NON_REACTIVE") # Hepatitis C
    vdrl_result = db.Column(db.String(20), nullable=False, default="NON_REACTIVE") # Syphilis
    malaria_result = db.Column(db.String(20), nullable=False, default="NON_REACTIVE")
    nat_test_result = db.Column(db.String(20), nullable=False, default="NEGATIVE") # Nucleic Acid Test: NEGATIVE, POSITIVE
    overall_quality_status = db.Column(db.String(20), nullable=False, default="PASSED") # PASSED, FAILED
    tested_by_technician_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    lab_notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "test_code": self.test_code,
            "bag_id": self.bag_id,
            "bag_code": self.blood_bag.bag_code if self.blood_bag else None,
            "hiv_result": self.hiv_result,
            "hbsag_result": self.hbsag_result,
            "hcv_result": self.hcv_result,
            "vdrl_result": self.vdrl_result,
            "malaria_result": self.malaria_result,
            "nat_test_result": self.nat_test_result,
            "overall_quality_status": self.overall_quality_status,
            "tested_by_technician_id": self.tested_by_technician_id,
            "lab_notes": self.lab_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
