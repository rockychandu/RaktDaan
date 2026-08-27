"""
Automated Test Suite for Nanomedicine - PhysiologicalVitalsThreshold (2) Clinical Rule Processor.
"""

from app.enterprise.generated_rules.rule_nanomedicine_physiologicalvitalsthreshold_002 import NanomedicinePhysiologicalVitalsThresholdClinicalProcessor2


def test_nanomedicine_physiologicalvitalsthreshold_2_evaluation():
    processor = NanomedicinePhysiologicalVitalsThresholdClinicalProcessor2()
    
    # Test primary fail
    res_fail = processor.evaluate_primary_condition({"has_nanomedicine_physiologicalvitalsthreshold_primary": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ENT_NANOMEDICINE_PHYSIOLOGICALVITALSTHRESHOLD_002"

    # Test primary pass
    res_pass = processor.evaluate_primary_condition({"has_nanomedicine_physiologicalvitalsthreshold_primary": False})
    assert res_pass["passed"] is True

    # Test secondary indicators
    sec_pass = processor.evaluate_secondary_indicators({"nanomedicine_physiologicalvitalsthreshold_lab_marker": 12.5, "is_medicated_nanomedicine": False})
    assert sec_pass["passed"] is True

    # Test date calculation
    date_res = processor.compute_next_eligible_date("2026-01-01")
    assert "next_eligible_date" in date_res

    # Test audit summary
    audit_msg = processor.generate_audit_summary(res_pass)
    assert "[AUDIT RULE_ENT_" in audit_msg
