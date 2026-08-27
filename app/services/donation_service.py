"""
Donation Workflow & State Machine Service Layer (Member 3 & Member 4 Integration).
Manages complete workflow: Registered -> Screening -> Eligible -> Donation -> Blood Bag Creation -> Inventory.
"""

import logging
from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional, Tuple

from app.database.connection import db
from app.database.models.donor import DonorProfile
from app.database.models.donation import DonationRecord, DonationScreening
from app.database.models.blood_bank import BloodBag
from app.users.models import EligibilityStatus
from app.common.constants import DonationStatus, DonationType, BloodBagStatus, ComponentType
from app.common.exceptions import (
    DonationNotFoundException, InvalidDonationWorkflowState, EligibilityEvaluationException
)
from app.services.donor_service import DonorService
from app.services.eligibility_engine import DonorEligibilityEngine
from app.schemas.donation_schemas import DonationCreateSchema, DonationScreeningUpdateSchema

logger = logging.getLogger(__name__)


def generate_unique_donation_code() -> str:
    """
    Generates unique donation tracking code in format DON-YYYY-XXXXXX.
    """
    year = datetime.now(timezone.utc).strftime("%Y")
    count = db.session.query(DonationRecord).count() + 1
    return f"DON-{year}-{count:06d}"


class DonationService:
    """
    Business Logic Layer for Donation Life-cycle and Screening Workflow.
    """

    @staticmethod
    def create_donation_registration(data_dict: Dict[str, Any], staff_user_id: Optional[int] = None) -> DonationRecord:
        """
        Initiates a new donation registration event for an eligible donor.
        """
        schema = DonationCreateSchema(**data_dict)
        donor = DonorService.get_donor_by_id(schema.donor_id)

        # Check donor eligibility status
        eval_result = DonorEligibilityEngine.evaluate_eligibility(donor.id)
        if not eval_result["is_eligible"]:
            raise EligibilityEvaluationException(
                reason="; ".join(eval_result["reasons"]),
                errors={"eligibility": eval_result["reasons"]}
            )

        donation_code = generate_unique_donation_code()

        donation = DonationRecord(
            donation_code=donation_code,
            donor_id=donor.id,
            blood_group=donor.blood_group,
            donation_type=schema.donation_type,
            collection_center=schema.collection_center,
            staff_user_id=staff_user_id,
            screening_status="PENDING",
            donation_status=DonationStatus.REGISTERED.value,
            notes=schema.notes
        )
        db.session.add(donation)
        db.session.commit()

        logger.info(f"Registered Donation Event: Code {donation_code} for Donor ID {donor.id}")
        return donation

    @staticmethod
    def submit_medical_screening(donation_id: int, screening_data: Dict[str, Any], staff_user_id: Optional[int] = None) -> Tuple[DonationRecord, DonationScreening]:
        """
        Submits healthcare staff medical screening & vitals check for a registered donation.
        Moves status from REGISTERED -> SCREENING -> ELIGIBLE (or DEFERRED).
        """
        donation = DonationRecord.query.filter_by(id=donation_id, is_deleted=False).first()
        if not donation:
            raise DonationNotFoundException(donation_id)

        if donation.donation_status not in [DonationStatus.REGISTERED.value, DonationStatus.SCREENING.value]:
            raise InvalidDonationWorkflowState(
                current_state=donation.donation_status,
                target_state=DonationStatus.SCREENING.value,
                reason="Medical screening can only be performed on REGISTERED donations."
            )

        schema = DonationScreeningUpdateSchema(**screening_data)

        # Create or update screening record
        screening = donation.screening
        if not screening:
            screening = DonationScreening(donation_id=donation.id)
            db.session.add(screening)

        screening.weight_kg = schema.weight_kg
        screening.hemoglobin_level = schema.hemoglobin_level
        screening.blood_pressure_sys = schema.blood_pressure_sys
        screening.blood_pressure_dia = schema.blood_pressure_dia
        screening.pulse_rate = schema.pulse_rate
        screening.temp_celsius = schema.temp_celsius
        screening.has_chronic_illness = schema.has_chronic_illness
        screening.is_on_medication = schema.is_on_medication
        screening.is_passed = schema.is_passed
        screening.screening_notes = schema.screening_notes
        screening.evaluated_by_staff_id = staff_user_id

        # Update Workflow States
        if schema.is_passed:
            donation.screening_status = "PASSED"
            donation.donation_status = DonationStatus.ELIGIBLE.value
        else:
            donation.screening_status = "FAILED"
            donation.donation_status = DonationStatus.DEFERRED.value
            donation.cancellation_reason = f"Medical Screening Failed: {schema.screening_notes}"

        db.session.commit()
        logger.info(f"Screening submitted for Donation ID {donation_id}: Passed={schema.is_passed}")
        return donation, screening

    @staticmethod
    def start_donation_procedure(donation_id: int) -> DonationRecord:
        """
        Transitions donation status from ELIGIBLE -> IN_PROGRESS.
        """
        donation = DonationRecord.query.filter_by(id=donation_id, is_deleted=False).first()
        if not donation:
            raise DonationNotFoundException(donation_id)

        if donation.donation_status != DonationStatus.ELIGIBLE.value:
            raise InvalidDonationWorkflowState(
                current_state=donation.donation_status,
                target_state=DonationStatus.IN_PROGRESS.value,
                reason="Donation can only be started when status is ELIGIBLE."
            )

        donation.donation_status = DonationStatus.IN_PROGRESS.value
        db.session.commit()
        logger.info(f"Donation ID {donation_id} is now IN_PROGRESS")
        return donation

    @staticmethod
    def complete_donation_procedure(donation_id: int, collected_volume_ml: int = 450) -> Tuple[DonationRecord, BloodBag]:
        """
        Completes donation procedure (IN_PROGRESS -> COMPLETED).
        Automatically creates a new BloodBag in COLLECTED status, updates donor's last donation date, and links records.
        """
        donation = DonationRecord.query.filter_by(id=donation_id, is_deleted=False).first()
        if not donation:
            raise DonationNotFoundException(donation_id)

        if donation.donation_status not in [DonationStatus.IN_PROGRESS.value, DonationStatus.ELIGIBLE.value]:
            raise InvalidDonationWorkflowState(
                current_state=donation.donation_status,
                target_state=DonationStatus.COMPLETED.value,
                reason="Cannot complete a donation that is not ELIGIBLE or IN_PROGRESS."
            )

        donation.donation_status = DonationStatus.COMPLETED.value
        donation.volume_ml = collected_volume_ml

        # Update Donor's Last Donation Date
        donor = donation.donor_profile
        donor.last_donation_date = date.today()

        # Import Blood Bag Service to generate bag
        from app.services.blood_bag_service import BloodBagService
        blood_bag = BloodBagService.create_blood_bag_from_donation(donation.id, volume_ml=collected_volume_ml)

        db.session.commit()
        logger.info(f"Completed Donation ID {donation_id}. Generated BloodBag Code: {blood_bag.bag_code}")
        return donation, blood_bag

    @staticmethod
    def cancel_donation(donation_id: int, reason: str) -> DonationRecord:
        """
        Cancels a donation procedure.
        """
        donation = DonationRecord.query.filter_by(id=donation_id, is_deleted=False).first()
        if not donation:
            raise DonationNotFoundException(donation_id)

        if donation.donation_status == DonationStatus.COMPLETED.value:
            raise InvalidDonationWorkflowState(
                current_state=donation.donation_status,
                target_state=DonationStatus.CANCELLED.value,
                reason="Completed donations cannot be cancelled."
            )

        donation.donation_status = DonationStatus.CANCELLED.value
        donation.cancellation_reason = reason
        db.session.commit()
        logger.info(f"Cancelled Donation ID {donation_id}. Reason: {reason}")
        return donation

    @staticmethod
    def list_donations_for_donor(donor_id: int) -> List[DonationRecord]:
        """
        Retrieves chronological donation history for a specific donor.
        """
        return DonationRecord.query.filter_by(donor_id=donor_id, is_deleted=False).order_by(DonationRecord.donation_date.desc()).all()

    @staticmethod
    def list_all_donations(
        status: Optional[str] = None,
        blood_group: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Queries and paginates system-wide donation records.
        """
        query = DonationRecord.query.filter_by(is_deleted=False)

        if status:
            query = query.filter(DonationRecord.donation_status == status)
        if blood_group:
            query = query.filter(DonationRecord.blood_group == blood_group)

        query = query.order_by(DonationRecord.donation_date.desc())
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "items": [d.to_dict() for d in items],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
