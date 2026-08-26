from flask import Blueprint, jsonify
from app.config import Config
from app.database.connection import db

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check and database diagnostics endpoint.
    """
    db_status = "healthy"
    try:
        db.session.execute(db.text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return jsonify({
        "status": "online" if db_status == "healthy" else "degraded",
        "app_name": Config.PROJECT_NAME,
        "version": Config.VERSION,
        "environment": Config.ENVIRONMENT,
        "database": db_status
    }), 200 if db_status == "healthy" else 503
