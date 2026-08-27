"""
Configurable Donor Eligibility Evaluation Engine (Member 3).
Evaluates medical criteria, donation intervals, deferral periods, and logs evaluation history.
Does NOT present output as medical diagnosis.
"""

import logging
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, Tuple, Optional

from app.database.connection import db
from app.database.models.donor import DonorProfile, DonorEligibility, DonorMedicalHistory
from app.users.models import EligibilityStatus
from app.common.constants import (
    DONATION_INTERVAL_MALE_DAYS, DONATION_INTERVAL_FEMALE_DAYS, DeferralType
)
from app.common.exceptions import DonorNotFoundException

logger = logging.getLogger(__name__)


class EligibilityRuleConfig:
    """
    Configurable Application Eligibility Threshold Rules.
    """
    MIN_AGE_YEARS: int = 18
    MAX_AGE_YEARS: int = 65
    MIN_WEIGHT_KG: float = 50.0
    MIN_HEMOGLOBIN_GDL: float = 12.5
    MIN_BP_SYS: int = 100
    MAX_BP_SYS: int = 140
    MIN_BP_DIA: int = 60
    MAX_BP_DIA: int = 90
    MIN_PULSE_BPM: int = 60
    MAX_PULSE_BPM: int = 100
    INTERVAL_MALE_DAYS: int = DONATION_INTERVAL_MALE_DAYS
    INTERVAL_FEMALE_DAYS: int = DONATION_INTERVAL_FEMALE_DAYS


