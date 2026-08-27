"""
Donor Module Analytics & Statistics Calculation Engine (Member 3).
Calculates donor population breakdown, monthly trends, repeat rates, and blood group distribution.
"""

import logging
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List
from sqlalchemy import func

from app.database.connection import db
from app.database.models.user import User
from app.database.models.donor import DonorProfile, DonorEligibility
from app.database.models.donation import DonationRecord
from app.users.models import EligibilityStatus, BloodGroup

logger = logging.getLogger(__name__)


class DonorAnalyticsService:
    """
    Analytics & Reporting Calculator for Donor Management.
    """

    @staticmethod
    def get_donor_dashboard_statistics() -> Dict[str, Any]:
        """
        Calculates key donor KPI dashboard statistics.
        """
        total_donors = DonorProfile.query.filter_by(is_deleted=False).count()

        active_donors = db.session.query(DonorProfile).join(User, DonorProfile.user_id == User.id)\
            .filter(DonorProfile.is_deleted == False, User.status == "ACTIVE").count()

        inactive_donors = total_donors - active_donors

        eligible_donors = DonorProfile.query.filter_by(
            eligibility_status=EligibilityStatus.ELIGIBLE.value,
            is_deleted=False
        ).count()

        deferred_donors = DonorProfile.query.filter(
            DonorProfile.eligibility_status.in_([
                EligibilityStatus.TEMPORARILY_INELIGIBLE.value,
                EligibilityStatus.PERMANENTLY_INELIGIBLE.value
            ]),
            DonorProfile.is_deleted == False
        ).count()

        # Donations this month & year
        now = datetime.now(timezone.utc)
        first_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        first_of_year = datetime(now.year, 1, 1, tzinfo=timezone.utc)

        donations_this_month = DonationRecord.query.filter(
            DonationRecord.donation_date >= first_of_month,
            DonationRecord.donation_status == "COMPLETED",
            DonationRecord.is_deleted == False
        ).count()

        donations_this_year = DonationRecord.query.filter(
            DonationRecord.donation_date >= first_of_year,
            DonationRecord.donation_status == "COMPLETED",
            DonationRecord.is_deleted == False
        ).count()

        # Blood group breakdown
        bg_counts = db.session.query(
            DonorProfile.blood_group,
            func.count(DonorProfile.id)
        ).filter(DonorProfile.is_deleted == False).group_by(DonorProfile.blood_group).all()

        blood_group_distribution = {bg.value: 0 for bg in BloodGroup}
        for bg, count in bg_counts:
            blood_group_distribution[bg] = count

        # Repeat vs First-Time Donors
        # Donors with > 1 completed donation
        repeat_donors_count = db.session.query(DonationRecord.donor_id)\
            .filter(DonationRecord.donation_status == "COMPLETED")\
            .group_by(DonationRecord.donor_id)\
            .having(func.count(DonationRecord.id) > 1).count()

        first_time_donors_count = max(0, total_donors - repeat_donors_count)
        repeat_rate_percent = round((repeat_donors_count / total_donors * 100), 1) if total_donors > 0 else 0.0

        return {
            "total_donors": total_donors,
            "active_donors": active_donors,
            "inactive_donors": inactive_donors,
            "eligible_donors": eligible_donors,
            "deferred_donors": deferred_donors,
            "donations_this_month": donations_this_month,
            "donations_this_year": donations_this_year,
            "repeat_donors_count": repeat_donors_count,
            "first_time_donors_count": first_time_donors_count,
            "repeat_rate_percent": repeat_rate_percent,
            "blood_group_distribution": blood_group_distribution
        }
