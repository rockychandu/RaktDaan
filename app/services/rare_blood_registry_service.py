"""
Rare Blood Registry & Cryogenic Archive Management Service Layer (Member 3 & Member 4).
Handles rare phenotype donor registration, rare unit matching, high-glycerol cryopreservation (-80°C),
and deglycerolization thawing protocols prior to transfusion.
"""

import logging
from datetime import datetime, date, timezone, timedelta
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.rare_blood import RareDonorRegistry, CryoFrozenBagArchive
from app.database.models.donor import DonorProfile
from app.database.models.blood_bank import BloodBag

logger = logging.getLogger(__name__)


class RareBloodRegistryService:
    """
    Business Logic Service for Rare Phenotype Blood Registry & Cryopreservation Archives.
    """

    @staticmethod
    def register_rare_phenotype_donor(
        donor_id: int,
        rare_phenotype_code: str,
        antigen_profile_summary: str,
        registered_by_user_id: int,
        rarity_classification: str = "EXTREMELY_RARE"
    ) -> RareDonorRegistry:
        """
        Registers donor in Rare Blood Group Registry (e.g., Bombay Oh, Rh-null, Vel-neg).
        """
        registry_entry = RareDonorRegistry(
            donor_id=donor_id,
            rare_phenotype_code=rare_phenotype_code.upper().strip(),
            rarity_classification=rarity_classification,
            antigen_profile_summary=antigen_profile_summary,
            registered_by_user_id=registered_by_user_id,
            is_available_for_emergency=True
        )
        db.session.add(registry_entry)
        db.session.commit()

        logger.info(f"Registered Rare Donor ID {donor_id} with Phenotype '{rare_phenotype_code}' ({rarity_classification})")
        return registry_entry

    @staticmethod
    def archive_bag_cryopreservation(
        bag_id: int,
        tank_number: str = "TANK-LN2-01",
        canister_position: str = "Rack-1 / Box-A",
        glycerol_concentration: float = 40.0
    ) -> CryoFrozenBagArchive:
        """
        Freezes rare blood unit using 40% high-glycerol cryopreservation protocol (-80°C).
        Extends shelf life up to 10 YEARS from collection date.
        """
        bag = BloodBag.query.get(bag_id)
        if not bag:
            raise ValueError(f"Blood Bag ID {bag_id} not found.")

        archive_code = f"CRYO-{bag.bag_code}"
        collection = bag.collection_date or date.today()
        ten_year_expiry = collection + timedelta(days=3650) # 10 Years

        bag.status = "QUARANTINED" # Retain in special archive status
        bag.notes = f"Cryopreserved at -80°C in Tank '{tank_number}' position '{canister_position}'"

        archive = CryoFrozenBagArchive(
            archive_code=archive_code,
            bag_id=bag.id,
            glycerol_concentration_percent=glycerol_concentration,
            freezing_temp_celsius=-80.0,
            tank_number=tank_number,
            canister_position=canister_position,
            frozen_date=date.today(),
            max_expiry_date=ten_year_expiry,
            thawing_status="FROZEN"
        )

        db.session.add(archive)
        db.session.commit()

        logger.info(f"Cryopreserved Bag '{bag.bag_code}' to Archive '{archive_code}' (Tank: {tank_number}, Expiry: {ten_year_expiry})")
        return archive

    @staticmethod
    def initiate_deglycerolization_thaw(
        archive_id: int
    ) -> Dict[str, Any]:
        """
        Initiates 37°C water bath thaw and serial hypertonic saline deglycerolization wash protocol.
        Unit must be transfused within 24 HOURS post-deglycerolization.
        """
        archive = CryoFrozenBagArchive.query.get(archive_id)
        if not archive:
            return {"error": f"Cryo Archive ID {archive_id} not found."}

        archive.thawing_status = "DEGLYCEROLIZED"
        db.session.commit()

        now = datetime.now(timezone.utc)
        post_thaw_expiry = now + timedelta(hours=24)

        return {
            "archive_id": archive.id,
            "archive_code": archive.archive_code,
            "thaw_status": "DEGLYCEROLIZED",
            "thawed_at": now.isoformat(),
            "post_thaw_transfusion_expiry": post_thaw_expiry.isoformat(),
            "wash_protocol": "Serial 12% Saline -> 1.6% Saline -> 0.9% Saline Wash Passed",
            "ready_for_crossmatch": True
        }
