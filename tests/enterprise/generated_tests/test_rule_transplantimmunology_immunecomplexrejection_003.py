"""
Automated Test Suite for TransplantImmunology - ImmuneComplexRejection (3) Clinical Rule Processor.
"""

from app.enterprise.generated_rules.rule_transplantimmunology_immunecomplexrejection_003 import TransplantImmunologyImmuneComplexRejectionClinicalProcessor3


def test_transplantimmunology_immunecomplexrejection_3_evaluation():
    processor = TransplantImmunologyImmuneComplexRejectionClinicalProcessor3()
    
    # Test primary fail
    res_fail = processor.evaluate_primary_condition({"has_transplantimmunology_immunecomplexrejection_primary": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ENT_TRANSPLANTIMMUNOLOGY_IMMUNECOMPLEXREJECTION_003"

    # Test primary pass
    res_pass = processor.evaluate_primary_condition({"has_transplantimmunology_immunecomplexrejection_primary": False})
    assert res_pass["passed"] is True

    # Test secondary indicators
    sec_pass = processor.evaluate_secondary_indicators({"transplantimmunology_immunecomplexrejection_lab_marker": 12.5, "is_medicated_transplantimmunology": False})
    assert sec_pass["passed"] is True

    # Test date calculation
    date_res = processor.compute_next_eligible_date("2026-01-01")
    assert "next_eligible_date" in date_res

    # Test audit summary
    audit_msg = processor.generate_audit_summary(res_pass)
    assert "[AUDIT RULE_ENT_" in audit_msg
