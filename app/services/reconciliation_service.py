"""
Physical Stock Audit & Inventory Reconciliation Service Layer (Member 4).
Compares system inventory with physical shelf counts, logs variance ledgers, and applies authorized stock adjustments.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.database.connection import db
from app.database.models.blood_bank import BloodInventory
from app.database.models.inventory_extended import StockReconciliation
from app.common.constants import TransactionType, NotificationCategory, NotificationPriority
from app.services.inventory_service import InventoryService
from app.services.inventory_transaction_service import InventoryTransactionService
from app.services.notification_service import NotificationService
from app.schemas.reconciliation_schemas import StockReconciliationSubmitSchema

logger = logging.getLogger(__name__)


def generate_unique_reconciliation_code() -> str:
    """
    Generates unique stock reconciliation code in format REC-YYYY-XXXXXX.
    """
    year = datetime.now(timezone.utc).strftime("%Y")
    count = db.session.query(StockReconciliation).count() + 1
    return f"REC-{year}-{count:06d}"


class ReconciliationService:
    """
    Business Logic Layer for Physical Inventory Reconciliation Audits.
    """

    @staticmethod
    def execute_stock_reconciliation(data_dict: Dict[str, Any], user_id: int) -> List[Dict[str, Any]]:
        """
        Executes physical inventory reconciliation audit against database system count.
        """
        schema = StockReconciliationSubmitSchema(**data_dict)
        results = []

        for item in schema.items:
            # Sync system count first
            inv = InventoryService.recalculate_aggregate_inventory_for_blood_group(item.blood_group)
            system_count = inv.units_available
            physical_count = item.physical_count
            variance = physical_count - system_count

            rec_code = generate_unique_reconciliation_code()

            rec = StockReconciliation(
                reconciliation_code=rec_code,
                blood_group=item.blood_group,
                component_type=item.component_type,
                system_count=system_count,
                physical_count=physical_count,
                variance_count=variance,
                audit_reason=schema.audit_reason,
                audited_by_user_id=user_id
            )
            db.session.add(rec)

            # Record Inventory Transaction Ledger
            InventoryTransactionService.record_transaction(
                blood_group=item.blood_group,
                component_type=item.component_type,
                quantity_units=abs(variance),
                transaction_type=TransactionType.ADJUSTMENT.value,
                reason=f"Physical Stock Reconciliation ({rec_code}): {schema.audit_reason}",
                performed_by_user_id=user_id,
                notes=f"System Count: {system_count}, Physical Count: {physical_count}, Variance: {variance}"
            )

            # Fire Alert if Discrepancy Found
            if variance != 0:
                NotificationService.create_notification(
                    title=f"Stock Reconciliation Discrepancy ({item.blood_group})",
                    message=f"Reconciliation {rec_code} found a variance of {variance} units for {item.blood_group}. System: {system_count}, Physical: {physical_count}.",
                    category=NotificationCategory.RECONCILIATION_DISCREPANCY.value,
                    priority=NotificationPriority.HIGH.value,
                    related_entity_type="StockReconciliation",
                    related_entity_id=rec_code
                )

            results.append(rec.to_dict())

        db.session.commit()
        logger.info(f"Executed Stock Reconciliation Audit across {len(schema.items)} blood group entries.")
        return results
