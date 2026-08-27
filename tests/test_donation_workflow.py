"""
Unit Tests for Donation Workflow & Blood Bag Creation (Member 3 & Member 4).
"""

from app.services.donor_service import DonorService
from app.services.donation_service import DonationService
from app.common.constants import DonationStatus, BloodBagStatus


def test_full_donation_workflow(app):
    with app.app_context():
        # 1. Register Donor
        payload = {
            "name": "Donation Tester",
            "email": "dontest@example.com",
            "password": "Password@123",
            "phone": "9874444444",
            "date_of_birth": "1991-04-18",
            "gender": "Male",
            "blood_group": "B-",
            "address": "404 Hospital Road",
            "city": "Kolkata",
            "state": "West Bengal",
            "emergency_contact": "9874444445"
        }
        user, donor = DonorService.register_donor(payload)

        # 2. Register Donation Event
        donation = DonationService.create_donation_registration({
            "donor_id": donor.id,
            "collection_center": "Central RaktDaan Center"
        })

        assert donation.donation_code.startswith("DON-")
        assert donation.donation_status == DonationStatus.REGISTERED.value

        # 3. Submit Medical Screening
        donation, screening = DonationService.submit_medical_screening(
            donation.id,
            {
                "weight_kg": 72.0,
                "hemoglobin_level": 14.2,
                "blood_pressure_sys": 122,
                "blood_pressure_dia": 82,
                "pulse_rate": 74,
                "is_passed": True
            }
        )

        assert donation.screening_status == "PASSED"
        assert donation.donation_status == DonationStatus.ELIGIBLE.value

        # 4. Start Procedure
        donation = DonationService.start_donation_procedure(donation.id)
        assert donation.donation_status == DonationStatus.IN_PROGRESS.value

        # 5. Complete Procedure & Auto-create BloodBag
        donation, bag = DonationService.complete_donation_procedure(donation.id, collected_volume_ml=450)
        assert donation.donation_status == DonationStatus.COMPLETED.value
        assert bag.bag_code.startswith("BB-")
        assert bag.blood_group == "B-"
        assert bag.status == BloodBagStatus.COLLECTED.value
        assert donor.last_donation_date is not None
