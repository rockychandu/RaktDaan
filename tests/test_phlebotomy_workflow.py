"""
Unit Tests for Phlebotomy Workflow Service (Member 3).
"""

from app.services.donor_service import DonorService
from app.services.donation_service import DonationService
from app.services.phlebotomy_workflow_service import PhlebotomyWorkflowService, PhlebotomyStep


def test_phlebotomy_workflow_execution(app):
    with app.app_context():
        # Setup donor & donation
        user, donor = DonorService.register_donor({
            "name": "Phleb Donor",
            "email": "phleb@example.com",
            "password": "Password@123",
            "phone": "9870001111",
            "date_of_birth": "1993-01-01",
            "gender": "Male",
            "blood_group": "O+",
            "address": "123 Phleb Way",
            "city": "Mumbai",
            "state": "Maharashtra",
            "emergency_contact": "9870001112"
        })
        don = DonationService.create_donation_registration({"donor_id": donor.id})
        DonationService.submit_medical_screening(don.id, {"weight_kg": 70, "hemoglobin_level": 14.0, "blood_pressure_sys": 120, "blood_pressure_dia": 80, "pulse_rate": 72, "is_passed": True})

        # Start Phlebotomy
        res = PhlebotomyWorkflowService.start_phlebotomy_procedure(
            donation_id=don.id,
            phlebotomist_user_id=1,
            vein_score="EXCELLENT"
        )
        assert res["current_step"] == PhlebotomyStep.VENIPUNCTURE
        assert res["vein_score"] == "EXCELLENT"

        # Monitor Progress
        progress = PhlebotomyWorkflowService.monitor_collection_progress(
            donation_id=don.id,
            elapsed_minutes=8.5,
            current_volume_ml=450
        )
        assert progress["is_target_reached"] is True
        assert progress["status_summary"] == "TARGET_VOLUME_REACHED"
