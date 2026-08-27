"""
Unit Tests for Storage Capacity & Stock Reconciliation (Member 4).
"""

from app.services.storage_service import StorageService
from app.services.reconciliation_service import ReconciliationService


def test_storage_unit_creation_and_capacity(app):
    with app.app_context():
        unit = StorageService.create_storage_unit({
            "name": "Test Fridge 101",
            "unit_type": "Blood Bank Refrigerator",
            "section_location": "Lab Section A",
            "total_capacity_units": 50,
            "min_temp_celsius": 2.0,
            "max_temp_celsius": 6.0
        })
        assert unit.id is not None
        assert unit.total_capacity_units == 50
        assert unit.available_capacity == 50


def test_stock_reconciliation_audit(app):
    with app.app_context():
        payload = {
            "items": [
                {"blood_group": "O+", "component_type": "Whole Blood", "physical_count": 25}
            ],
            "audit_reason": "End-of-month physical count verification"
        }
        results = ReconciliationService.execute_stock_reconciliation(payload, user_id=1)
        assert len(results) == 1
        assert results[0]["blood_group"] == "O+"
        assert results[0]["physical_count"] == 25
