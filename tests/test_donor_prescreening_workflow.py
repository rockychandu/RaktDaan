"""
Unit & Integration Tests for Donor Pre-Donation Health Checkup & Admin Forwarding Workflow.
"""

from app.database.models.donor import DonorProfile
from app.database.models.user import User
from app.database.models.donation import DonationRecord
from app.services.donation_prescreening_service import DonorPrescreeningService


def test_health_checkup_failed(app):
    with app.app_context():
        # Create test donor
        user = User.query.filter_by(email="donor1@example.com").first()
        if not user or not user.donor_profile:
            donor = DonorProfile.query.first()
        else:
            donor = user.donor_profile

        # Submit failing vitals (weight = 42 kg, Hb = 10.0 g/dL)
        res = DonorPrescreeningService.evaluate_and_submit_prescreening(
            donor_profile_id=donor.id,
            weight_kg=42.0,
            hemoglobin_level=10.0,
            blood_pressure_sys=120,
            blood_pressure_dia=80,
            pulse_rate=72,
            temp_celsius=36.6,
            has_chronic_illness=False,
            is_on_medication=False
        )

        assert res["is_passed"] is False
        assert "Sorry, you cannot donate blood" in res["message"]
        assert len(res["reasons"]) >= 2


def test_health_checkup_passed_and_forwarded_to_admin(app):
    with app.app_context():
        donor = DonorProfile.query.first()

        # Submit passing vitals
        res = DonorPrescreeningService.evaluate_and_submit_prescreening(
            donor_profile_id=donor.id,
            weight_kg=68.0,
            hemoglobin_level=14.5,
            blood_pressure_sys=120,
            blood_pressure_dia=80,
            pulse_rate=72,
            temp_celsius=36.6,
            has_chronic_illness=False,
            is_on_medication=False
        )

        assert res["is_passed"] is True
        assert "Health Checkup Passed!" in res["message"]

        # Verify admin pending list includes this donation
        pending = DonorPrescreeningService.get_pending_admin_donations()
        codes = [p["donation_code"] for p in pending]
        assert res["donation_code"] in codes
