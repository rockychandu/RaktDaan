"""
Unit Tests for FEFO Reservation & Hospital Dispatch Workflows (Member 4).
"""

from datetime import date, timedelta
from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.services.reservation_service import ReservationService
from app.services.dispatch_service import DispatchService
from app.common.constants import BloodBagStatus


def test_fefo_reservation_and_dispatch_workflow(app):
    with app.app_context():
        # Create 2 available bags with different expiry dates
        bag1 = BloodBag(bag_code="BB-FEFO-01", blood_group="A+", component_type="Whole Blood", volume_ml=450, collection_date=date.today(), expiry_date=date.today()+timedelta(days=10), status=BloodBagStatus.AVAILABLE.value)
        bag2 = BloodBag(bag_code="BB-FEFO-02", blood_group="A+", component_type="Whole Blood", volume_ml=450, collection_date=date.today(), expiry_date=date.today()+timedelta(days=20), status=BloodBagStatus.AVAILABLE.value)
        db.session.add_all([bag1, bag2])
        db.session.commit()

        # 1. Create FEFO Reservation for 1 unit of A+
        rsv = ReservationService.create_reservation({
            "reference_request_id": "REQ-101",
            "hospital_name": "City Emergency Hospital",
            "patient_name": "John Doe",
            "blood_group": "A+",
            "component_type": "Whole Blood",
            "quantity_units": 1
        })

        assert rsv.reservation_code.startswith("RSV-")
        assert len(rsv.reserved_bags) == 1
        # FEFO strategy selects bag1 (expires in 10 days vs 20 days)
        assert rsv.reserved_bags[0].bag_code == "BB-FEFO-01"
        assert rsv.reserved_bags[0].status == BloodBagStatus.RESERVED.value

        # 2. Create Dispatch
        dsp = DispatchService.create_dispatch({
            "reservation_id": rsv.id,
            "reference_request_id": "REQ-101",
            "hospital_name": "City Emergency Hospital",
            "recipient_patient_name": "John Doe",
            "blood_group": "A+",
            "component_type": "Whole Blood",
            "bag_ids": [bag1.id]
        }, user_id=1)

        assert dsp.dispatch_code.startswith("DSP-")
        assert dsp.status == "COMPLETED"
        db.session.refresh(bag1)
        assert bag1.status == BloodBagStatus.DISPATCHED.value
