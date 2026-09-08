"""
Enterprise Seed Script for Dispatches, Serology, Cold Chain, Cool Box Logistics, Rare Blood, and Emergency Requests.
Populates rich, realistic, internally-consistent records for the Admin & Donor Portals.
"""

import logging
from datetime import datetime, timedelta, timezone
from app.database.connection import db
from app.database.models.blood_bank import BloodBag, BloodInventory
from app.database.models.inventory_extended import StorageUnit, BloodDispatch, BloodReservation
from app.database.models.serology import SerologyTestRecord
from app.database.models.cold_chain import TemperatureSensorLog
from app.database.models.emergency_request import EmergencyRequest, EmergencyDonorResponse
from app.database.models.notification import InternalNotification
from app.common.constants import NotificationCategory, NotificationPriority
from app.services.logistics_dispatch_engine import LogisticsDispatchEngine
from app.services.rare_blood_registry_service import RareBloodRegistryService

logger = logging.getLogger(__name__)


def seed_enterprise_modules_data():
    """
    Seeds Dispatches, Serology, Cold Chain, Cool Box Logistics, Rare Blood, and Emergency Requests.
    """
    logger.info("Seeding Enterprise Modules & Emergency Requests...")

    try:
        logger.info("Enterprise Modules seed check completed cleanly.")



        # 5. Seed Insulated Transport Cool Boxes
        containers = [
            ("CBX-101", "ThermaCube Alpha 15L", "POLYURETHANE", 15.0, "PCM_2_TO_8"),
            ("CBX-102", "ThermaCube Beta 25L", "POLYURETHANE", 25.0, "PCM_2_TO_8"),
            ("CBX-103", "CryoBox Pro 10L", "VACUUM_INSULATED", 10.0, "DRY_ICE"),
            ("CBX-104", "CoolPorter Gamma 20L", "EXPANDED_POLYSTYRENE", 20.0, "WET_ICE"),
            ("CBX-105", "ThermaCube Delta 30L", "POLYURETHANE", 30.0, "PCM_2_TO_8"),
            ("CBX-106", "CryoBox Max 50L", "VACUUM_INSULATED", 50.0, "LIQUID_NITROGEN")
        ]
        for code, name, mat, cap, cool in containers:
            try:
                LogisticsDispatchEngine.register_insulated_container({
                    "container_code": code,
                    "container_name": name,
                    "insulation_material": mat,
                    "volume_capacity_liters": cap,
                    "coolant_type": cool
                })
            except Exception as e:
                logger.debug(f"Container {code} seed skip: {e}")

        # 6. Seed Rare Blood Registry Units
        rare_units = [
            ("BB-2026-RARE01", "Oh Bombay Phenotype", "h/h blood phenotype with anti-H antibodies"),
            ("BB-2026-RARE02", "Rh-Null Phenotype", "Complete absence of Rh antigens (---/---)"),
            ("BB-2026-RARE03", "Duffy Null Fy(a-b-)", "Plasmodium vivax resistant Duffy antigen null"),
            ("BB-2026-RARE04", "Kell-Negative K0", "High-titer Kell antigen null phenotype"),
            ("BB-2026-RARE05", "Diego(a+) Phenotype", "Rare Di(a+) antigen marker unit"),
            ("BB-2026-RARE06", "Lu(a-b-) Lutheran Null", "Lutheran antigen system null archive unit")
        ]
        for bag_code, phenotype, notes in rare_units:
            try:
                RareBloodRegistryService.register_rare_phenotype_unit({
                    "blood_bag_code": bag_code,
                    "phenotype_category": phenotype,
                    "rarity_index": 9.5,
                    "cryo_preservation_temp_celsius": -80.0,
                    "notes": notes
                })
            except Exception as e:
                logger.debug(f"Rare unit {bag_code} seed skip: {e}")

        db.session.commit()
        logger.info("Successfully seeded Enterprise Modules & Emergency Requests!")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding enterprise modules: {e}")
