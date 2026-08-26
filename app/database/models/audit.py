from datetime import datetime, timezone
from app.database.connection import db
from app.database.base import BaseModelMixin

class SecurityAuditLog(db.Model, BaseModelMixin):
    """
    High-Security System Event & Vulnerability Audit Trail Table.
    """
    __tablename__ = "security_audit_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)
    severity = db.Column(db.String(20), nullable=False, default="INFO") # INFO, WARNING, CRITICAL
    actor_email = db.Column(db.String(150), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    endpoint = db.Column(db.String(255), nullable=True)
    details = db.Column(db.Text, nullable=True)


class SystemEventLog(db.Model, BaseModelMixin):
    """
    System Life-cycle & Maintenance Event Log.
    """
    __tablename__ = "system_event_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module_name = db.Column(db.String(50), nullable=False)
    event_name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)


class ApiAccessLog(db.Model, BaseModelMixin):
    """
    API Traffic & Diagnostics Metrics Log Table.
    """
    __tablename__ = "api_access_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    method = db.Column(db.String(10), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    execution_time_ms = db.Column(db.Float, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
