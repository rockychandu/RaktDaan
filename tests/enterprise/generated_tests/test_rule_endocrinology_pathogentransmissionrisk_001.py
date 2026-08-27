"""
Automated Test Suite for Endocrinology - PathogenTransmissionRisk (1) Clinical Rule Processor.
"""

from app.enterprise.generated_rules.rule_endocrinology_pathogentransmissionrisk_001 import EndocrinologyPathogenTransmissionRiskClinicalProcessor1


def test_endocrinology_pathogentransmissionrisk_1_evaluation():
    processor = EndocrinologyPathogenTransmissionRiskClinicalProcessor1()
    
    # Test primary fail
    res_fail = processor.evaluate_primary_condition({"has_endocrinology_pathogentransmissionrisk_primary": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ENT_ENDOCRINOLOGY_PATHOGENTRANSMISSIONRISK_001"

    # Test primary pass
    res_pass = processor.evaluate_primary_condition({"has_endocrinology_pathogentransmissionrisk_primary": False})
    assert res_pass["passed"] is True

    # Test secondary indicators
    sec_pass = processor.evaluate_secondary_indicators({"endocrinology_pathogentransmissionrisk_lab_marker": 12.5, "is_medicated_endocrinology": False})
    assert sec_pass["passed"] is True

    # Test date calculation
    date_res = processor.compute_next_eligible_date("2026-01-01")
    assert "next_eligible_date" in date_res

    # Test audit summary
    audit_msg = processor.generate_audit_summary(res_pass)
    assert "[AUDIT RULE_ENT_" in audit_msg
