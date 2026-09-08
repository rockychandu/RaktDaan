"""
Unit Tests for Subgroup Typing & Extended Rh Phenotyping (Member 3 & Member 4).
"""

from datetime import date, timedelta
from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.services.subgroup_typing_service import SubgroupTypingService


def test_subgroup_typing_evaluation(app):
    with app.app_context():
        bag = BloodBag(
            bag_code="BB-SUBGRP-01",
            blood_group="A+",
            component_type="PRBC",
            volume_ml=280,
            collection_date=date.today(),
            expiry_date=date.today()+timedelta(days=25),
            status="AVAILABLE",
            quality_status="PASSED"
        )
        db.session.add(bag)
        db.session.commit()

        res = SubgroupTypingService.evaluate_subgroup_typing(
            bag_id=bag.id,
            anti_a1_lectin_result="POSITIVE",
            rh_c_antigen=True,
            rh_c_little_antigen=True,
            rh_e_antigen=False,
            rh_e_little_antigen=True,
            kell_antigen_k=False
        )

        assert res["subgroup"] == "A1"
        assert res["rh_phenotype"] == "C+ c+ E- e+"
        assert res["kell_status"] == "K-"
