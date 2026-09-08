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
        # 1. Seed Emergency Requests
        emergency_data = [
            ("ER-2026-900101", "Dr. Sunita Rao", "9876543210", "sunita.rao@example.com", "Anil Verma", 42, "O-", 3, "Apex City Hospital", "Bandra West, Mumbai", "Mumbai", "STAT", "2026-08-28 10:00 AM", "Acute surgical trauma hemorrhage", "PENDING"),
            ("ER-2026-900102", "Priya Sharma", "9820123456", "priya.sharma@example.com", "Kavita Sharma", 38, "A+", 2, "Fortis Super Specialty", "Vasant Kunj, Delhi", "Delhi", "HIGH", "2026-08-28 02:00 PM", "Emergency blood loss during surgery", "APPROVED"),
            ("ER-2026-900103", "Rohan Mehta", "9930987654", "rohan.mehta@example.com", "Dev Mehta", 65, "B-", 2, "Apollo Heart Institute", "Jubilee Hills, Hyderabad", "Hyderabad", "HIGH", "2026-08-28 06:00 PM", "Platelet replacement for cardiac surgery", "ACTIVE"),
            ("ER-2026-900104", "Dr. Vikram Das", "9711223344", "vikram.das@example.com", "Siddharth Das", 29, "AB-", 1, "Max Healthcare", "Indiranagar, Bangalore", "Bangalore", "STAT", "2026-08-28 11:30 AM", "Critical ICU transfusion support", "PENDING"),
        ]

        for code, rname, rphone, remail, pname, page, bg, units, hosp, addr, city, urg, req_dt, reason, st in emergency_data:
            existing = EmergencyRequest.query.filter_by(request_code=code).first()
            if not existing:
                req = EmergencyRequest(
                    request_code=code,
                    requester_id=1,
                    requester_name=rname,
                    requester_phone=rphone,
                    requester_email=remail,
                    patient_name=pname,
                    patient_age=page,
                    blood_group=bg,
                    units_required=units,
                    hospital_name=hosp,
                    hospital_address=addr,
                    hospital_city=city,
                    urgency_level=urg,
                    required_datetime=req_dt,
                    additional_reason=reason,
                    status=st
                )
                db.session.add(req)
                db.session.flush()

                # Add sample donor response for active request
                if st == "ACTIVE":
                    resp = EmergencyDonorResponse(
                        request_id=req.id,
                        donor_id=2,
                        donor_name="Rajesh Kumar",
                        donor_phone="9876543210",
                        donor_blood_group=bg,
                        response_status="RESPONDED",
                        response_notes="Pledged voluntary donation from Donor Portal."
                    )
                    db.session.add(resp)

                # Add internal alert notification for Admin
                notif = InternalNotification(
                    title=f"🚨 Emergency Request {code} ({bg})",
                    message=f"CRITICAL: {units} Unit(s) of {bg} required at {hosp} for patient {pname}. Urgency: {urg}.",
                    category=NotificationCategory.SYSTEM_ALERT.value if hasattr(NotificationCategory, 'SYSTEM_ALERT') else "SYSTEM_ALERT",
                    priority=NotificationPriority.HIGH.value
                )
                db.session.add(notif)

        # 2. Seed Serology Test Records
        bags = BloodBag.query.all()
        if bags:
            for idx, bag in enumerate(bags[:8]):
                code = f"SER-2026-{bag.id:04d}"
                existing = SerologyTestRecord.query.filter_by(test_code=code).first()
                if not existing:
                    rec = SerologyTestRecord(
                        test_code=code,
                        bag_id=bag.id,
                        hiv_result="NON_REACTIVE",
                        hbsag_result="NON_REACTIVE",
                        hcv_result="NON_REACTIVE",
                        vdrl_result="NON_REACTIVE",
                        malaria_result="NON_REACTIVE",
                        nat_test_result="NEGATIVE",
                        overall_quality_status="PASSED",
                        tested_by_technician_id=1,
                        lab_notes="Automated NAT & ELISA serology screening verified."
                    )
                    db.session.add(rec)

        # 3. Seed Cold Chain Sensor Logs
        units = StorageUnit.query.all()
        if units:
            for unit in units:
                target = (unit.min_temp_celsius + unit.max_temp_celsius) / 2.0
                for i in range(3):
                    reading = round(target + (i * 0.2), 1)
                    log = TemperatureSensorLog(
                        storage_unit_id=unit.id,
                        reading_temp_celsius=reading,
                        is_excursion=False,
                        recorded_at=datetime.now(timezone.utc) - timedelta(hours=i*2),
                        notes=f"Automated IoT sensor telemetry check for {unit.name}."
                    )
                    db.session.add(log)

        # 4. Seed Dispatches
        if bags:
            hospitals = [
                ("Apex City Hospital", "Ramesh Verma", "O+"),
                ("Fortis Emergency Care", "Sunita Nair", "A+"),
                ("Max Super Specialty", "Vikram Das", "B+"),
                ("Apollo Transfusion Center", "Meera Iyer", "AB+")
            ]
            for idx, (hosp, patient, bg) in enumerate(hospitals):
                code = f"DSP-2026-{idx+1:04d}"
                existing = BloodDispatch.query.filter_by(dispatch_code=code).first()
                if not existing:
                    dsp = BloodDispatch(
                        dispatch_code=code,
                        reference_request_id=f"REQ-{idx+101}",
                        hospital_name=hosp,
                        recipient_patient_name=patient,
                        blood_group=bg,
                        component_type="WHOLE_BLOOD",
                        quantity_units=2,
                        dispatched_by_user_id=1,
                        status="COMPLETED" if idx == 0 else "IN_TRANSIT",
                        transport_box_temp_celsius=4.0,
                        notes=f"Emergency dispatch order of {bg} units to {hosp} for patient {patient}."
                    )
                    db.session.add(dsp)

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
