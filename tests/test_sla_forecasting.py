"""
Unit Tests for SLA Tracking, Demand Forecasting, and Compliance Audit Engines (Member 4).
"""

from app.services.hospital_sla_engine import HospitalSLAEngine
from app.services.demand_forecasting_engine import DemandForecastingEngine
from app.services.compliance_audit_engine import ComplianceAuditEngine


def test_demand_forecasting(app):
    with app.app_context():
        res = DemandForecastingEngine.calculate_blood_demand_forecast(days_window=30)
        assert res["window_days"] == 30
        assert len(res["forecasts"]) == 8


def test_hospital_sla_performance(app):
    with app.app_context():
        res = HospitalSLAEngine.calculate_hospital_sla_performance()
        assert "sla_compliance_rate_percent" in res


def test_compliance_audit(app):
    with app.app_context():
        res = ComplianceAuditEngine.run_compliance_audit()
        assert "is_compliant" in res
        assert "violations" in res
