"""
Automated Unit Tests for Deep Predictive Analytics & Supply Depletion Simulations.
"""

from app.services.analytics.deep_predictive_engine import DeepPredictiveAnalyticsEngine
from app.services.analytics.seasonal_forecasting_engine import SeasonalBloodDemandForecastingEngine
from app.services.analytics.donor_churn_predictor import DonorChurnPredictorEngine


def test_donor_lifetime_value_score():
    res = DeepPredictiveAnalyticsEngine.calculate_donor_lifetime_value_index(
        total_donations=12,
        first_donation_year=2020
    )
    assert res["donor_value_score"] > 0
    assert res["hero_badge_eligible"] is True


def test_supply_depletion_simulation():
    res = DeepPredictiveAnalyticsEngine.simulate_supply_depletion_curve(
        initial_units=100,
        daily_outflow_rate=10.0,
        daily_inflow_rate=5.0,
        simulation_days=30
    )
    assert res["stockout_projected"] is True
    assert res["stockout_day"] == 20


def test_seasonal_forecasting():
    res = SeasonalBloodDemandForecastingEngine.forecast_blood_group_demand(
        blood_group="O-",
        current_stock_units=20,
        average_daily_consumption=3.0,
        target_forecast_days=30
    )
    assert "projected_deficit_units" in res
    assert "risk_level" in res


def test_donor_churn_predictor():
    res = DonorChurnPredictorEngine.predict_donor_lapsing_risk(
        months_since_last_donation=14.0,
        total_lifetime_donations=2,
        deferral_count=1
    )
    assert "churn_probability_pct" in res
    assert res["churn_risk_level"] in ["LOW", "MEDIUM", "HIGH"]
