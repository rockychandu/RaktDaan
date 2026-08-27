"""
Unit Tests for Blood Bag Lifecycle & Traceability Timeline (Member 4).
"""

import pytest
from app.services.donor_service import DonorService
from app.services.donation_service import DonationService
from app.services.blood_bag_service import BloodBagService
from app.common.constants import BloodBagStatus
from app.common.exceptions import InvalidBagStatusTransition


def test_blood_bag_state_transitions_and_timeline(app):
    with app.app_context():
        # Setup Donor & Donation
        payload = {
            "name": "Bag Tester",
            "email": "bagtest@example.com",
            "password": "Password@123",
            "phone": "9875555555",
            "date_of_birth": "1993-09-30",
            "gender": "Female",
            "blood_group": "AB-",
            "address": "505 Lab Lane",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "emergency_contact": "9875555556"
        }
        user, donor = DonorService.register_donor(payload)
        don = DonationService.create_donation_registration({"donor_id": donor.id})
        DonationService.submit_medical_screening(don.id, {"weight_kg": 60, "hemoglobin_level": 13.5, "blood_pressure_sys": 120, "blood_pressure_dia": 80, "pulse_rate": 70, "is_passed": True})
        don, bag = DonationService.complete_donation_procedure(don.id)

        # 1. Transition COLLECTED -> PROCESSING
        bag = BloodBagService.transition_bag_status(bag.id, BloodBagStatus.PROCESSING.value, "Processing whole blood component")
        assert bag.status == BloodBagStatus.PROCESSING.value

        # 2. Transition PROCESSING -> TESTING
        bag = BloodBagService.transition_bag_status(bag.id, BloodBagStatus.TESTING.value, "Lab serology testing")
        assert bag.status == BloodBagStatus.TESTING.value

        # 3. Transition TESTING -> AVAILABLE
        bag = BloodBagService.transition_bag_status(bag.id, BloodBagStatus.AVAILABLE.value, "Passed all lab tests")
        assert bag.status == BloodBagStatus.AVAILABLE.value

        # 4. Attempt Invalid Transition: AVAILABLE -> PROCESSING (Not allowed)
        with pytest.raises(InvalidBagStatusTransition):
            BloodBagService.transition_bag_status(bag.id, BloodBagStatus.PROCESSING.value, "Illegal backwards transition")

        # 5. Verify Traceability Timeline Generation
        timeline = BloodBagService.get_bag_traceability_timeline(bag.id)
        assert timeline["bag_code"] == bag.bag_code
        assert len(timeline["timeline"]) >= 4
