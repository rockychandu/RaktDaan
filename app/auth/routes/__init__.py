"""
Auth Routes Blueprint Package
"""
from app.auth.routes.donor_routes import donor_bp
from app.auth.routes.admin_routes import admin_bp
from app.auth.routes.health_routes import health_bp

__all__ = ["donor_bp", "admin_bp", "health_bp"]
