import os
from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.database.connection import init_db
from app.database.seed import seed_all
from app.auth.routes import donor_bp, admin_bp, health_bp, ui_bp
from app.users.exceptions import DomainException

# Import Member 3 & Member 4 API Blueprints
from app.routes.donor_routes import donor_api_bp
from app.routes.donation_routes import donation_api_bp
from app.routes.inventory_routes import inventory_api_bp
from app.routes.blood_bag_routes import blood_bag_api_bp
from app.routes.storage_routes import storage_api_bp
from app.routes.reservation_routes import reservation_api_bp
from app.routes.dispatch_routes import dispatch_api_bp
from app.routes.quarantine_routes import quarantine_api_bp
from app.routes.return_routes import return_api_bp
from app.routes.notification_routes import notification_api_bp
from app.routes.report_routes import report_api_bp
from app.routes.analytics_routes import analytics_api_bp
from app.routes.serology_routes import serology_api_bp
from app.routes.component_routes import component_api_bp
from app.routes.cold_chain_routes import cold_chain_api_bp
from app.routes.sla_forecasting_routes import sla_forecasting_api_bp
from app.routes.safety_deferral_routes import safety_deferral_api_bp
from app.routes.logistics_routes import logistics_bp
from app.routes.rare_blood_routes import rare_blood_bp
from app.routes.health_analytics_routes import health_analytics_bp
from app.routes.admin_account_routes import admin_account_api_bp
from app.routes.donor_history_routes import donor_history_api_bp
from app.routes.clinical_screening_routes import clinical_screening_api_bp
from app.routes.volunteer_routes import volunteer_api_bp
from app.routes.emergency_request_routes import emergency_request_api_bp
from app.routes.blood_request_routes import blood_request_api_bp

# Import Background Scheduler
from app.services.background_scheduler import BackgroundJobScheduler


def create_app(config_class=Config):
    """
    Application Factory for RaktDaan Enterprise Backend.
    """
    app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/static")
    app.config.from_object(config_class)

    # Initialize CORS and Database
    CORS(app)
    init_db(app)

    # Register Blueprints
    app.register_blueprint(donor_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(ui_bp)

    # Member 3 & 4 Enterprise Blueprints
    app.register_blueprint(donor_api_bp)
    app.register_blueprint(donation_api_bp)
    app.register_blueprint(inventory_api_bp)
    app.register_blueprint(blood_bag_api_bp)
    app.register_blueprint(storage_api_bp)
    app.register_blueprint(reservation_api_bp)
    app.register_blueprint(dispatch_api_bp)
    app.register_blueprint(quarantine_api_bp)
    app.register_blueprint(return_api_bp)
    app.register_blueprint(notification_api_bp)
    app.register_blueprint(report_api_bp)
    app.register_blueprint(analytics_api_bp)
    app.register_blueprint(serology_api_bp)
    app.register_blueprint(component_api_bp)
    app.register_blueprint(cold_chain_api_bp)
    app.register_blueprint(sla_forecasting_api_bp)
    app.register_blueprint(safety_deferral_api_bp)
    app.register_blueprint(logistics_bp)
    app.register_blueprint(rare_blood_bp)
    app.register_blueprint(health_analytics_bp)
    app.register_blueprint(admin_account_api_bp)
    app.register_blueprint(donor_history_api_bp)
    app.register_blueprint(clinical_screening_api_bp)
    app.register_blueprint(volunteer_api_bp)
    app.register_blueprint(emergency_request_api_bp)
    app.register_blueprint(blood_request_api_bp)






    # Seed Database on Startup
    with app.app_context():
        seed_all()

    # Start Local Background Maintenance Scheduler (unless in testing mode)
    if not app.config.get("TESTING", False):
        BackgroundJobScheduler.start(app, interval_seconds=300)

    # Central Error Handlers
    @app.errorhandler(DomainException)
    def handle_domain_exception(error):
        response = {
            "success": False,
            "message": error.message,
            "detail": error.errors or error.message
        }
        return jsonify(response), error.status_code

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5050"))
    app.run(host="0.0.0.0", port=port, debug=True)
