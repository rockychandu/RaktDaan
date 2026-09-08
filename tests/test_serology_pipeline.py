"""
Unit Tests for Serology & NAT Laboratory Testing Engine (Member 3 & Member 4).
"""

from datetime import date, timedelta
from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.services.serology_testing_engine import SerologyTestingEngine
from app.common.constants import BloodBagStatus


def test_serology_testing_passed(app):
    with app.app_context():
        bag = BloodBag(
            bag_code="BB-SERO-PASS",
            blood_group="A+",
            component_type="Whole Blood",
            volume_ml=450,
            collection_date=date.today(),
            expiry_date=date.today()+timedelta(days=35),
            status=BloodBagStatus.TESTING.value,
            quality_status="UNTESTED"
        )
        db.session.add(bag)
        db.session.commit()

        record = SerologyTestingEngine.submit_lab_test_results(
            bag_id=bag.id,
            hiv_result="NON_REACTIVE",
            hbsag_result="NON_REACTIVE",
            hcv_result="NON_REACTIVE",
            vdrl_result="NON_REACTIVE",
            malaria_result="NON_REACTIVE",
            nat_test_result="NEGATIVE"
        )

        assert record.overall_quality_status == "PASSED"
        db.session.refresh(bag)
        assert bag.quality_status == "PASSED"
        assert bag.status == BloodBagStatus.AVAILABLE.value


def test_serology_testing_reactive_auto_quarantine(app):
    with app.app_context():
        bag = BloodBag(
            bag_code="BB-SERO-FAIL",
            blood_group="O+",
            component_type="Whole Blood",
            volume_ml=450,
            collection_date=date.today(),
            expiry_date=date.today()+timedelta(days=35),
            status=BloodBagStatus.TESTING.value,
            quality_status="UNTESTED"
        )
        db.session.add(bag)
        db.session.commit()

        record = SerologyTestingEngine.submit_lab_test_results(
            bag_id=bag.id,
            hiv_result="REACTIVE", # HIV Positive
            hbsag_result="NON_REACTIVE"
        )

        assert record.overall_quality_status == "FAILED"
        db.session.refresh(bag)
        assert bag.quality_status == "FAILED"
        assert bag.status == BloodBagStatus.QUARANTINED.value
