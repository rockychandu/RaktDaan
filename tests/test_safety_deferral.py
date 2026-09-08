"""
Unit Tests for Cross-Matching, Bedside Transfusion Safety, and Deferral Reinstatement (Member 3 & Member 4).
"""

from datetime import date, timedelta
from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.services.cross_match_engine import CrossMatchEngine
from app.services.transfusion_safety_engine import TransfusionSafetyEngine
from app.services.donor_service import DonorService
from app.services.donor_deferral_engine import DonorDeferralEngine
from app.common.constants import BloodBagStatus


def test_cross_match_engine_success(app):
    with app.app_context():
        bag = BloodBag(
            bag_code="BB-XM-PASS",
            blood_group="O-",
            component_type="PRBC",
            volume_ml=280,
            collection_date=date.today(),
            expiry_date=date.today()+timedelta(days=30),
            status=BloodBagStatus.AVAILABLE.value,
            quality_status="PASSED"
        )
        db.session.add(bag)
        db.session.commit()

        res = CrossMatchEngine.perform_cross_match(
            bag_id=bag.id,
            recipient_blood_group="A+", # O- is compatible with A+
            recipient_name="Alice Smith"
        )
        assert res["is_compatible"] is True


def test_bedside_safety_check(app):
    with app.app_context():
        bag = BloodBag(
            bag_code="BB-BEDSIDE-01",
            blood_group="B+",
            component_type="PRBC",
            volume_ml=280,
            collection_date=date.today(),
            expiry_date=date.today()+timedelta(days=25),
            status=BloodBagStatus.AVAILABLE.value,
            quality_status="PASSED"
        )
        db.session.add(bag)
        db.session.commit()

        res = TransfusionSafetyEngine.verify_bedside_safety(
            bag_code="BB-BEDSIDE-01",
            patient_name="Bob Brown",
            patient_blood_group="B+",
            verifier_1_user_id=1,
            verifier_2_user_id=2
        )
        assert res["is_approved"] is True
        assert res["verification_status"] == "APPROVED"


def test_donor_deferral_and_reinstatement(app):
    with app.app_context():
        payload = {
            "name": "Deferred Donor",
            "email": "defdonor@example.com",
            "password": "Password@123",
            "phone": "9879999999",
            "date_of_birth": "1994-02-14",
            "gender": "Male",
            "blood_group": "AB-",
            "address": "909 Safety St",
            "city": "Jaipur",
            "state": "Rajasthan",
            "emergency_contact": "9879999998"
        }
        user, donor = DonorService.register_donor(payload)

        # Apply 0-day deferral (expires today)
        DonorDeferralEngine.apply_temporary_deferral(
            donor_id=donor.id,
            reason="Minor Dental Procedure",
            deferral_days=0
        )

        res = DonorDeferralEngine.evaluate_reinstatement(donor.id)
        assert res["is_reinstated"] is True
        assert res["status"] == "ELIGIBLE"
