"""
Unit Tests for Cold Chain Monitoring Engine (Member 4).
"""

from app.services.storage_service import StorageService
from app.services.cold_chain_monitoring_engine import ColdChainMonitoringEngine
from app.services.notification_service import NotificationService


def test_cold_chain_temperature_reading_and_excursion(app):
    with app.app_context():
        unit = StorageService.create_storage_unit({
            "name": "Plasma Freezer 301",
            "unit_type": "Deep Freezer (-30C)",
            "section_location": "Lab Section B",
            "total_capacity_units": 40,
            "min_temp_celsius": -30.0,
            "max_temp_celsius": -18.0
        })

        # 1. Normal Reading (-25.0°C)
        log1 = ColdChainMonitoringEngine.record_temperature_reading(
            storage_unit_id=unit.id,
            temp_celsius=-25.0
        )
        assert log1.is_excursion is False

        # 2. Excursion Reading (-10.0°C -> Too warm!)
        log2 = ColdChainMonitoringEngine.record_temperature_reading(
            storage_unit_id=unit.id,
            temp_celsius=-10.0
        )
        assert log2.is_excursion is True

        # Verify breach notification triggered
        unreads = NotificationService.get_unread_notifications()
        assert len(unreads) >= 1
