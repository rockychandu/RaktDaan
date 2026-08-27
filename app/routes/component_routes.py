"""
REST API Blueprint for Blood Component Fractionation (Member 4).
"""

from flask import Blueprint, request, jsonify
from app.services.component_separation_engine import ComponentSeparationEngine
from app.common.exceptions import DomainException

component_api_bp = Blueprint("component_api", __name__, url_prefix="/api/components")


@component_api_bp.route("/separate", methods=["POST"])
def separate_whole_blood():
    """
    Separates a whole blood unit into child component bags.
    """
    try:
        data = request.get_json() or {}
        parent_bag_id = data.get("parent_bag_id")
        if not parent_bag_id:
            return jsonify({"status": "error", "message": "Field 'parent_bag_id' is required."}), 400

        record, child_bags = ComponentSeparationEngine.separate_whole_blood(
            parent_bag_id=int(parent_bag_id),
            technician_user_id=data.get("technician_user_id", 1),
            centrifuge_speed_rpm=data.get("centrifuge_speed_rpm", 3500),
            centrifuge_time_minutes=data.get("centrifuge_time_minutes", 15),
            prbc_volume_ml=data.get("prbc_volume_ml", 280),
            ffp_volume_ml=data.get("ffp_volume_ml", 220),
            platelet_volume_ml=data.get("platelet_volume_ml", 60)
        )

        return jsonify({
            "status": "success",
            "data": {
                "separation_record": record.to_dict(),
                "child_bags": [b.to_dict() for b in child_bags]
            }
        }), 201
    except DomainException as e:
        return jsonify({"status": "error", "message": e.message}), e.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
