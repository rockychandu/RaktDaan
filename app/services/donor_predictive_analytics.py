"""
Donor Longitudinal Health Analytics & Predictive Trajectory Engine.
Calculates hemoglobin recovery rates, ACC/AHA Blood Pressure staging,
donor lifetime retention scoring, and deferral recovery dates.
"""

from typing import Dict, Any, List
from datetime import date, datetime, timedelta
from app.database.models.donor import DonorProfile
from app.database.models.donation import DonationRecord, DonationScreening


class DonorPredictiveAnalyticsEngine:
    """
    Analytics engine for donor health trends and predictive modeling.
    """

    @staticmethod
    def classify_acc_aha_blood_pressure(sys: int, dia: int) -> Dict[str, str]:
        """
        Classifies BP according to ACC/AHA clinical guidelines.
        """
        if sys < 120 and dia < 80:
            stage = "NORMAL"
            desc = "Normal resting blood pressure."
        elif 120 <= sys <= 129 and dia < 80:
            stage = "ELEVATED"
            desc = "Elevated blood pressure. Lifestyle modifications recommended."
        elif (130 <= sys <= 139) or (80 <= dia <= 89):
            stage = "STAGE_1_HYPERTENSION"
            desc = "Stage 1 Hypertension."
        elif sys >= 140 or dia >= 90:
            stage = "STAGE_2_HYPERTENSION"
            desc = "Stage 2 Hypertension. Requires clinical monitoring."
        else:
            stage = "HYPERTENSIVE_CRISIS"
            desc = "Hypertensive Crisis. Consult physician immediately."

        return {"stage": stage, "description": desc}

    @staticmethod
    def calculate_hemoglobin_recovery(current_hb: float, target_hb: float = 13.5) -> Dict[str, Any]:
        """
        Estimates recovery days needed for donor hemoglobin to reach target levels post-donation.
        Standard erythropoiesis rate: ~0.15 g/dL per day.
        """
        if current_hb >= target_hb:
            return {
                "recovery_days": 0,
                "target_hb": target_hb,
                "current_hb": current_hb,
                "status": "OPTIMAL_HEMOGLOBIN"
            }

        deficit = target_hb - current_hb
        estimated_days = int(deficit / 0.15)

        return {
            "recovery_days": estimated_days,
            "target_hb": target_hb,
            "current_hb": current_hb,
            "estimated_recovery_date": (date.today() + timedelta(days=estimated_days)).isoformat(),
            "status": "RECOVERY_IN_PROGRESS"
        }

    @staticmethod
    def compute_donor_retention_score(donor_id: int) -> Dict[str, Any]:
        """
        Computes donor loyalty/retention score based on donation frequency and screening pass rate.
        """
        donor = DonorProfile.query.get(donor_id)
        if not donor:
            return {"retention_score": 0.0, "tier": "UNKNOWN"}

        total_donations = len(donor.donation_records) if donor.donation_records else 0
        if total_donations == 0:
            return {"retention_score": 10.0, "tier": "NOVICE_DONOR", "donations_count": 0}

        score = min(100.0, total_donations * 15.0)
        tier = "BRONZE" if score < 40 else ("SILVER" if score < 75 else "GOLD_HERO")

        return {
            "donor_id": donor_id,
            "donations_count": total_donations,
            "retention_score": score,
            "tier": tier,
            "total_volume_contributed_ml": total_donations * 450
        }
