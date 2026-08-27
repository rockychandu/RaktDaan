"""
Donor Churn & Lapsing Probability Modeling Engine.
Evaluates time since last donation, deferred screening history, and communication responsiveness
to identify donors at risk of becoming permanently inactive.
"""

from typing import Dict, Any
from datetime import date, datetime, timedelta


class DonorChurnPredictorEngine:
    """
    Predictive engine for donor lapsing risk scoring.
    """

    @staticmethod
    def predict_donor_lapsing_risk(
        months_since_last_donation: float,
        total_lifetime_donations: int,
        deferral_count: int = 0
    ) -> Dict[str, Any]:
        """
        Calculates churn probability score (0.0 to 100.0%).
        """
        base_score = min(100.0, months_since_last_donation * 8.0)
        
        # Adjust for lifetime loyalty
        loyalty_discount = min(30.0, total_lifetime_donations * 5.0)
        
        # Adjust for deferral penalty
        deferral_penalty = deferral_count * 12.0

        raw_score = max(0.0, min(100.0, base_score - loyalty_discount + deferral_penalty))
        churn_risk = "HIGH" if raw_score > 70.0 else ("MEDIUM" if raw_score > 35.0 else "LOW")

        return {
            "months_since_last_donation": months_since_last_donation,
            "total_lifetime_donations": total_lifetime_donations,
            "deferral_count": deferral_count,
            "churn_probability_pct": round(raw_score, 1),
            "churn_risk_level": churn_risk,
            "intervention_recommended": churn_risk in ["MEDIUM", "HIGH"]
        }
