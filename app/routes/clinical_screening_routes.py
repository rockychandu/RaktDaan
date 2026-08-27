"""
Clinical Screening & Rule Engine REST API Blueprint.
Endpoints: /api/v1/clinical-screening
"""

from flask import Blueprint, request, jsonify
from app.auth.dependencies import require_login, require_admin, get_current_user
from app.services.donation_prescreening_service import DonorPrescreeningService
from app.services.clinical_lab_testing_engine import ClinicalLabTestingEngine
from app.schemas.clinical_screening_schemas import ComprehensiveHealthCheckupSchema
from pydantic import ValidationError as PydanticValError

clinical_screening_api_bp = Blueprint("clinical_screening_api", __name__, url_prefix="/api/v1/clinical-screening")


@clinical_screening_api_bp.route("/evaluate", methods=["POST"])
@require_login
def evaluate_clinical_health_checkup():
    """Evaluates donor health checkup against master clinical screening rules."""
    user = get_current_user()
    if not user.donor_profile:
        return jsonify({"status": "error", "message": "Donor Profile not found"}), 404

    data = request.get_json(silent=True) or {}
    try:
        schema = ComprehensiveHealthCheckupSchema(**data)
        res = DonorPrescreeningService.evaluate_and_submit_prescreening(
            donor_profile_id=user.donor_profile.id,
            weight_kg=schema.weight_kg,
            hemoglobin_level=schema.hemoglobin_level,
            blood_pressure_sys=schema.blood_pressure_sys,
            blood_pressure_dia=schema.blood_pressure_dia,
            pulse_rate=schema.pulse_rate,
            temp_celsius=schema.temp_celsius,
            has_chronic_illness=schema.has_chronic_illness,
            is_on_medication=schema.is_on_medication,
            has_recent_infection=schema.has_recent_infection,
            has_recent_hospitalization=schema.has_recent_hospitalization,
            has_recent_surgery=schema.has_recent_surgery,
            surgery_type=schema.surgery_type or "NONE",
            medication_category=schema.medication_category or "GENERAL",
            has_recent_vaccination=schema.has_recent_vaccination,
            vaccine_type=schema.vaccine_type or "INACTIVATED",
            is_currently_pregnant=schema.is_currently_pregnant,
            is_breastfeeding=schema.is_breastfeeding,
            recent_delivery_within_12_months=schema.recent_delivery_within_12_months,
            collection_center=schema.collection_center or "Central RaktDaan Blood Bank"
        )
        status_code = 200 if res["is_passed"] else 400
        return jsonify(res), status_code
    except PydanticValError as ve:
        return jsonify({"status": "error", "detail": ve.errors()}), 422
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@clinical_screening_api_bp.route("/serology/process", methods=["POST"])
@require_admin
def process_serology_panel():
    """Processes serology and NAT pathogen panel for a blood bag."""
    data = request.get_json(silent=True) or {}
    bag_id = data.get("bag_id")
    if not bag_id:
        return jsonify({"status": "error", "message": "bag_id is required"}), 400

    user = get_current_user()
    try:
        res = ClinicalLabTestingEngine.process_complete_serology_panel(
            bag_id=bag_id,
            hiv_result=data.get("hiv_result", "NEGATIVE"),
            hbv_result=data.get("hbv_result", "NEGATIVE"),
            hcv_result=data.get("hcv_result", "NEGATIVE"),
            syphilis_result=data.get("syphilis_result", "NEGATIVE"),
            malaria_result=data.get("malaria_result", "NEGATIVE"),
            nat_hiv_rna=data.get("nat_hiv_rna", "NEGATIVE"),
            nat_hbv_dna=data.get("nat_hbv_dna", "NEGATIVE"),
            nat_hcv_rna=data.get("nat_hcv_rna", "NEGATIVE"),
            abo_subgroup=data.get("abo_subgroup", "A1"),
            rhd_phenotype=data.get("rhd_phenotype", "POSITIVE"),
            irregular_antibody_screen=data.get("irregular_antibody_screen", "NEGATIVE"),
            technician_user_id=user.id
        )
        return jsonify({"status": "success", "data": res}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
