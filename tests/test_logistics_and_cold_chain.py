"""
Unit Tests for Cold Chain Logistics & Container Tracking (Member 4).
"""

from app.services.blood_bank_logistics_engine import BloodBankLogisticsEngine


def test_logistics_container_and_shipment_workflow(app):
    with app.app_context():
        # 1. Calculate coolant requirement
        coolant_info = BloodBankLogisticsEngine.calculate_coolant_ice_pack_requirement(
            bag_count=10,
            transit_duration_hours=4.0,
            ambient_temp_celsius=38.0
        )
        assert coolant_info["recommended_ice_packs_kg"] > 0
        assert coolant_info["ice_pack_units_count"] >= 2

        # 2. Register container
        container = BloodBankLogisticsEngine.create_transport_container(
            container_code="CONT-TEST-01",
            name="Validated Cool Box 01",
            capacity_bags=15
        )
        assert container.container_code == "CONT-TEST-01"

        # 3. Initiate shipment
        shipment = BloodBankLogisticsEngine.initiate_shipment(
            dispatch_id=1,
            container_id=container.id,
            driver_name="Ramesh Kumar",
            driver_phone="9876543210",
            origin_location="Central Blood Bank",
            destination_hospital="KEM Hospital",
            departure_temp_celsius=4.0
        )
        assert shipment.status == "IN_TRANSIT"

        # 4. Complete delivery
        delivery_res = BloodBankLogisticsEngine.complete_delivery(
            shipment_id=shipment.id,
            arrival_temp_celsius=5.2
        )
        assert delivery_res["status"] == "DELIVERED"
        assert delivery_res["is_cold_chain_breached"] is False
