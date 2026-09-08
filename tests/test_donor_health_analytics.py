"""
Unit Tests for Donor Health Trajectory & BP Classification (Member 3).
"""

from app.services.donor_service import DonorService
from app.services.donation_service import DonationService
from app.services.donor_health_analytics_engine import DonorHealthAnalyticsEngine


def test_donor_health_analytics(app):
    with app.app_context():
        # Setup donor & screening
        user, donor = DonorService.register_donor({
            "name": "Health Donor",
            "email": "health.donor@example.com",
            "password": "Password@123",
            "phone": "9700001111",
            "date_of_birth": "1992-08-20",
            "gender": "Male",
            "blood_group": "A+",
            "address": "789 Health Rd",
            "city": "Bangalore",
            "state": "Karnataka",
            "emergency_contact": "9700001112"
        })
        don = DonationService.create_donation_registration({"donor_id": donor.id})
        DonationService.submit_medical_screening(don.id, {
            "weight_kg": 75,
            "hemoglobin_level": 14.5,
            "blood_pressure_sys": 118,
            "blood_pressure_dia": 78,
            "pulse_rate": 70,
            "is_passed": True
        })

        analysis = DonorHealthAnalyticsEngine.analyze_donor_health_trajectory(donor.id)
        assert analysis["total_screenings"] == 1
        assert analysis["latest_bp_classification"] == "NORMAL"
        assert analysis["health_score"] == 100
