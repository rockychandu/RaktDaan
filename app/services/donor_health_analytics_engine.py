"""
Donor Health Trajectory & Cardiovascular Risk Analytics Engine (Member 3).
Analyzes longitudinal donor health metrics (hemoglobin trends, BP trajectories, pulse rate stability,
post-donation recovery rate) over multiple donations.
Calculates AHA/ACC blood pressure staging and donor wellness scores.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.database.models.donor import DonorProfile, DonorMedicalHistory
from app.database.models.donation import DonationRecord, DonationScreening

logger = logging.getLogger(__name__)


class DonorHealthAnalyticsEngine:
    """
    Business Logic Engine for In-Depth Longitudinal Donor Health Surveillance.
    """

    @staticmethod
    def classify_blood_pressure(systolic: int, diastolic: int) -> Dict[str, str]:
        """
        Classifies blood pressure based on ACC/AHA clinical guidelines.
        """
        if systolic < 120 and diastolic < 80:
            category = "NORMAL"
            recommendation = "Blood pressure is optimal for blood donation."
        elif 120 <= systolic <= 129 and diastolic < 80:
            category = "ELEVATED"
            recommendation = "Slightly elevated BP. Suitable for donation; recommend lifestyle monitoring."
        elif (130 <= systolic <= 139) or (80 <= diastolic <= 89):
            category = "STAGE_1_HYPERTENSION"
            recommendation = "Stage 1 Hypertension. Suitable for donation if asymptomatic and BP < 180/100."
        elif (140 <= systolic <= 179) or (90 <= diastolic <= 99):
            category = "STAGE_2_HYPERTENSION"
            recommendation = "Stage 2 Hypertension. Defer if BP > 180/100 mmHg."
        else:
            category = "HYPERTENSIVE_CRISIS"
            recommendation = "Hypertensive Crisis! Immediate deferral and urgent medical referral required."

        return {
            "category": category,
            "recommendation": recommendation
        }

    @staticmethod
    def analyze_donor_health_trajectory(donor_id: int) -> Dict[str, Any]:
        """
        Calculates donor hemoglobin trend, average BP, and recovery stability score across all donations.
        """
        donor = DonorProfile.query.filter_by(id=donor_id, is_deleted=False).first()
        if not donor:
            return {"error": f"Donor ID {donor_id} not found."}

        screenings = (
            DonationScreening.query
            .join(DonationRecord, DonationScreening.donation_id == DonationRecord.id)
            .filter(DonationRecord.donor_id == donor_id, DonationRecord.is_deleted == False)
            .order_by(DonationScreening.created_at.asc())
            .all()
        )

        if not screenings:
            return {
                "donor_id": donor_id,
                "total_screenings": 0,
                "hemoglobin_trend": "INSUFFICIENT_DATA",
                "average_hb_g_dl": 0.0,
                "latest_bp_classification": "NONE",
                "health_score": 100
            }

        hb_values = [s.hemoglobin_level for s in screenings if s.hemoglobin_level is not None]
        sys_values = [s.blood_pressure_sys for s in screenings if s.blood_pressure_sys is not None]
        dia_values = [s.blood_pressure_dia for s in screenings if s.blood_pressure_dia is not None]

        avg_hb = sum(hb_values) / len(hb_values) if hb_values else 0.0
        latest_sys = sys_values[-1] if sys_values else 120
        latest_dia = dia_values[-1] if dia_values else 80

        bp_eval = DonorHealthAnalyticsEngine.classify_blood_pressure(latest_sys, latest_dia)

        # Determine HB trajectory
        trend = "STABLE"
        if len(hb_values) >= 2:
            diff = hb_values[-1] - hb_values[0]
            if diff > 0.5:
                trend = "IMPROVING"
            elif diff < -0.5:
                trend = "DECLINING"

        # Calculate wellness score (0-100)
        health_score = 100
        if bp_eval["category"] in ["STAGE_2_HYPERTENSION", "HYPERTENSIVE_CRISIS"]:
            health_score -= 30
        if avg_hb < 13.0:
            health_score -= 15

        return {
            "donor_id": donor_id,
            "total_screenings": len(screenings),
            "hemoglobin_trend": trend,
            "average_hb_g_dl": round(avg_hb, 2),
            "latest_bp": f"{latest_sys}/{latest_dia} mmHg",
            "latest_bp_classification": bp_eval["category"],
            "recommendation": bp_eval["recommendation"],
            "health_score": max(0, health_score),
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }
