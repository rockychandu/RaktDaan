"""
Unit Tests for Hospital Emergency Request Allocation (Member 4).
"""

from datetime import date, timedelta
from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.services.hospital_order_fulfillment_service import HospitalOrderFulfillmentService, OrderPriority
from app.common.constants import BloodBagStatus


def test_emergency_stat_allocation_exact(app):
    with app.app_context():
        bag = BloodBag(
            bag_code="BB-EMERGENCY-01",
            blood_group="AB-",
            component_type="PRBC",
            volume_ml=280,
            collection_date=date.today(),
            expiry_date=date.today()+timedelta(days=20),
            status=BloodBagStatus.AVAILABLE.value,
            quality_status="PASSED"
        )
        db.session.add(bag)
        db.session.commit()

        res = HospitalOrderFulfillmentService.evaluate_emergency_allocation(
            hospital_name="Apollo Emergency Hospital",
            patient_name="Severe Trauma Patient",
            requested_blood_group="AB-",
            requested_units=1,
            component_type="PRBC",
            priority=OrderPriority.EMERGENCY_STAT
        )

        assert res["is_fully_fulfilled"] is True
        assert "BB-EMERGENCY-01" in res["allocated_bag_codes"]
