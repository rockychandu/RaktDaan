"""
Blood Bank Inventory Operating Policy & Storage Specs (Member 4).
Defines temperature tolerances, out-of-fridge time limits, and transport container specs.
"""

from typing import Dict, Any, Tuple


class InventoryOperatingPolicy:
    """
    Storage Equipment Temperature & Transport Protocol Specs.
    """

    # Temperature Specs (°C) by Component Type
    TEMPERATURE_SPECIFICATIONS: Dict[str, Dict[str, float]] = {
        "Whole Blood": {"min_temp": 2.0, "max_temp": 6.0, "target_temp": 4.0},
        "PRBC": {"min_temp": 2.0, "max_temp": 6.0, "target_temp": 4.0},
        "Packed Red Blood Cells": {"min_temp": 2.0, "max_temp": 6.0, "target_temp": 4.0},
        "FFP": {"min_temp": -30.0, "max_temp": -18.0, "target_temp": -25.0},
        "Fresh Frozen Plasma": {"min_temp": -30.0, "max_temp": -18.0, "target_temp": -25.0},
        "Platelets": {"min_temp": 20.0, "max_temp": 24.0, "target_temp": 22.0},
        "Platelet Concentrate": {"min_temp": 20.0, "max_temp": 24.0, "target_temp": 22.0},
        "Cryoprecipitate": {"min_temp": -30.0, "max_temp": -18.0, "target_temp": -25.0}
    }

    # Maximum Allowed Out-Of-Fridge (OOF) Time in Minutes before bag MUST be discarded
    MAX_OUT_OF_FRIDGE_MINUTES = 30 # 30-Minute Rule

    # Agitation Requirement: Platelets MUST be constantly agitated on a flatbed shaker at 20-24°C
    PLATELET_AGITATION_REQUIRED = True

    @classmethod
    def is_temperature_valid(cls, component_type: str, measured_temp_celsius: float) -> bool:
        """
        Validates whether a measured temperature is within the safe storage tolerance for given component.
        """
        specs = cls.TEMPERATURE_SPECIFICATIONS.get(component_type)
        if not specs:
            # Default to PRBC specs (2-6°C) if component type not found
            return 2.0 <= measured_temp_celsius <= 6.0
        return specs["min_temp"] <= measured_temp_celsius <= specs["max_temp"]

    @classmethod
    def get_temperature_range(cls, component_type: str) -> Tuple[float, float]:
        """
        Returns (min_temp, max_temp) tuple for a component.
        """
        specs = cls.TEMPERATURE_SPECIFICATIONS.get(component_type)
        if not specs:
            return (2.0, 6.0)
        return (specs["min_temp"], specs["max_temp"])
