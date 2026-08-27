"""
Blood Bank Cold Chain Logistics & Thermal Modeling Engine.
Calculates transport box ice pack sublimation rate, temperature excursion risks during transit,
and transport leg telemetry verification.
"""

import logging
import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.database.connection import db
from app.database.models.logistics import TransportContainer, TransportLeg

logger = logging.getLogger(__name__)


class LogisticsDispatchEngine:
    """
    Thermal Modeling & Cold Chain Logistics Engine.
    """

    @staticmethod
    def calculate_ice_pack_thermal_endurance(
        ambient_temp_celsius: float,
        ice_pack_mass_kg: float,
        container_insulation_r_value: float = 4.5
    ) -> Dict[str, Any]:
        """
        Models ice pack phase change endurance in hours based on ambient temperature and insulation.
        Latent heat of fusion of ice = 334 kJ/kg.
        """
        temp_diff = max(1.0, ambient_temp_celsius - 4.0) # Target inside temp = 4°C
        heat_transfer_rate_watts = (temp_diff / container_insulation_r_value) * 1.8
        total_cooling_capacity_kj = ice_pack_mass_kg * 334.0
        endurance_hours = (total_cooling_capacity_kj * 1000.0) / (heat_transfer_rate_watts * 3600.0)

        endurance_hours = round(min(72.0, max(2.0, endurance_hours)), 1)
        excursion_risk = "HIGH" if endurance_hours < 8.0 else ("MEDIUM" if endurance_hours < 18.0 else "LOW")

        return {
            "ambient_temp_celsius": ambient_temp_celsius,
            "ice_pack_mass_kg": ice_pack_mass_kg,
            "estimated_cooling_endurance_hours": endurance_hours,
            "excursion_risk": excursion_risk,
            "recommended_max_transit_time_hours": round(endurance_hours * 0.8, 1)
        }

    @staticmethod
    def register_transport_leg_dispatch(
        container_code: str,
        origin_facility: str,
        destination_facility: str,
        courier_name: str,
        initial_temp_celsius: float = 4.0
    ) -> Dict[str, Any]:
        """
        Registers a new temperature-controlled transport leg for blood units in transit.
        """
        container = TransportContainer.query.filter_by(container_code=container_code).first()
        if not container:
            container = TransportContainer(
                container_code=container_code,
                container_type="COOL_BOX_GEL",
                capacity_bags=10,
                status="IN_TRANSIT"
            )
            db.session.add(container)
            db.session.flush()

        leg = TransportLeg(
            container_id=container.id,
            shipment_code=f"TR-{container.id}-{datetime.now().strftime('%M%S')}",
            origin=origin_facility,
            destination=destination_facility,
            courier_name=courier_name,
            departure_time=datetime.now(timezone.utc),
            status="IN_TRANSIT",
            current_temp_celsius=initial_temp_celsius
        )
        db.session.add(leg)
        db.session.commit()

        logger.info(f"Registered Transport Leg {leg.shipment_code} from {origin_facility} to {destination_facility}")

        return {
            "shipment_code": leg.shipment_code,
            "container_code": container_code,
            "origin": origin_facility,
            "destination": destination_facility,
            "status": "IN_TRANSIT"
        }
