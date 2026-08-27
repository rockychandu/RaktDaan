"""
Unit Tests for Automatic Expiry Scanner Engine (Member 4).
"""

from datetime import date, timedelta
from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.services.expiry_engine import ExpiryEngine
from app.common.constants import BloodBagStatus


def test_automatic_expiry_check_and_stock_exclusion(app):
    with app.app_context():
        # Create an expired bag directly in DB
        expired_bag = BloodBag(
            bag_code="BB-TEST-EXP01",
            blood_group="O-",
            component_type="Whole Blood",
            volume_ml=450,
            collection_date=date.today() - timedelta(days=40),
            expiry_date=date.today() - timedelta(days=2), # Expired 2 days ago
            status=BloodBagStatus.AVAILABLE.value
        )
        db.session.add(expired_bag)
        db.session.commit()

        # Run Expiry Engine
        res = ExpiryEngine.run_automatic_expiry_check()

        assert res["transitioned_to_expired"] >= 1
        db.session.refresh(expired_bag)
        assert expired_bag.status == BloodBagStatus.EXPIRED.value
