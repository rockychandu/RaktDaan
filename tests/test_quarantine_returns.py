"""
Unit Tests for Quarantine Isolation & Hospital Returns (Member 4).
"""

from datetime import date, timedelta
from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.services.quarantine_service import QuarantineService
from app.services.return_recall_service import ReturnRecallService
from app.common.constants import BloodBagStatus


def test_quarantine_isolation_and_resolution(app):
    with app.app_context():
        bag = BloodBag(
            bag_code="BB-QRN-TEST01",
            blood_group="B+",
            component_type="Whole Blood",
            volume_ml=450,
            collection_date=date.today(),
            expiry_date=date.today()+timedelta(days=30),
            status=BloodBagStatus.AVAILABLE.value
        )
        db.session.add(bag)
        db.session.commit()

        # 1. Place in Quarantine
        q_record = QuarantineService.place_bag_in_quarantine({
            "bag_id": bag.id,
            "reason": "Serology Re-test Required",
            "suspected_issue": "Faint marker detected"
        }, user_id=1)

        assert q_record.quarantine_code.startswith("QRN-")
        db.session.refresh(bag)
        assert bag.status == BloodBagStatus.QUARANTINED.value

        # 2. Resolve Quarantine (Release back to AVAILABLE)
        resolved = QuarantineService.resolve_quarantine(
            q_record.id,
            {"resolution": "RELEASE_TO_AVAILABLE", "resolution_notes": "Re-test confirmed negative."},
            user_id=1
        )
        assert resolved.status == "RESOLVED_RELEASED"
        db.session.refresh(bag)
        assert bag.status == BloodBagStatus.AVAILABLE.value
