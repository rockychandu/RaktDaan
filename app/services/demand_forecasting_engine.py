"""
Demand Forecasting & Safety Stock Calculation Engine (Member 4).
Calculates moving average demand for blood units by blood group and component type.
Determines recommended safety stock levels and flags expected shortage risk.
"""

import logging
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List
from sqlalchemy import func

from app.database.connection import db
from app.database.models.blood_bank import BloodInventory
from app.database.models.inventory_extended import BloodDispatch
from app.users.models import BloodGroup

logger = logging.getLogger(__name__)


class DemandForecastingEngine:
    """
    Business Logic Engine for Blood Demand Forecasting & Safety Stock Planning.
    """

    @staticmethod
    def calculate_blood_demand_forecast(days_window: int = 30) -> Dict[str, Any]:
        """
        Calculates moving average daily consumption rate and predicts next 30-day demand.
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_window)

        # Query total units dispatched per blood group over window
        dispatch_sums = db.session.query(
            BloodDispatch.blood_group,
            func.sum(BloodDispatch.quantity_units).label("total_units")
        ).filter(BloodDispatch.dispatch_date >= cutoff_date).group_by(BloodDispatch.blood_group).all()

        dispatch_map = {bg: (units or 0) for bg, units in dispatch_sums}

        forecasts = []
        for bg in BloodGroup.list_values():
            units_30d = dispatch_map.get(bg, 0)
            daily_burn_rate = round(units_30d / days_window, 2)
            predicted_30d_demand = int(daily_burn_rate * 30)
            recommended_safety_stock = int(daily_burn_rate * 7) # 7-day safety buffer

            inv = BloodInventory.query.filter_by(blood_group=bg).first()
            current_available = inv.units_available if inv else 0

            days_of_stock_left = round(current_available / daily_burn_rate, 1) if daily_burn_rate > 0 else 999.0
            shortage_risk = "HIGH" if days_of_stock_left < 3 else ("MEDIUM" if days_of_stock_left < 7 else "LOW")

            forecasts.append({
                "blood_group": bg,
                "current_available": current_available,
                "historical_units_dispatched_30d": units_30d,
                "daily_burn_rate": daily_burn_rate,
                "predicted_next_30d_demand": predicted_30d_demand,
                "recommended_safety_stock": recommended_safety_stock,
                "days_of_stock_left": days_of_stock_left,
                "shortage_risk": shortage_risk
            })

        return {
            "window_days": days_window,
            "forecasted_at": datetime.now(timezone.utc).isoformat(),
            "forecasts": forecasts
        }
