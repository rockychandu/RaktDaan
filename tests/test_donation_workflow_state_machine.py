"""
Automated Test Suite for Donation Workflow State Machine & Timeline Event Logging.
"""

import pytest
from app.database.connection import db
from app.database.models.donor import DonorProfile
from app.database.models.donation import DonationRecord
from app.services.donation_workflow_state_machine import DonationStateMachine
from app.services.donor_history_event_service import DonorHistoryEventService


def test_donation_state_machine_valid_transitions(app):
    with app.app_context():
        donor = DonorProfile.query.first()
        if not donor:
            return

        don = DonationRecord(
            donation_code="DON-TEST-FSM-01",
            donor_id=donor.id,
            blood_group=donor.blood_group,
            screening_status="PASSED",
            donation_status="SCREENING_COMPLETED"
        )
        db.session.add(don)
        db.session.commit()

        # SCREENING_COMPLETED -> ELIGIBLE
        res1 = DonationStateMachine.transition(don.id, "ELIGIBLE", staff_user_id=1, remarks="Verified vitals")
        assert res1["new_status"] == "ELIGIBLE"

        # ELIGIBLE -> WAITING_FOR_STAFF
        res2 = DonationStateMachine.transition(don.id, "WAITING_FOR_STAFF", staff_user_id=1)
        assert res2["new_status"] == "WAITING_FOR_STAFF"

        # WAITING_FOR_STAFF -> APPROVED
        res3 = DonationStateMachine.transition(don.id, "APPROVED", staff_user_id=1)
        assert res3["new_status"] == "APPROVED"

        # APPROVED -> COLLECTION_PENDING
        res4 = DonationStateMachine.transition(don.id, "COLLECTION_PENDING", staff_user_id=1)
        assert res4["new_status"] == "COLLECTION_PENDING"

        # COLLECTION_PENDING -> COLLECTED (Auto creates Blood Bag!)
        res5 = DonationStateMachine.transition(don.id, "COLLECTED", staff_user_id=1, volume_ml=450)
        assert res5["new_status"] == "COLLECTED"
        assert res5["blood_bag_code"] is not None
        assert "BB-2026-" in res5["blood_bag_code"]

        # Verify donor history timeline has recorded the events
        history = DonorHistoryEventService.get_donor_chronological_history(donor.id)
        assert len(history) >= 1


def test_donation_state_machine_invalid_transition(app):
    with app.app_context():
        donor = DonorProfile.query.first()
        if not donor:
            return

        don = DonationRecord(
            donation_code="DON-TEST-FSM-ERR",
            donor_id=donor.id,
            blood_group=donor.blood_group,
            screening_status="PASSED",
            donation_status="SCREENING_COMPLETED"
        )
        db.session.add(don)
        db.session.commit()

        # Cannot jump directly from SCREENING_COMPLETED to COMPLETED!
        with pytest.raises(ValueError):
            DonationStateMachine.transition(don.id, "COMPLETED")
