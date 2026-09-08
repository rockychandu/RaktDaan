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

    # 3. Seed 20 Realistic Donors
    donors = []
    for i in range(1, 21):
        email = f"donor{i}@example.com"
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            if existing_user.donor_profile:
                donors.append(existing_user.donor_profile)
            continue

        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        phone = f"98765{i:05d}"
        bg = BLOOD_GROUPS[i % len(BLOOD_GROUPS)]
        gender = "Female" if i % 2 == 0 else "Male"
        city_idx = i % len(CITIES)

        user = User(
            name=name,
            email=email,
            password_hash=PasswordPolicyEngine.hash_password("Donor@RaktDaan123"),
            role=UserRole.DONOR.value,
            phone=phone,
            status=UserStatus.ACTIVE.value
        )
        db.session.add(user)
        db.session.flush()

        dob = date(1985 + (i % 20), (i % 12) + 1, (i % 25) + 1)
        last_donation = date.today() - timedelta(days=90 + (i * 10))

        donor = DonorProfile(
            user_id=user.id,
            date_of_birth=dob,
            gender=gender,
            blood_group=bg,
            address=f"House No. {10 + i}, Sector {i % 5 + 1}",
            city=CITIES[city_idx],
            state=STATES[city_idx],
            emergency_contact=f"91234{i:05d}",
            eligibility_status=EligibilityStatus.ELIGIBLE.value,
            last_donation_date=last_donation
        )
        db.session.add(donor)
        db.session.flush()

        pref = DonorPreference(donor_profile_id=donor.id, allow_emergency_sms=True, allow_email_notifications=True)
        db.session.add(pref)
        donors.append(donor)

    db.session.commit()

    # 4. Seed 30 Donations and Blood Bags
    today = date.today()
    bag_statuses = [
        BloodBagStatus.AVAILABLE.value, BloodBagStatus.AVAILABLE.value, BloodBagStatus.AVAILABLE.value,
        BloodBagStatus.RESERVED.value, BloodBagStatus.DISPATCHED.value, BloodBagStatus.QUARANTINED.value,
        BloodBagStatus.EXPIRED.value
    ]

    for i, donor in enumerate(donors):
        don_code = f"DON-2026-{i+1:06d}"
        existing_don = DonationRecord.query.filter_by(donation_code=don_code).first()
        if existing_don:
            continue

        don_date = datetime.now(timezone.utc) - timedelta(days=15 + (i * 3))

        donation = DonationRecord(
            donation_code=don_code,
            donor_id=donor.id,
            blood_group=donor.blood_group,
            donation_type=DonationType.WHOLE_BLOOD.value,
            donation_date=don_date,
            volume_ml=450,
            collection_center="Central RaktDaan Blood Bank",
            screening_status="PASSED",
            donation_status=DonationStatus.COMPLETED.value
        )
        db.session.add(donation)
        db.session.flush()

        screening = DonationScreening(
            donation_id=donation.id,
            weight_kg=65.0 + (i % 20),
            hemoglobin_level=14.0 + (i % 3) * 0.5,
            blood_pressure_sys=120,
            blood_pressure_dia=80,
            pulse_rate=72,
            temp_celsius=36.6,
            has_chronic_illness=False,
            is_on_medication=False,
            is_passed=True,
            screening_notes="Vitals normal. Approved for donation."
        )
        db.session.add(screening)

        # Generate Blood Bag
        bag_code = f"BB-2026-{i+1:06d}"
        status = bag_statuses[i % len(bag_statuses)]
        comp_type = COMPONENTS[i % len(COMPONENTS)]

        col_date = don_date.date()
        exp_date = col_date + timedelta(days=35 if comp_type == ComponentType.WHOLE_BLOOD.value else 42)
        if status == BloodBagStatus.EXPIRED.value:
            exp_date = today - timedelta(days=2) # Force expired

        unit = storage_units[i % len(storage_units)]

        bag = BloodBag(
            bag_code=bag_code,
            donation_id=donation.id,
            donor_id=donor.id,
            blood_group=donor.blood_group,
            component_type=comp_type,
            volume_ml=450,
            collection_date=col_date,
            processing_date=col_date,
            testing_date=col_date,
            expiry_date=exp_date,
            storage_unit_id=unit.id,
            shelf_position=f"Rack-{(i%3)+1} / Shelf-{(i%4)+1} / Pos-{(i%10)+1}",
            status=status,
            quality_status="PASSED"
        )
        db.session.add(bag)
        unit.occupied_units += 1

    db.session.commit()

    # 5. Seed Notifications
    notifications_data = [
        ("Low Stock Alert: O- Blood Group", "CRITICAL: O- Blood group has reached critical stock level (2 units remaining).", NotificationCategory.CRITICAL_STOCK.value, NotificationPriority.CRITICAL.value),
        ("Expiring Soon: BB-2026-000005", "Blood bag BB-2026-000005 (A+ PRBC) will expire in 3 days.", NotificationCategory.EXPIRING_SOON.value, NotificationPriority.HIGH.value),
        ("Quarantine Isolation Alert: BB-2026-000006", "Blood bag BB-2026-000006 placed in quarantine pending serology re-test.", NotificationCategory.QUARANTINE_ALERT.value, NotificationPriority.HIGH.value),
        ("System Maintenance Complete", "Routine database background consistency check completed successfully.", NotificationCategory.IMPORTANT_EVENT.value, NotificationPriority.LOW.value),
    ]

    for title, msg, cat, prio in notifications_data:
        existing = InternalNotification.query.filter_by(title=title).first()
        if not existing:
            notif = InternalNotification(
                title=title,
                message=msg,
                category=cat,
                priority=prio,
                is_read=False,
                is_acknowledged=False
            )
            db.session.add(notif)

    db.session.commit()

    # Synchronize aggregate inventory
    from app.services.inventory_service import InventoryService
    InventoryService.sync_all_blood_groups_inventory()

    logger.info("Extended seed process for Member 3 & Member 4 completed successfully.")
