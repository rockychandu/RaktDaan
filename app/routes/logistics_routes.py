"""
Blood Bank Logistics & Transport REST API Blueprint (Member 4).
"""

import logging
from flask import Blueprint, request, jsonify

from app.services.blood_bank_logistics_engine import BloodBankLogisticsEngine
from app.database.models.logistics import TransportContainer, TransportLeg

logger = logging.getLogger(__name__)

logistics_bp = Blueprint("logistics_bp", __name__, url_prefix="/api/logistics")


@logistics_bp.route("/containers", methods=["GET"])
def list_containers():
    containers = TransportContainer.query.filter_by(is_deleted=False).all()
    return jsonify({
        "status": "success",
        "count": len(containers),
        "data": [c.to_dict() for c in containers]
    }), 200


@logistics_bp.route("/containers", methods=["POST"])
def create_container():
    payload = request.get_json() or {}
    try:
        container = BloodBankLogisticsEngine.create_transport_container(
            container_code=payload.get("container_code"),
            name=payload.get("name"),
            container_type=payload.get("container_type", "INSULATED_COOL_BOX"),
            capacity_bags=payload.get("capacity_bags", 10),
            coolant_type=payload.get("coolant_type", "WET_ICE_PACKS"),
            max_hold_time_hours=payload.get("max_hold_time_hours", 6.0)
        )
        return jsonify({
            "status": "success",
            "message": "Transport container registered successfully.",
            "data": container.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error creating container: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@logistics_bp.route("/calculate-coolant", methods=["POST"])
def calculate_coolant():
    payload = request.get_json() or {}
    res = BloodBankLogisticsEngine.calculate_coolant_ice_pack_requirement(
        bag_count=payload.get("bag_count", 1),
        transit_duration_hours=payload.get("transit_duration_hours", 2.0),
        ambient_temp_celsius=payload.get("ambient_temp_celsius", 35.0)
    )
    return jsonify({"status": "success", "data": res}), 200


@logistics_bp.route("/shipments", methods=["POST"])
def initiate_shipment():
    payload = request.get_json() or {}
    try:
        shipment = BloodBankLogisticsEngine.initiate_shipment(
            dispatch_id=payload.get("dispatch_id"),
            container_id=payload.get("container_id"),
            driver_name=payload.get("driver_name"),
            driver_phone=payload.get("driver_phone"),
            origin_location=payload.get("origin_location"),
            destination_hospital=payload.get("destination_hospital"),
            departure_temp_celsius=payload.get("departure_temp_celsius", 4.0),
            seal_number=payload.get("seal_number")
        )
        return jsonify({
            "status": "success",
            "message": "Shipment initiated successfully.",
            "data": shipment.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error initiating shipment: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@logistics_bp.route("/shipments/<int:shipment_id>/complete", methods=["POST"])
def complete_shipment(shipment_id):
    payload = request.get_json() or {}
    res = BloodBankLogisticsEngine.complete_delivery(
        shipment_id=shipment_id,
        arrival_temp_celsius=payload.get("arrival_temp_celsius", 4.5)
    )
    return jsonify({"status": "success", "data": res}), 200
