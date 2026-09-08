"""
Unit Tests for Component Separation Engine (Member 4).
"""

from datetime import date, timedelta
from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.services.component_separation_engine import ComponentSeparationEngine
from app.common.constants import BloodBagStatus, ComponentType


def test_component_separation_workflow(app):
    with app.app_context():
        parent_bag = BloodBag(
            bag_code="BB-PARENT-WB",
            blood_group="B+",
            component_type=ComponentType.WHOLE_BLOOD.value,
            volume_ml=450,
            collection_date=date.today(),
            expiry_date=date.today()+timedelta(days=35),
            status=BloodBagStatus.COLLECTED.value,
            quality_status="PASSED"
        )
        db.session.add(parent_bag)
        db.session.commit()

        record, child_bags = ComponentSeparationEngine.separate_whole_blood(
            parent_bag_id=parent_bag.id,
            technician_user_id=1,
            prbc_volume_ml=280,
            ffp_volume_ml=220,
            platelet_volume_ml=60
        )

        assert record.separation_code.startswith("SEP-")
        assert len(child_bags) == 3
        types = [b.component_type for b in child_bags]
        assert ComponentType.PACKED_RED_BLOOD_CELLS.value in types
        assert ComponentType.FRESH_FROZEN_PLASMA.value in types
        assert ComponentType.PLATELET_CONCENTRATE.value in types
