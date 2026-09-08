"""
Donor History Timeline & Event Sourcing Query Service.
Retrieves and aggregates complete chronological donor histories, screening records,
blood bag lineage, and admin verifications.
"""

import logging
from typing import Dict, Any, List, Optional
from app.database.models.donor import DonorProfile
from app.database.models.donation import DonationRecord
from app.database.models.history_audit import DonorHistoryTimeline

logger = logging.getLogger(__name__)


class DonorHistoryEventService:
    """
    Business Logic & Query Layer for Donor Timelines and Admin Monitoring.
    """

    @staticmethod
    def get_donor_chronological_history(donor_id: int) -> List[Dict[str, Any]]:
        """
        Fetches chronological history items for a specific donor.
        """
        timelines = DonorHistoryTimeline.query.filter_by(donor_id=donor_id)\
            .order_by(DonorHistoryTimeline.event_date.desc()).all()
        return [t.to_dict() for t in timelines]

    @staticmethod
    def admin_search_and_filter_donors(
        query_str: Optional[str] = None,
        blood_group: Optional[str] = None,
        eligibility_status: Optional[str] = None,
        donation_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Comprehensive Admin search and filter across donors, health checkup vitals, and histories.
        """
        q = DonorProfile.query

        if blood_group:
            q = q.filter(DonorProfile.blood_group == blood_group.upper().strip())

        if eligibility_status:
            q = q.filter(DonorProfile.eligibility_status == eligibility_status.upper().strip())

        donors = q.all()
        results = []

        for d in donors:
            # Check text query
            if query_str:
                q_lower = query_str.lower().strip()
                name_match = (d.user and q_lower in d.user.name.lower()) if d.user else False
                email_match = (d.user and q_lower in d.user.email.lower()) if d.user else False
                city_match = q_lower in d.city.lower() if d.city else False
                if not (name_match or email_match or city_match):
                    continue

            # Fetch latest donation and history
            latest_don = DonationRecord.query.filter_by(donor_id=d.id)\
                .order_by(DonationRecord.created_at.desc()).first()

            if donation_status and latest_don:
                if latest_don.donation_status.upper() != donation_status.upper():
                    continue

            history_items = DonorHistoryTimeline.query.filter_by(donor_id=d.id)\
                .order_by(DonorHistoryTimeline.event_date.desc()).all()

            donor_dict = {
                "donor_id": d.id,
                "donor_name": d.user.name if d.user else "Donor",
                "email": d.user.email if d.user else "",
                "phone": d.user.phone if d.user else "",
                "blood_group": d.blood_group,
                "city": d.city,
                "eligibility_status": d.eligibility_status,
                "last_donation_date": d.last_donation_date.isoformat() if d.last_donation_date else None,
                "latest_donation": latest_don.to_dict() if latest_don else None,
                "history_timeline": [h.to_dict() for h in history_items]
            }
            results.append(donor_dict)

        return results
