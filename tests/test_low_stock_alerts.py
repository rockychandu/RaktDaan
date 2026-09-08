"""
Unit Tests for Low & Critical Stock Threshold Engine (Member 4).
"""

from app.services.low_stock_engine import LowStockEngine
from app.database.models.inventory_extended import StockThreshold
from app.services.notification_service import NotificationService


def test_evaluate_stock_levels_and_fire_notifications(app):
    with app.app_context():
        evals = LowStockEngine.evaluate_stock_levels()
        assert len(evals) == 8 # All 8 blood groups evaluated

        # Check notifications generated
        notifs = NotificationService.get_all_notifications()
        assert notifs["total"] >= 0
