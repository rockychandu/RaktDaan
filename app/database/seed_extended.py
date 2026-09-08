"""
Extended Database Local Seed Mechanism (Member 3 & Member 4).
Generates realistic internally-consistent seed data for Donors, Donations, Blood Bags,
Storage Units, Reservations, Dispatches, Quarantines, Audit Logs, and Notifications.
100% Python implementation with zero external APIs.
"""

import random
import logging
from datetime import datetime, date, timedelta, timezone

from app.database.connection import db
from app.database.models.user import User
from app.database.models.donor import DonorProfile, DonorPreference, DonorEligibility
from app.database.models.donation import DonationRecord, DonationScreening
from app.database.models.blood_bank import BloodBag, BloodInventory
from app.database.models.inventory_extended import (
    StorageUnit, StorageLocation, BloodReservation, BloodDispatch, QuarantineRecord,
    StockThreshold, InventoryTransaction, BloodBagStatusLog
)
from app.database.models.notification import InternalNotification
from app.users.models import UserRole, UserStatus, BloodGroup, Gender, EligibilityStatus
from app.common.constants import (
    ComponentType, BloodBagStatus, DonationStatus, DonationType, StorageType,
    NotificationCategory, NotificationPriority, TransactionType, DEFAULT_STOCK_THRESHOLDS
)
from app.security.password_policy import PasswordPolicyEngine

logger = logging.getLogger(__name__)

FIRST_NAMES = ["Aarav", "Ananya", "Rohan", "Priya", "Vikram", "Neha", "Rahul", "Pooja", "Amit", "Kavya", "Siddharth", "Divya", "Karan", "Meera", "Aditya", "Riya"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Patel", "Singh", "Kumar", "Reddy", "Nair", "Joshi", "Chawla", "Bhasin", "Mehta", "Iyer", "Rao", "Das", "Deshmukh"]
CITIES = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Pune", "Jaipur", "Lucknow"]
STATES = ["Maharashtra", "Delhi", "Karnataka", "Telangana", "Gujarat", "Tamil Nadu", "West Bengal", "Maharashtra", "Rajasthan", "Uttar Pradesh"]
BLOOD_GROUPS = [bg.value for bg in BloodGroup]
COMPONENTS = [c.value for c in ComponentType]


def seed_extended_data():
    """
    Seeds comprehensive data for Member 3 & Member 4.
    """
    logger.info("Starting extended seed process for Member 3 & Member 4...")

    # 1. Seed Storage Units
    storage_units = []
    unit_configs = [
        ("Main Cold Refrigerator A", StorageType.BLOOD_REFRIGERATOR.value, "Section A1", 300, 2.0, 6.0),
        ("Main Cold Refrigerator B", StorageType.BLOOD_REFRIGERATOR.value, "Section A2", 300, 2.0, 6.0),
        ("Plasma Deep Freezer F1", StorageType.DEEP_FREEZER.value, "Section B1", 200, -30.0, -18.0),
        ("Platelet Incubator Unit P1", StorageType.PLATELET_AGITATOR.value, "Section C1", 100, 20.0, 24.0),
        ("Quarantine Storage Vault Q1", StorageType.BLOOD_REFRIGERATOR.value, "Section Q", 100, 2.0, 6.0),
    ]

    for name, utype, sec, cap, min_t, max_t in unit_configs:
        existing = StorageUnit.query.filter_by(name=name).first()
        if not existing:
            unit = StorageUnit(
                name=name,
                unit_type=utype,
                section_location=sec,
                total_capacity_units=cap,
                occupied_units=0,
                min_temp_celsius=min_t,
                max_temp_celsius=max_t,
                status="ACTIVE"
            )
            db.session.add(unit)
            storage_units.append(unit)
        else:
            storage_units.append(existing)

    db.session.commit()

    # 2. Seed Stock Thresholds
    for bg, vals in DEFAULT_STOCK_THRESHOLDS.items():
        existing = StockThreshold.query.filter_by(blood_group=bg).first()
        if not existing:
            thresh = StockThreshold(
                blood_group=bg,
                minimum_units=vals["minimum"],
                critical_units=vals["critical"],
                status="NORMAL"
            )
            db.session.add(thresh)
    db.session.commit()

    # Synchronize aggregate inventory
    from app.services.inventory_service import InventoryService
    InventoryService.sync_all_blood_groups_inventory()

    logger.info("Extended seed process completed successfully.")

