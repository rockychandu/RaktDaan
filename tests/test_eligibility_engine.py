"""
Unit Tests for Configurable Donor Eligibility Engine (Member 3).
"""

from datetime import date, timedelta
from app.services.donor_service import DonorService
from app.services.eligibility_engine import DonorEligibilityEngine
from app.users.models import EligibilityStatus


def test_donor_eligibility_evaluation_passed(app):
    with app.app_context():
        payload = {
            "name": "Eligible Donor",
            "email": "eligible@example.com",
            "password": "Password@123",
            "phone": "9871111111",
            "date_of_birth": "1996-03-25",
            "gender": "Male",
            "blood_group": "A-",
            "address": "101 Clean Ave",
            "city": "Bengaluru",
            "state": "Karnataka",
            "emergency_contact": "9871111112"
        }
        user, donor = DonorService.register_donor(payload)

        res = DonorEligibilityEngine.evaluate_eligibility(
            donor_id=donor.id,
            weight_kg=68.0,
            hemoglobin_level=14.5,
            bp_sys=120,
            bp_dia=80,
            pulse_rate=72
        )

        assert res["is_eligible"] is True
        assert res["status"] == EligibilityStatus.ELIGIBLE.value


def test_donor_eligibility_underweight_deferred(app):
    with app.app_context():
        payload = {
            "name": "Underweight Donor",
            "email": "underweight@example.com",
            "password": "Password@123",
            "phone": "9872222222",
            "date_of_birth": "1998-07-12",
            "gender": "Female",
            "blood_group": "O+",
            "address": "202 Light St",
            "city": "Hyderabad",
            "state": "Telangana",
            "emergency_contact": "9872222223"
        }
        user, donor = DonorService.register_donor(payload)

        res = DonorEligibilityEngine.evaluate_eligibility(
            donor_id=donor.id,
            weight_kg=44.0, # Underweight < 50 kg
            hemoglobin_level=13.0,
            bp_sys=115,
            bp_dia=75
        )

        assert res["is_eligible"] is False
        assert res["status"] == EligibilityStatus.TEMPORARILY_INELIGIBLE.value
        assert any("below minimum requirement" in r for r in res["reasons"])


def test_donor_donation_interval_check(app):
    with app.app_context():
        payload = {
            "name": "Recent Donor",
            "email": "recentdonor@example.com",
            "password": "Password@123",
            "phone": "9873333333",
            "date_of_birth": "1994-11-05",
            "gender": "Male",
            "blood_group": "AB+",
            "address": "303 Quick St",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "emergency_contact": "9873333334"
        }
        user, donor = DonorService.register_donor(payload)

        # Set last donation date to 20 days ago (< 56 days)
        donor.last_donation_date = date.today() - timedelta(days=20)

        res = DonorEligibilityEngine.evaluate_eligibility(
            donor_id=donor.id,
            weight_kg=70.0,
            hemoglobin_level=15.0
        )

        assert res["is_eligible"] is False
        assert any("Must wait" in r for r in res["reasons"])
