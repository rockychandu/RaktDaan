import os
from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.database.connection import init_db
from app.database.seed import seed_all
from app.auth.routes import donor_bp, admin_bp, health_bp, ui_bp
from app.users.exceptions import DomainException

def create_app(config_class=Config):
    """
    Application Factory for RaktDaan Enterprise Backend.
    """
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(config_class)

    # Configure CORS
    CORS(app, origins=app.config.get("CORS_ALLOWED_ORIGINS", "*"))

    # Initialize Database
    init_db(app)

    # Register Blueprints
    app.register_blueprint(ui_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(health_bp)

    # Seed Database on Startup
    with app.app_context():
        seed_all()

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
