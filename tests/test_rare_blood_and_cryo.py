"""
Unit Tests for Rare Blood Group Registry & Cryopreservation Archives (Member 3 & Member 4).
"""

from datetime import date, timedelta
from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.services.donor_service import DonorService
from app.services.rare_blood_registry_service import RareBloodRegistryService


def test_rare_blood_registry_and_cryopreservation(app):
    with app.app_context():
        # Setup donor
        user, donor = DonorService.register_donor({
            "name": "Rare Donor",
            "email": "rare.donor@example.com",
            "password": "Password@123",
            "phone": "9800001111",
            "date_of_birth": "1990-05-15",
            "gender": "Female",
            "blood_group": "O-",
            "address": "456 Rare St",
            "city": "Delhi",
            "state": "Delhi",
            "emergency_contact": "9800001112"
        })

        # Register in Rare Phenotype Registry
        rare_reg = RareBloodRegistryService.register_rare_phenotype_donor(
            donor_id=donor.id,
            rare_phenotype_code="BOMBAY_OH",
            antigen_profile_summary="H-antigen negative, anti-H antibodies present in serum",
            registered_by_user_id=1
        )
        assert rare_reg.rare_phenotype_code == "BOMBAY_OH"

        # Setup blood bag
        bag = BloodBag(
            bag_code="BB-RARE-01",
            blood_group="O-",
            component_type="PRBC",
            volume_ml=280,
            collection_date=date.today(),
            expiry_date=date.today()+timedelta(days=35),
            status="AVAILABLE",
            quality_status="PASSED"
        )
        db.session.add(bag)
        db.session.commit()

        # Archive cryopreservation (-80C)
        archive = RareBloodRegistryService.archive_bag_cryopreservation(
            bag_id=bag.id,
            tank_number="TANK-LN2-01",
            canister_position="Canister-A1"
        )
        assert archive.archive_code == "CRYO-BB-RARE-01"
        assert archive.thawing_status == "FROZEN"

        # Thaw deglycerolization
        thaw_res = RareBloodRegistryService.initiate_deglycerolization_thaw(archive.id)
        assert thaw_res["thaw_status"] == "DEGLYCEROLIZED"
        assert thaw_res["ready_for_crossmatch"] is True
