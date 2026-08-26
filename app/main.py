from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.database.connection import db, init_db
from app.database.seed import seed_initial_admin
from app.auth.routes import auth_bp

def create_app(config_class=Config):
    """
    Application Factory for RaktDaan Flask app.
    Initializes extensions, routes, CORS, and seeds default admin account.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for Frontend integration (Member 2)
    CORS(app)

    # Initialize Database
    init_db(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)

    # Seed Admin on startup
    with app.app_context():
        seed_initial_admin()

    @app.route("/")
    def root():
        return jsonify({
            "status": "online",
            "app": app.config.get("PROJECT_NAME"),
            "version": "1.0.0"
        })

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
