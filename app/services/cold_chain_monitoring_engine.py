"""
Cold Chain Temperature Excursion Monitoring Engine (Member 4).
Evaluates storage equipment temperature sensor logs, detects cold chain breaches,
and triggers high-priority alerts.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.database.connection import db
from app.database.models.inventory_extended import StorageUnit
from app.database.models.cold_chain import TemperatureSensorLog
from app.common.constants import NotificationCategory, NotificationPriority
from app.services.notification_service import NotificationService
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)


class ColdChainMonitoringEngine:
    """
    Business Logic Engine for Cold Storage Temperature Surveillance.
    """

    @staticmethod
    def record_temperature_reading(
        storage_unit_id: int,
        temp_celsius: float,
        notes: str = None
    ) -> TemperatureSensorLog:
        """
        Records a sensor reading for a storage unit and evaluates temperature thresholds.
        """
        unit = StorageService.get_unit_by_id(storage_unit_id)

        # Check for excursion out of allowed bounds
        is_excursion = False
        if temp_celsius < unit.min_temp_celsius or temp_celsius > unit.max_temp_celsius:
            is_excursion = True

        log = TemperatureSensorLog(
            storage_unit_id=unit.id,
            reading_temp_celsius=temp_celsius,
            is_excursion=is_excursion,
            notes=notes or ("Temperature within range" if not is_excursion else "CRITICAL: Excursion detected!")
        )
        db.session.add(log)

        if is_excursion:
            NotificationService.create_notification(
                title=f"COLD CHAIN BREACH ALERT: {unit.name}",
                message=f"CRITICAL: Storage unit '{unit.name}' registered temperature of {temp_celsius}°C (Allowed range: {unit.min_temp_celsius}°C to {unit.max_temp_celsius}°C). Immediate inspection required!",
                category=NotificationCategory.VALIDATION_FAILURE.value,
                priority=NotificationPriority.CRITICAL.value,
                related_entity_type="StorageUnit",
                related_entity_id=str(unit.id)
            )

        db.session.commit()
        logger.info(f"Recorded Temperature for Unit '{unit.name}': {temp_celsius}°C (Excursion={is_excursion})")
        return log
