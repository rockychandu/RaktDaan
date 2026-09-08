"""
Donor Engagement, Retention & Rewards Engine (Member 3).
Calculates donor milestone badges, retention scores, and automated return reminder eligibility dates.
"""

import logging
from datetime import date, timedelta
from typing import Dict, Any, List

from app.database.models.donor import DonorProfile
from app.database.models.donation import DonationRecord
from app.services.donor_service import DonorService
from app.services.eligibility_engine import DonorEligibilityEngine

logger = logging.getLogger(__name__)


class DonorEngagementEngine:
    """
    Business Logic Layer for Donor Loyalty Badges & Engagement Analytics.
    """

    @staticmethod
    def get_donor_engagement_profile(donor_id: int) -> Dict[str, Any]:
        """
        Calculates donor milestone tier, total donations, retention rating, and next reminder date.
        """
        donor = DonorService.get_donor_by_id(donor_id)
        completed_donations = DonationRecord.query.filter_by(
            donor_id=donor.id,
            donation_status="COMPLETED",
            is_deleted=False
        ).count()

        # Determine Milestone Tier
        if completed_donations >= 20:
            milestone_tier = "PLATINUM_HERO"
            badge_title = "Platinum Life Saver (20+ Donations)"
        elif completed_donations >= 10:
            milestone_tier = "GOLD_DONOR"
            badge_title = "Gold Hero (10+ Donations)"
        elif completed_donations >= 4:
            milestone_tier = "SILVER_DONOR"
            badge_title = "Silver Champion (4+ Donations)"
        elif completed_donations >= 1:
            milestone_tier = "BRONZE_DONOR"
            badge_title = "Bronze Voluntary Donor (1-3 Donations)"
        else:
            milestone_tier = "FIRST_TIME"
            badge_title = "First-Time Registered Donor"

        # Calculate Next Return Date
        next_eligible_date = DonorEligibilityEngine.calculate_next_eligible_date(donor.id)
        is_ready_now = date.today() >= next_eligible_date if next_eligible_date else True

        # Retention Score (0-100)
        retention_score = min(100, completed_donations * 15)

        return {
            "donor_id": donor.id,
            "donor_name": donor.user.name if donor.user else "Donor",
            "completed_donations_count": completed_donations,
            "milestone_tier": milestone_tier,
            "badge_title": badge_title,
            "retention_score": retention_score,
            "last_donation_date": donor.last_donation_date.isoformat() if donor.last_donation_date else None,
            "next_eligible_date": next_eligible_date.isoformat() if next_eligible_date else None,
            "is_ready_to_donate_now": is_ready_now
        }