class DonorEligibilityEngine:
    """
    Rules Engine for automated donor eligibility evaluation.
    """

    @staticmethod
    def evaluate_eligibility(
        donor_id: int,
        weight_kg: Optional[float] = None,
        hemoglobin_level: Optional[float] = None,
        bp_sys: Optional[int] = None,
        bp_dia: Optional[int] = None,
        pulse_rate: Optional[int] = None,
        has_chronic_illness: bool = False,
        is_on_medication: bool = False,
        evaluator_staff_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Evaluates donor eligibility against configurable criteria and records history.
        """
        donor = DonorProfile.query.filter_by(id=donor_id, is_deleted=False).first()
        if not donor:
            raise DonorNotFoundException(donor_id)

        today = date.today()
        dob = donor.date_of_birth
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        reasons = []
        is_eligible = True
        deferral_type = DeferralType.NONE.value
        eligible_after_date = None

        # Rule 1: Age Check
        if age < EligibilityRuleConfig.MIN_AGE_YEARS or age > EligibilityRuleConfig.MAX_AGE_YEARS:
            is_eligible = False
            reasons.append(f"Age {age} is outside the allowed range of {EligibilityRuleConfig.MIN_AGE_YEARS}-{EligibilityRuleConfig.MAX_AGE_YEARS} years.")
            if age < EligibilityRuleConfig.MIN_AGE_YEARS:
                deferral_type = DeferralType.TEMPORARY.value
                # Calculate date when donor turns 18
                eligible_after_date = date(dob.year + 18, dob.month, dob.day)
            else:
                deferral_type = DeferralType.PERMANENT.value

        # Rule 2: Donation Interval Check
        if donor.last_donation_date:
            required_days = (
                EligibilityRuleConfig.INTERVAL_FEMALE_DAYS
                if donor.gender == "Female"
                else EligibilityRuleConfig.INTERVAL_MALE_DAYS
            )
            next_eligible = donor.last_donation_date + timedelta(days=required_days)
            if today < next_eligible:
                is_eligible = False
                days_remaining = (next_eligible - today).days
                reasons.append(f"Recent donation on {donor.last_donation_date}. Must wait {days_remaining} more days until {next_eligible}.")
                if deferral_type != DeferralType.PERMANENT.value:
                    deferral_type = DeferralType.TEMPORARY.value
                    eligible_after_date = next_eligible

        # Rule 3: Weight Check
        if weight_kg is not None and weight_kg < EligibilityRuleConfig.MIN_WEIGHT_KG:
            is_eligible = False
            reasons.append(f"Weight {weight_kg} kg is below minimum requirement of {EligibilityRuleConfig.MIN_WEIGHT_KG} kg.")
            if deferral_type != DeferralType.PERMANENT.value:
                deferral_type = DeferralType.TEMPORARY.value

        # Rule 4: Hemoglobin Check
        if hemoglobin_level is not None and hemoglobin_level < EligibilityRuleConfig.MIN_HEMOGLOBIN_GDL:
            is_eligible = False
            reasons.append(f"Hemoglobin level {hemoglobin_level} g/dL is below minimum requirement of {EligibilityRuleConfig.MIN_HEMOGLOBIN_GDL} g/dL.")
            if deferral_type != DeferralType.PERMANENT.value:
                deferral_type = DeferralType.TEMPORARY.value
                if not eligible_after_date:
                    eligible_after_date = today + timedelta(days=30)

        # Rule 5: Blood Pressure Check
        if bp_sys is not None and bp_dia is not None:
            if bp_sys < EligibilityRuleConfig.MIN_BP_SYS or bp_sys > EligibilityRuleConfig.MAX_BP_SYS:
                is_eligible = False
                reasons.append(f"Systolic BP {bp_sys} mmHg outside acceptable range ({EligibilityRuleConfig.MIN_BP_SYS}-{EligibilityRuleConfig.MAX_BP_SYS} mmHg).")
                if deferral_type != DeferralType.PERMANENT.value:
                    deferral_type = DeferralType.TEMPORARY.value
            if bp_dia < EligibilityRuleConfig.MIN_BP_DIA or bp_dia > EligibilityRuleConfig.MAX_BP_DIA:
                is_eligible = False
                reasons.append(f"Diastolic BP {bp_dia} mmHg outside acceptable range ({EligibilityRuleConfig.MIN_BP_DIA}-{EligibilityRuleConfig.MAX_BP_DIA} mmHg).")
                if deferral_type != DeferralType.PERMANENT.value:
                    deferral_type = DeferralType.TEMPORARY.value

        # Rule 6: Chronic Illness & Medication Check
        if has_chronic_illness:
            is_eligible = False
            reasons.append("Donor reported active chronic medical condition.")
            deferral_type = DeferralType.PERMANENT.value
        if is_on_medication:
            is_eligible = False
            reasons.append("Donor is currently taking interfering prescription medications.")
            if deferral_type != DeferralType.PERMANENT.value:
                deferral_type = DeferralType.TEMPORARY.value

        # Determine Final Status String
        if is_eligible:
            final_status = EligibilityStatus.ELIGIBLE.value
            summary_reason = "All medical screening & donation interval criteria met."
        elif deferral_type == DeferralType.PERMANENT.value:
            final_status = EligibilityStatus.PERMANENTLY_INELIGIBLE.value
            summary_reason = "; ".join(reasons)
        else:
            final_status = EligibilityStatus.TEMPORARILY_INELIGIBLE.value
            summary_reason = "; ".join(reasons)

        # Update DonorProfile Status
        donor.eligibility_status = final_status

        # Create Evaluation History Record
        eligibility_record = DonorEligibility(
            donor_profile_id=donor.id,
            status=final_status,
            reason=summary_reason,
            eligible_after_date=eligible_after_date
        )
        db.session.add(eligibility_record)

        # Save Medical Vitals if provided
        if weight_kg is not None:
            medical_hist = DonorMedicalHistory(
                donor_profile_id=donor.id,
                weight_kg=weight_kg,
                hemoglobin_level=hemoglobin_level,
                blood_pressure_sys=bp_sys,
                blood_pressure_dia=bp_dia,
                pulse_rate=pulse_rate,
                has_chronic_illness=has_chronic_illness,
                is_on_medication=is_on_medication,
                medical_notes=summary_reason
            )
            db.session.add(medical_hist)

        db.session.commit()

        logger.info(f"Evaluated Eligibility for Donor ID {donor_id}: Status={final_status}")

        return {
            "donor_id": donor.id,
            "status": final_status,
            "is_eligible": is_eligible,
            "deferral_type": deferral_type,
            "reasons": reasons if not is_eligible else [summary_reason],
            "eligible_after_date": eligible_after_date.isoformat() if eligible_after_date else None,
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    def calculate_next_eligible_date(donor_id: int) -> Optional[date]:
        """
        Calculates the next eligible donation date based on last donation and gender.
        """
        donor = DonorProfile.query.filter_by(id=donor_id).first()
        if not donor or not donor.last_donation_date:
            return date.today()

        days = (
            EligibilityRuleConfig.INTERVAL_FEMALE_DAYS
            if donor.gender == "Female"
            else EligibilityRuleConfig.INTERVAL_MALE_DAYS
        )
        return donor.last_donation_date + timedelta(days=days)
