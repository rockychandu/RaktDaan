"""
Donor Deferral Management & Reinstatement Engine (Member 3).
Handles temporary and permanent donor deferrals, tracks deferral periods,
evaluates reinstatement dates, and generates deferral history logs.
"""

import logging
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.donor import DonorProfile, DonorEligibility
from app.common.donor_medical_rules import DonorMedicalRules
from app.common.exceptions import DonorNotFoundException
from app.users.models import EligibilityStatus

logger = logging.getLogger(__name__)


class DonorDeferralEngine:
    """
    Business Logic Layer for Donor Deferrals & Automatic Reinstatement Evaluation.
    """

    @staticmethod
    def apply_temporary_deferral(
        donor_id: int,
        reason: str,
        deferral_days: int,
        deferral_category: str = "MEDICAL",
        notes: str = None
    ) -> DonorEligibility:
        """
        Applies a temporary deferral to a donor for specified number of days.
        """
        donor = DonorProfile.query.filter_by(id=donor_id, is_deleted=False).first()
        if not donor:
            raise DonorNotFoundException(donor_id)

        today = date.today()
        eligible_after = today + timedelta(days=deferral_days)

        eligibility = DonorEligibility(
            donor_profile_id=donor.id,
            status=EligibilityStatus.TEMPORARILY_INELIGIBLE.value,
            reason=reason,
            eligible_after_date=eligible_after
        )
        db.session.add(eligibility)

        donor.status = EligibilityStatus.TEMPORARILY_INELIGIBLE.value
        db.session.commit()

        logger.info(f"Applied {deferral_days}-day temporary deferral for Donor ID {donor.id}. Deferral until: {eligible_after}")
        return eligibility

    @staticmethod
    def apply_permanent_deferral(
        donor_id: int,
        reason: str,
        condition_code: str = "PERM_CONDITION",
        notes: str = None
    ) -> DonorEligibility:
        """
        Applies a permanent deferral to a donor.
        """
        donor = DonorProfile.query.filter_by(id=donor_id, is_deleted=False).first()
        if not donor:
            raise DonorNotFoundException(donor_id)

        eligibility = DonorEligibility(
            donor_profile_id=donor.id,
            status=EligibilityStatus.PERMANENTLY_INELIGIBLE.value,
            reason=f"PERMANENT DEFERRAL: {reason} (Code: {condition_code})",
            eligible_after_date=None
        )
        db.session.add(eligibility)

        donor.status = EligibilityStatus.PERMANENTLY_INELIGIBLE.value
        db.session.commit()

        logger.warning(f"Applied PERMANENT DEFERRAL for Donor ID {donor.id}. Reason: {reason}")
        return eligibility

    @staticmethod
    def evaluate_reinstatement(donor_id: int) -> Dict[str, Any]:
        """
        Evaluates whether a temporarily deferred donor's deferral period has expired
        and reinstates their status to ELIGIBLE if cleared.
        """
        donor = DonorProfile.query.filter_by(id=donor_id, is_deleted=False).first()
        if not donor:
            raise DonorNotFoundException(donor_id)

        if donor.status == EligibilityStatus.PERMANENTLY_INELIGIBLE.value:
            return {
                "donor_id": donor.id,
                "is_reinstated": False,
                "status": EligibilityStatus.PERMANENTLY_INELIGIBLE.value,
                "message": "Donor has permanent deferral. Cannot be reinstated."
            }

        latest_eligibility = DonorEligibility.query.filter_by(donor_profile_id=donor.id).order_by(DonorEligibility.created_at.desc()).first()

        if not latest_eligibility or not latest_eligibility.eligible_after_date:
            return {
                "donor_id": donor.id,
                "is_reinstated": True,
                "status": EligibilityStatus.ELIGIBLE.value,
                "message": "No active deferral period found."
            }

        today = date.today()
        if today >= latest_eligibility.eligible_after_date:
            # Reinstatement!
            donor.status = EligibilityStatus.ELIGIBLE.value

            reinstated_log = DonorEligibility(
                donor_profile_id=donor.id,
                status=EligibilityStatus.ELIGIBLE.value,
                reason="Automatic reinstatement upon expiration of temporary deferral period.",
                eligible_after_date=None
            )
            db.session.add(reinstated_log)
            db.session.commit()

            logger.info(f"Reinstated Donor ID {donor.id} to ELIGIBLE status.")
            return {
                "donor_id": donor.id,
                "is_reinstated": True,
                "status": EligibilityStatus.ELIGIBLE.value,
                "message": f"Temporary deferral expired on {latest_eligibility.eligible_after_date}. Donor successfully reinstated."
            }
        else:
            days_left = (latest_eligibility.eligible_after_date - today).days
            return {
                "donor_id": donor.id,
                "is_reinstated": False,
                "status": EligibilityStatus.TEMPORARILY_INELIGIBLE.value,
                "deferral_until": latest_eligibility.eligible_after_date.isoformat(),
                "days_remaining": days_left,
                "message": f"Donor remains temporarily deferred for {days_left} more days."
            }
