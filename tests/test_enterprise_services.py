"""
Automated Test Suite for Clinical Lab Serology, FEFO Allocation, Logistics, and Predictive Analytics.
"""

from app.database.models.blood_bank import BloodBag
from app.services.clinical_lab_testing_engine import ClinicalLabTestingEngine
from app.services.inventory_fefo_allocation_engine import InventoryFEFOAllocationEngine
from app.services.logistics_dispatch_engine import LogisticsDispatchEngine
from app.services.donor_predictive_analytics import DonorPredictiveAnalyticsEngine
from app.services.compliance_audit_reporting_engine import ComplianceAuditReportingEngine
from app.services.hospital_transfusion_service import HospitalTransfusionService


def test_serology_panel_reactive_quarantine(app):
    with app.app_context():
        bag = BloodBag.query.first()
        res = ClinicalLabTestingEngine.process_complete_serology_panel(
            bag_id=bag.id,
            hiv_result="POSITIVE", # Reactive!
            hbv_result="NEGATIVE",
            hcv_result="NEGATIVE",
            syphilis_result="NEGATIVE",
            malaria_result="NEGATIVE"
        )
        assert res["overall_result"] == "REACTIVE"
        assert res["quality_status"] == "FAILED_SEROLOGY"


def test_fefo_allocation(app):
    with app.app_context():
        res = InventoryFEFOAllocationEngine.allocate_fefo_bags(
            required_blood_group="A+",
            required_units=1,
            hospital_id="City Memorial Hospital"
        )
        assert res["allocated"] is True
        assert len(res["allocated_bags"]) == 1


def test_logistics_thermal_modeling():
    res = LogisticsDispatchEngine.calculate_ice_pack_thermal_endurance(
        ambient_temp_celsius=32.0,
        ice_pack_mass_kg=2.5
    )
    assert res["estimated_cooling_endurance_hours"] > 0
    assert res["excursion_risk"] in ["LOW", "MEDIUM", "HIGH"]


def test_predictive_bp_analytics():
    res1 = DonorPredictiveAnalyticsEngine.classify_acc_aha_blood_pressure(118, 76)
    assert res1["stage"] == "NORMAL"

    res2 = DonorPredictiveAnalyticsEngine.classify_acc_aha_blood_pressure(145, 92)
    assert res2["stage"] == "STAGE_2_HYPERTENSION"


def test_compliance_cold_chain_audit(app):
    with app.app_context():
        audit = ComplianceAuditReportingEngine.audit_cold_chain_sla_compliance()
        assert "is_audit_compliant" in audit
        assert "total_storage_units" in audit
