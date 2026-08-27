"""
Donor Health Checkup Pre-Screening & Appointment Submission Service.
Evaluates donor health checkup vitals against medical blood bank standards using
MasterClinicalScreeningEvaluator and records complete DonorHistoryTimeline entries.
"""

import logging
from datetime import datetime, timezone, date, timedelta
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.donor import DonorProfile
from app.database.models.donation import DonationRecord, DonationScreening
from app.database.models.history_audit import DonorHistoryTimeline
from app.database.models.notification import InternalNotification
from app.clinical.screening_evaluator import MasterClinicalScreeningEvaluator
from app.common.constants import (
    DonationStatus, DonationType, NotificationCategory, NotificationPriority
)

logger = logging.getLogger(__name__)


class DonorPrescreeningService:
    """
    Business Logic Layer for Donor Self-Checkup, Health Evaluation, and History Timeline Logging.
    """

    @staticmethod
    def evaluate_and_submit_prescreening(
        donor_profile_id: int,
        weight_kg: float,
        hemoglobin_level: float,
        blood_pressure_sys: int,
        blood_pressure_dia: int,
        pulse_rate: int,
        temp_celsius: float,
        has_chronic_illness: bool,
        is_on_medication: bool,
        has_recent_infection: bool = False,
        has_recent_hospitalization: bool = False,
        has_recent_surgery: bool = False,
        surgery_type: str = "NONE",
        medication_category: str = "GENERAL",
        has_recent_vaccination: bool = False,
        vaccine_type: str = "INACTIVATED",
        is_currently_pregnant: bool = False,
        is_breastfeeding: bool = False,
        recent_delivery_within_12_months: bool = False,
        collection_center: str = "Central RaktDaan Blood Bank"
    ) -> Dict[str, Any]:
        """
        Evaluates donor vitals and medical history questions using MasterClinicalScreeningEvaluator.
        Saves result to DonationRecord and DonorHistoryTimeline (for BOTH pass and fail).
        """
        donor = DonorProfile.query.get(donor_profile_id)
        if not donor:
            raise ValueError(f"Donor Profile ID {donor_profile_id} not found.")

        # Prepare evaluation payload
        eval_payload = {
            "donor_id": donor.id,
            "gender": donor.gender,
            "date_of_birth": donor.date_of_birth,
            "last_donation_date": donor.last_donation_date,
            "weight_kg": weight_kg,
            "hemoglobin_level": hemoglobin_level,
            "blood_pressure_sys": blood_pressure_sys,
            "blood_pressure_dia": blood_pressure_dia,
            "pulse_rate": pulse_rate,
            "temp_celsius": temp_celsius,
            "has_chronic_illness": has_chronic_illness,
            "is_on_medication": is_on_medication,
            "has_recent_infection": has_recent_infection,
            "has_recent_hospitalization": has_recent_hospitalization,
            "has_recent_surgery": has_recent_surgery,
            "surgery_type": surgery_type,
            "medication_category": medication_category,
            "has_recent_vaccination": has_recent_vaccination,
            "vaccine_type": vaccine_type,
            "is_currently_pregnant": is_currently_pregnant,
            "is_breastfeeding": is_breastfeeding,
            "recent_delivery_within_12_months": recent_delivery_within_12_months
        }

        # 1. Run Master Clinical Evaluation
        evaluator = MasterClinicalScreeningEvaluator()
        eval_result = evaluator.evaluate_donor_checkup(eval_payload)

        is_passed = eval_result["is_passed"]
        reasons = eval_result["reasons"]
        max_deferral_days = eval_result["max_deferral_days"]
        next_eligible_date_str = eval_result["next_eligible_date"]
        next_eligible_dt = date.fromisoformat(next_eligible_date_str) if next_eligible_date_str else None

        don_code = f"DON-{datetime.now().strftime('%Y%m%d%H%M%S')}-{donor.id}"

        # 2. Save Donation Record & Screening Entry
        donation = DonationRecord(
            donation_code=don_code,
            donor_id=donor.id,
            blood_group=donor.blood_group,
            donation_type=DonationType.WHOLE_BLOOD.value,
            donation_date=datetime.now(timezone.utc),
            volume_ml=450,
            collection_center=collection_center,
            screening_status="PASSED" if is_passed else "FAILED",
            donation_status=DonationStatus.REGISTERED.value if is_passed else DonationStatus.CANCELLED.value,
            cancellation_reason="; ".join(reasons) if not is_passed else None,
            notes="Passed health checkup" if is_passed else f"Failed health checkup: {'; '.join(reasons)}"
        )
        db.session.add(donation)
        db.session.flush()

        screening = DonationScreening(
            donation_id=donation.id,
            weight_kg=weight_kg,
            hemoglobin_level=hemoglobin_level,
            blood_pressure_sys=blood_pressure_sys,
            blood_pressure_dia=blood_pressure_dia,
            pulse_rate=pulse_rate,
            temp_celsius=temp_celsius,
            has_chronic_illness=has_chronic_illness,
            is_on_medication=is_on_medication,
            is_passed=is_passed,
            screening_notes="PASSED: Qualified for donation" if is_passed else f"FAILED: {'; '.join(reasons)}"
        )
        db.session.add(screening)

        # Update Donor Profile Eligibility Status
        if not is_passed:
            donor.eligibility_status = "TEMPORARILY_DEFERRED"

        # 3. Store Event in DonorHistoryTimeline (ALWAYS saved to Donor History)
        history = DonorHistoryTimeline(
            donor_id=donor.id,
            event_type="HEALTH_CHECKUP",
            event_date=datetime.now(timezone.utc),
            health_checkup_result="PASSED" if is_passed else "FAILED",
            eligibility_status="ELIGIBLE" if is_passed else "TEMPORARILY_DEFERRED",
            reasons_summary="Health checkup passed successfully" if is_passed else "; ".join(reasons),
            next_eligible_date=next_eligible_dt,
            donation_id=donation.id,
            donation_status=donation.donation_status,
            remarks=eval_result["summary_message"]
        )
        db.session.add(history)

        # 4. If Passed, Alert Admin
        if is_passed:
            donor_name = donor.user.name if donor.user else "Donor"
            notif = InternalNotification(
                title=f"New Health Checkup Passed: {donor_name}",
                message=f"Donor {donor_name} ({donor.blood_group}, {donor.city}) passed pre-donation health checkup (Weight: {weight_kg}kg, Hb: {hemoglobin_level}g/dL, BP: {blood_pressure_sys}/{blood_pressure_dia}). Request forwarded to Admin.",
                category=NotificationCategory.IMPORTANT_EVENT.value,
                priority=NotificationPriority.MEDIUM.value
            )
            db.session.add(notif)

        db.session.commit()

        if is_passed:
            logger.info(f"Donor {donor.id} PASSED health checkup. Forwarded to Admin.")
            return {
                "is_passed": True,
                "screening_status": "PASSED",
                "eligibility_status": "ELIGIBLE",
                "message": "Health checkup passed. You can proceed to the donation process.",
                "donation_code": don_code,
                "donation": donation.to_dict(),
                "screening": screening.to_dict(),
                "history_timeline_id": history.id
            }
        else:
            logger.info(f"Donor {donor.id} FAILED health checkup: {reasons}")
            return {
                "is_passed": False,
                "screening_status": "FAILED",
                "eligibility_status": "TEMPORARILY_DEFERRED",
                "message": "Sorry, you cannot donate blood at this time.",
                "reasons": reasons,
                "screening_date": eval_result["screening_date"],
                "next_eligible_date": eval_result["next_eligible_date"],
                "donation_code": don_code,
                "history_timeline_id": history.id
            }

    @staticmethod
    def get_pending_admin_donations() -> List[Dict[str, Any]]:
        """
        Retrieves all passed pre-screened donor registrations for Admin review.
        """
        records = DonationRecord.query.filter_by(
            screening_status="PASSED",
            donation_status=DonationStatus.REGISTERED.value
        ).order_by(DonationRecord.created_at.desc()).all()

        res = []
        for r in records:
            d_dict = r.to_dict()
            if r.donor_profile:
                d_dict["phone"] = r.donor_profile.user.phone if r.donor_profile.user else None
                d_dict["email"] = r.donor_profile.user.email if r.donor_profile.user else None
                d_dict["city"] = r.donor_profile.city
            if r.screening:
                d_dict["vitals"] = r.screening.to_dict()
            res.append(d_dict)
        return res
