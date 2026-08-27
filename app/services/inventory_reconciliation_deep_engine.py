"""
Deep Physical Inventory Reconciliation & Discrepancy Analyzer Engine (Member 4).
Analyzes physical stock audit counts against active database stock,
calculates variance percentages per blood group, and generates adjustment logs.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.database.connection import db
from app.database.models.blood_bank import BloodInventory, BloodBag
from app.database.models.inventory_extended import StockReconciliation
from app.users.models import BloodGroup

logger = logging.getLogger(__name__)


class InventoryReconciliationDeepEngine:
    """
    Business Logic Engine for Deep Physical Stock Reconciliation.
    """

    @staticmethod
    def analyze_stock_discrepancies() -> Dict[str, Any]:
        """
        Compares actual AVAILABLE blood bag counts in DB with aggregate BloodInventory table records.
        Identifies any out-of-sync inventory counts and returns variance report.
        """
        discrepancies = []
        total_system_units = 0
        total_actual_bags = 0

        for bg in BloodGroup.list_values():
            inv = BloodInventory.query.filter_by(blood_group=bg).first()
            system_count = inv.units_available if inv else 0

            actual_bags_count = BloodBag.query.filter_by(
                blood_group=bg,
                status="AVAILABLE",
                is_deleted=False
            ).count()

            total_system_units += system_count
            total_actual_bags += actual_bags_count

            variance = actual_bags_count - system_count
            if variance != 0:
                discrepancies.append({
                    "blood_group": bg,
                    "system_record_count": system_count,
                    "actual_bags_count": actual_bags_count,
                    "variance": variance,
                    "status": "SURPLUS" if variance > 0 else "DEFICIT"
                })

        is_balanced = len(discrepancies) == 0

        return {
            "audited_at": datetime.now(timezone.utc).isoformat(),
            "is_balanced": is_balanced,
            "total_system_units": total_system_units,
            "total_actual_bags": total_actual_bags,
            "total_discrepancies_count": len(discrepancies),
            "discrepancies": discrepancies
        }

    @staticmethod
    def synchronize_inventory_counts() -> int:
        """
        Automatically reconciles and resynchronizes aggregate BloodInventory table counts
        with actual AVAILABLE BloodBag records in database.
        Returns number of blood group rows updated.
        """
        updated_count = 0
        for bg in BloodGroup.list_values():
            actual_count = BloodBag.query.filter_by(
                blood_group=bg,
                status="AVAILABLE",
                is_deleted=False
            ).count()

            inv = BloodInventory.query.filter_by(blood_group=bg).first()
            if inv:
                if inv.units_available != actual_count:
                    inv.units_available = actual_count
                    inv.last_updated = datetime.now(timezone.utc)
                    updated_count += 1
            else:
                inv = BloodInventory(blood_group=bg, units_available=actual_count)
                db.session.add(inv)
                updated_count += 1

        db.session.commit()
        logger.info(f"Synchronized Inventory Counts: Updated {updated_count} blood group records.")
        return updated_count
