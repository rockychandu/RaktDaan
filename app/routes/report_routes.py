"""
Reporting & Export System REST API Blueprints (Member 4).
Endpoints: /api/v1/reports
"""

from flask import Blueprint, request, jsonify, Response
from app.auth.dependencies import require_admin
from app.services.reporting_export_engine import ReportingExportEngine

report_api_bp = Blueprint("report_api", __name__, url_prefix="/api/v1/reports")


@report_api_bp.route("/<string:report_type>", methods=["GET"])
@require_admin
def get_report(report_type: str):
    """Generates and returns JSON report payload."""
    args = request.args.to_dict()
    report = ReportingExportEngine.generate_report(report_type, args)
    return jsonify(report), 200


@report_api_bp.route("/export/<string:report_type>", methods=["GET"])
@require_admin
def export_report_csv(report_type: str):
    """Generates and streams downloadable CSV report file locally."""
    args = request.args.to_dict()
    csv_content, filename = ReportingExportEngine.export_report_to_csv(report_type, args)

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )
