"""
Unit Tests for Local Reporting & Analytics Engine (Member 4).
"""

from app.services.reporting_export_engine import ReportingExportEngine
from app.services.inventory_analytics_engine import InventoryAnalyticsEngine


def test_generate_report_and_csv_export(app):
    with app.app_context():
        # 1. Generate Current Inventory JSON Report
        report = ReportingExportEngine.generate_report("current_inventory")
        assert report["title"] == "Current Blood Bag Inventory Report"
        assert "data" in report

        # 2. Export CSV
        csv_str, filename = ReportingExportEngine.export_report_to_csv("current_inventory")
        assert "bag_code,blood_group" in csv_str
        assert filename.endswith(".csv")


def test_inventory_analytics_overview(app):
    with app.app_context():
        analytics = InventoryAnalyticsEngine.get_inventory_analytics_overview()
        assert "total_bags_collected" in analytics
        assert "wastage_percentage" in analytics
        assert "utilization_rate_percent" in analytics
