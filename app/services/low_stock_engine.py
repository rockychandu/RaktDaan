"""
Low & Critical Stock Threshold Monitoring Engine (Member 4).
Evaluates current available stock against configurable per-blood-group thresholds and generates internal notifications.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.database.connection import db
from app.database.models.blood_bank import BloodInventory
from app.database.models.inventory_extended import StockThreshold
from app.common.constants import (
    StockLevelStatus, DEFAULT_STOCK_THRESHOLDS, NotificationCategory, NotificationPriority
)
from app.users.models import BloodGroup
from app.services.inventory_service import InventoryService
from app.services.notification_service import NotificationService
from app.schemas.inventory_schemas import StockThresholdUpdateSchema

logger = logging.getLogger(__name__)


class LowStockEngine:
    """
    Stock Threshold Evaluation & Internal Alert Trigger Engine.
    """

    @staticmethod
    def initialize_default_thresholds():
        """
        Initializes default threshold rows for all 8 human blood groups if missing.
        """
        for bg, values in DEFAULT_STOCK_THRESHOLDS.items():
            existing = StockThreshold.query.filter_by(blood_group=bg).first()
            if not existing:
                threshold = StockThreshold(
                    blood_group=bg,
                    minimum_units=values["minimum"],
                    critical_units=values["critical"],
                    status=StockLevelStatus.NORMAL.value
                )
                db.session.add(threshold)
        db.session.commit()

    @staticmethod
    def evaluate_stock_levels() -> List[Dict[str, Any]]:
        """
        Evaluates current available inventory against stock thresholds and generates alerts.
        """
        LowStockEngine.initialize_default_thresholds()
        InventoryService.sync_all_blood_groups_inventory()

        thresholds = StockThreshold.query.all()
        evaluations = []

        for thresh in thresholds:
            inv = BloodInventory.query.filter_by(blood_group=thresh.blood_group).first()
            available = inv.units_available if inv else 0

            old_status = thresh.status
            new_status = StockLevelStatus.NORMAL.value

            if available <= thresh.critical_units:
                new_status = StockLevelStatus.CRITICAL.value
            elif available <= thresh.minimum_units:
                new_status = StockLevelStatus.LOW.value

            thresh.status = new_status
            thresh.last_evaluated_at = datetime.now(timezone.utc)

            # Fire Notification if stock is LOW or CRITICAL
            if new_status == StockLevelStatus.CRITICAL.value:
                NotificationService.create_notification(
                    title=f"CRITICAL STOCK ALERT: Blood Group {thresh.blood_group}",
                    message=f"CRITICAL: Blood Group {thresh.blood_group} has only {available} units available (Critical threshold: {thresh.critical_units}). Immediate donation drive required!",
                    category=NotificationCategory.CRITICAL_STOCK.value,
                    priority=NotificationPriority.CRITICAL.value,
                    related_entity_type="StockThreshold",
                    related_entity_id=thresh.blood_group
                )
            elif new_status == StockLevelStatus.LOW.value:
                NotificationService.create_notification(
                    title=f"Low Stock Alert: Blood Group {thresh.blood_group}",
                    message=f"LOW STOCK: Blood Group {thresh.blood_group} has {available} units available (Minimum threshold: {thresh.minimum_units}).",
                    category=NotificationCategory.LOW_STOCK.value,
                    priority=NotificationPriority.HIGH.value,
                    related_entity_type="StockThreshold",
                    related_entity_id=thresh.blood_group
                )

            evaluations.append({
                "blood_group": thresh.blood_group,
                "available_units": available,
                "minimum_threshold": thresh.minimum_units,
                "critical_threshold": thresh.critical_units,
                "status": new_status,
                "status_changed": (old_status != new_status)
            })

        db.session.commit()
        logger.info(f"Evaluated stock levels for {len(evaluations)} blood groups.")
        return evaluations

    @staticmethod
    def update_threshold_config(data_dict: Dict[str, Any]) -> StockThreshold:
        """
        Updates stock threshold configuration for a specific blood group.
        """
        schema = StockThresholdUpdateSchema(**data_dict)
        thresh = StockThreshold.query.filter_by(blood_group=schema.blood_group).first()
        if not thresh:
            thresh = StockThreshold(blood_group=schema.blood_group)
            db.session.add(thresh)

        thresh.minimum_units = schema.minimum_units
        thresh.critical_units = schema.critical_units

        db.session.commit()
        # Re-evaluate stock level
        LowStockEngine.evaluate_stock_levels()
        return thresh
