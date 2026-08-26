from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config, DevelopmentConfig
from app.database.connection import init_db
from app.database.seed import seed_all
from app.auth.routes import donor_bp, admin_bp, health_bp
from app.users.exceptions import DomainException

def create_app(config_class=Config):
    """
    Application Factory for RaktDaan Enterprise Backend.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure CORS
    CORS(app, origins=app.config.get("CORS_ALLOWED_ORIGINS", "*"))

    # Initialize Database
    init_db(app)

    # Register Blueprints
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

    @app.route("/")
    def root():
        return jsonify({
            "status": "online",
            "app": app.config.get("PROJECT_NAME"),
            "version": app.config.get("VERSION", "2.0.0"),
            "docs": "/api/v1/auth/health"
        })

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
