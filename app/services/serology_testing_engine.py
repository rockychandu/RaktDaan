"""
Serology & Nucleic Acid Laboratory Testing Pipeline Service Layer (Member 3 & Member 4).
Processes laboratory serology marker testing (HIV, HBsAg, HCV, VDRL, Malaria, NAT).
Automatically quarantines any reactive blood bag and updates quality status.
"""

import logging
from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.blood_bank import BloodBag
from app.database.models.serology import SerologyTestRecord
from app.common.constants import BloodBagStatus, NotificationCategory, NotificationPriority
from app.common.exceptions import BloodBagNotFoundException
from app.services.blood_bag_service import BloodBagService
from app.services.notification_service import NotificationService
from app.services.quarantine_service import QuarantineService

logger = logging.getLogger(__name__)


def generate_unique_serology_code() -> str:
    """
    Generates unique serology lab test code in format LAB-YYYY-XXXXXX.
    """
    year = datetime.now(timezone.utc).strftime("%Y")
    count = db.session.query(SerologyTestRecord).count() + 1
    return f"LAB-{year}-{count:06d}"


class SerologyTestingEngine:
    """
    Business Logic Layer for Transfusion Transmissible Infection (TTI) Lab Testing.
    """

    @staticmethod
    def submit_lab_test_results(
        bag_id: int,
        hiv_result: str = "NON_REACTIVE",
        hbsag_result: str = "NON_REACTIVE",
        hcv_result: str = "NON_REACTIVE",
        vdrl_result: str = "NON_REACTIVE",
        malaria_result: str = "NON_REACTIVE",
        nat_test_result: str = "NEGATIVE",
        technician_user_id: int = 1,
        lab_notes: Optional[str] = None
    ) -> SerologyTestRecord:
        """
        Processes lab test results.
        If any marker is reactive or NAT positive, flags bag as FAILED and places into QUARANTINE.
        Otherwise, flags bag as PASSED and allows transition to AVAILABLE.
        """
        bag = BloodBagService.get_bag_by_id(bag_id)

        # Check for reactive markers
        reactive_markers = []
        if hiv_result != "NON_REACTIVE":
            reactive_markers.append(f"HIV ({hiv_result})")
        if hbsag_result != "NON_REACTIVE":
            reactive_markers.append(f"HBsAg ({hbsag_result})")
        if hcv_result != "NON_REACTIVE":
            reactive_markers.append(f"HCV ({hcv_result})")
        if vdrl_result != "NON_REACTIVE":
            reactive_markers.append(f"Syphilis VDRL ({vdrl_result})")
        if malaria_result != "NON_REACTIVE":
            reactive_markers.append(f"Malaria ({malaria_result})")
        if nat_test_result != "NEGATIVE":
            reactive_markers.append(f"NAT Nucleic Acid ({nat_test_result})")

        is_passed = len(reactive_markers) == 0
        overall_status = "PASSED" if is_passed else "FAILED"

        test_code = generate_unique_serology_code()

        record = SerologyTestRecord(
            test_code=test_code,
            bag_id=bag.id,
            hiv_result=hiv_result,
            hbsag_result=hbsag_result,
            hcv_result=hcv_result,
            vdrl_result=vdrl_result,
            malaria_result=malaria_result,
            nat_test_result=nat_test_result,
            overall_quality_status=overall_status,
            tested_by_technician_id=technician_user_id,
            lab_notes=lab_notes
        )
        db.session.add(record)

        bag.testing_date = date.today()
        bag.quality_status = overall_status

        if not is_passed:
            # Automatic Quarantine Isolation
            QuarantineService.place_bag_in_quarantine(
                {
                    "bag_id": bag.id,
                    "reason": f"Reactive TTI Marker Detected: {', '.join(reactive_markers)}",
                    "suspected_issue": f"Serology Test Code {test_code} failed quality control."
                },
                user_id=technician_user_id
            )
        else:
            # Transition from TESTING -> AVAILABLE if currently in TESTING status
            if bag.status == BloodBagStatus.TESTING.value:
                BloodBagService.transition_bag_status(
                    bag_id=bag.id,
                    target_status=BloodBagStatus.AVAILABLE.value,
                    reason=f"Passed all serology & NAT lab tests (Code {test_code})",
                    changed_by_user_id=technician_user_id
                )

        db.session.commit()
        logger.info(f"Submitted Serology Test '{test_code}' for Bag '{bag.bag_code}': Result={overall_status}")
        return record
