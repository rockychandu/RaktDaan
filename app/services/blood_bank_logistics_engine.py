"""
Blood Bank Logistics & Cold Chain Transport Engine (Member 4).
Handles transport box initialization, cool pack mass calculation, delivery route SLA estimation,
and arrival temperature validation.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.logistics import TransportContainer, TransportLeg
from app.database.models.inventory_extended import BloodDispatch

logger = logging.getLogger(__name__)


class BloodBankLogisticsEngine:
    """
    Business Logic Layer for Cold Chain Logistics & Dispatch Container Tracking.
    """

    @staticmethod
    def calculate_coolant_ice_pack_requirement(
        bag_count: int,
        transit_duration_hours: float,
        ambient_temp_celsius: float = 35.0
    ) -> Dict[str, Any]:
        """
        Calculates recommended ice pack mass (kg) needed for transport cool box.
        Based on thermal transfer formula: Q = U * A * (T_ambient - T_inside) * time
        """
        base_ice_kg_per_bag = 0.25 # 250g ice per unit
        duration_factor = max(1.0, transit_duration_hours / 4.0)
        temp_delta_factor = max(1.0, (ambient_temp_celsius - 4.0) / 30.0)

        required_ice_packs_kg = bag_count * base_ice_kg_per_bag * duration_factor * temp_delta_factor

        return {
            "bag_count": bag_count,
            "transit_duration_hours": transit_duration_hours,
            "ambient_temp_celsius": ambient_temp_celsius,
            "recommended_ice_packs_kg": round(required_ice_packs_kg, 2),
            "ice_pack_units_count": max(2, int(required_ice_packs_kg / 0.4)) # 400g packs
        }

    @staticmethod
    def create_transport_container(
        container_code: str,
        name: str,
        container_type: str = "INSULATED_COOL_BOX",
        capacity_bags: int = 10,
        coolant_type: str = "WET_ICE_PACKS",
        max_hold_time_hours: float = 6.0
    ) -> TransportContainer:
        """
        Registers new insulated blood transport box in logistics database.
        """
        container = TransportContainer(
            container_code=container_code,
            name=name,
            container_type=container_type,
            capacity_bags=capacity_bags,
            coolant_type=coolant_type,
            max_hold_time_hours=max_hold_time_hours,
            status="AVAILABLE"
        )
        db.session.add(container)
        db.session.commit()
        logger.info(f"Created Transport Container '{container_code}' (Capacity: {capacity_bags} bags)")
        return container

    @staticmethod
    def initiate_shipment(
        dispatch_id: int,
        container_id: int,
        driver_name: str,
        driver_phone: str,
        origin_location: str,
        destination_hospital: str,
        departure_temp_celsius: float = 4.0,
        seal_number: Optional[str] = None
    ) -> TransportLeg:
        """
        Initiates blood shipment leg to hospital destination.
        """
        container = TransportContainer.query.get(container_id)
        if container:
            container.status = "IN_TRANSIT"

        shipment_code = f"SHP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{dispatch_id:04d}"
        now = datetime.now(timezone.utc)
        eta = now + timedelta(hours=2) # 2-hour standard SLA

        shipment = TransportLeg(
            shipment_code=shipment_code,
            container_id=container_id,
            dispatch_id=dispatch_id,
            origin_location=origin_location,
            destination_hospital=destination_hospital,
            driver_name=driver_name,
            driver_phone=driver_phone,
            departure_time=now,
            estimated_arrival_time=eta,
            departure_temp_celsius=departure_temp_celsius,
            status="IN_TRANSIT",
            seal_number=seal_number or f"SEAL-{shipment_code}"
        )
        db.session.add(shipment)
        db.session.commit()

        logger.info(f"Initiated Shipment '{shipment_code}' for Dispatch {dispatch_id} to '{destination_hospital}'")
        return shipment

    @staticmethod
    def complete_delivery(
        shipment_id: int,
        arrival_temp_celsius: float
    ) -> Dict[str, Any]:
        """
        Marks shipment delivered upon hospital receipt and validates cold chain seal.
        """
        shipment = TransportLeg.query.get(shipment_id)
        if not shipment:
            return {"error": f"Shipment ID {shipment_id} not found."}

        now = datetime.now(timezone.utc)
        shipment.actual_arrival_time = now
        shipment.arrival_temp_celsius = arrival_temp_celsius

        # Cold chain breach check (Must remain 1°C to 10°C during transport)
        is_breached = arrival_temp_celsius < 1.0 or arrival_temp_celsius > 10.0
        shipment.status = "BREACHED" if is_breached else "DELIVERED"

        if shipment.container_id:
            container = TransportContainer.query.get(shipment.container_id)
            if container:
                container.status = "AVAILABLE"

        db.session.commit()

        return {
            "shipment_id": shipment_id,
            "shipment_code": shipment.shipment_code,
            "destination_hospital": shipment.destination_hospital,
            "arrival_temp_celsius": arrival_temp_celsius,
            "is_cold_chain_breached": is_breached,
            "status": shipment.status,
            "delivered_at": now.isoformat()
        }
