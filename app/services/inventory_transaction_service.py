"""
Inventory Transaction Audit Ledger Service Layer (Member 4).
Records every inventory delta with transaction code, bag ID, blood group, type, and user ID.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.database.connection import db
from app.database.models.inventory_extended import InventoryTransaction
from app.schemas.inventory_schemas import InventoryTransactionFilterSchema

logger = logging.getLogger(__name__)


def generate_unique_transaction_code() -> str:
    """
    Generates unique inventory transaction code in format TXN-YYYY-XXXXXX.
    """
    year = datetime.now(timezone.utc).strftime("%Y")
    count = db.session.query(InventoryTransaction).count() + 1
    return f"TXN-{year}-{count:06d}"


class InventoryTransactionService:
    """
    Audit Trail Ledger Service for Inventory Movements.
    """

    @staticmethod
    def record_transaction(
        blood_group: str,
        transaction_type: str,
        reason: str,
        bag_id: Optional[int] = None,
        component_type: str = "Whole Blood",
        quantity_units: int = 1,
        previous_status: Optional[str] = None,
        new_status: Optional[str] = None,
        performed_by_user_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> InventoryTransaction:
        """
        Appends an immutable audit transaction record to the inventory transaction ledger.
        """
        txn_code = generate_unique_transaction_code()

        txn = InventoryTransaction(
            transaction_code=txn_code,
            bag_id=bag_id,
            blood_group=blood_group,
            component_type=component_type,
            quantity_units=quantity_units,
            transaction_type=transaction_type,
            previous_status=previous_status,
            new_status=new_status,
            performed_by_user_id=performed_by_user_id,
            reason=reason,
            notes=notes
        )
        db.session.add(txn)
        db.session.commit()
        logger.info(f"Recorded Inventory Transaction '{txn_code}': Type={transaction_type}, Group={blood_group}")
        return txn

    @staticmethod
    def list_transactions(filter_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Queries and paginates inventory transaction ledger.
        """
        schema = InventoryTransactionFilterSchema(**filter_params)

        query = InventoryTransaction.query.filter_by(is_deleted=False)

        if schema.blood_group:
            query = query.filter(InventoryTransaction.blood_group == schema.blood_group)
        if schema.transaction_type:
            query = query.filter(InventoryTransaction.transaction_type == schema.transaction_type)
        if schema.bag_code:
            query = query.filter(InventoryTransaction.bag_id != None)
        if schema.user_id:
            query = query.filter(InventoryTransaction.performed_by_user_id == schema.user_id)

        query = query.order_by(InventoryTransaction.created_at.desc())
        total = query.count()
        items = query.offset((schema.page - 1) * schema.per_page).limit(schema.per_page).all()

        return {
            "items": [t.to_dict() for t in items],
            "total": total,
            "page": schema.page,
            "per_page": schema.per_page,
            "total_pages": (total + schema.per_page - 1) // schema.per_page
        }
