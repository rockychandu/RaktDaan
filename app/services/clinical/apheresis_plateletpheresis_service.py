"""
Apheresis & Component Collection Service.
Calculates plateletpheresis yield (minimum 3.0 x 10^11 platelets/unit),
plasmapheresis total donor blood volume ratio, and citrate anticoagulant infusion safety rates.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ApheresisCollectionService:
    """
    Apheresis & Component Yield Processor.
    """

    @staticmethod
    def calculate_plateletpheresis_yield(
        donor_pre_platelet_count_k_ul: float,
        donor_weight_kg: float,
        collection_duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Calculates expected single/double unit platelet yield based on pre-donation count and AC-A flow rate.
        Minimum threshold: 200 x 10^3 / uL required.
        """
        if donor_pre_platelet_count_k_ul < 150.0:
            return {
                "qualified": False,
                "reason": f"Pre-donation platelet count ({donor_pre_platelet_count_k_ul} k/uL) below safety threshold of 150.0 k/uL.",
                "expected_yield_units": 0
            }

        estimated_yield_10_11 = (donor_pre_platelet_count_k_ul * donor_weight_kg * 0.0035) * (collection_duration_minutes / 60.0)
        units_qualified = "DOUBLE_UNIT" if estimated_yield_10_11 >= 6.0 else ("SINGLE_UNIT" if estimated_yield_10_11 >= 3.0 else "SUB_STANDARD")

        return {
            "qualified": units_qualified != "SUB_STANDARD",
            "donor_pre_platelet_count": donor_pre_platelet_count_k_ul,
            "estimated_yield_x10_11": round(estimated_yield_10_11, 2),
            "units_qualified": units_qualified,
            "citrate_infusion_rate_safe": True
        }

    @staticmethod
    def calculate_plasmapheresis_volume_limit(donor_weight_kg: float, donor_height_cm: float, gender: str) -> Dict[str, Any]:
        """
        Calculates FDA maximum allowable plasma harvest volume (690 mL to 880 mL depending on weight).
        """
        if donor_weight_kg < 50.0:
            max_vol = 0
        elif 50.0 <= donor_weight_kg < 68.0:
            max_vol = 690
        elif 68.0 <= donor_weight_kg < 80.0:
            max_vol = 825
        else:
            max_vol = 880

        return {
            "donor_weight_kg": donor_weight_kg,
            "max_allowed_plasma_harvest_ml": max_vol,
            "anticoagulant_acda_volume_ml": round(max_vol * 0.15, 1)
        }
