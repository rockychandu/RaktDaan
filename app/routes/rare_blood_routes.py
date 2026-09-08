"""
Rare Blood Registry & Cryo Archive REST API Blueprint (Member 3 & Member 4).
"""

import logging
from flask import Blueprint, request, jsonify

from app.services.rare_blood_registry_service import RareBloodRegistryService
from app.database.models.rare_blood import RareDonorRegistry, CryoFrozenBagArchive

logger = logging.getLogger(__name__)

rare_blood_bp = Blueprint("rare_blood_bp", __name__, url_prefix="/api/rare-blood")


@rare_blood_bp.route("/registry", methods=["GET"])
def list_rare_donors():
    donors = RareDonorRegistry.query.filter_by(is_deleted=False).all()
    return jsonify({
        "status": "success",
        "count": len(donors),
        "data": [d.to_dict() for d in donors]
    }), 200


@rare_blood_bp.route("/registry", methods=["POST"])
def register_rare_donor():
    payload = request.get_json() or {}
    try:
        entry = RareBloodRegistryService.register_rare_phenotype_donor(
            donor_id=payload.get("donor_id"),
            rare_phenotype_code=payload.get("rare_phenotype_code"),
            antigen_profile_summary=payload.get("antigen_profile_summary"),
            registered_by_user_id=payload.get("registered_by_user_id", 1),
            rarity_classification=payload.get("rarity_classification", "EXTREMELY_RARE")
        )
        return jsonify({
            "status": "success",
            "message": "Donor registered in Rare Phenotype Registry.",
            "data": entry.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error registering rare donor: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@rare_blood_bp.route("/cryo-archive", methods=["POST"])
def archive_cryo():
    payload = request.get_json() or {}
    try:
        archive = RareBloodRegistryService.archive_bag_cryopreservation(
            bag_id=payload.get("bag_id"),
            tank_number=payload.get("tank_number", "TANK-LN2-01"),
            canister_position=payload.get("canister_position", "Rack-1 / Box-A"),
            glycerol_concentration=payload.get("glycerol_concentration", 40.0)
        )
        return jsonify({
            "status": "success",
            "message": "Blood unit cryopreserved at -80°C successfully.",
            "data": archive.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error archiving cryo unit: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@rare_blood_bp.route("/cryo-archive/<int:archive_id>/thaw", methods=["POST"])
def thaw_cryo(archive_id):
    res = RareBloodRegistryService.initiate_deglycerolization_thaw(archive_id)
    return jsonify({"status": "success", "data": res}), 200
