"""
Test Suite for Oncology - OvarianCancer Rule.
"""

from app.enterprise.generated_rules.rule_oncology_ovariancancer import OvarianCancerClinicalRuleProcessor


def test_ovariancancer_rule_evaluation():
    processor = OvarianCancerClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_ovariancancer": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ONCOLOGY_OVARIANCANCER"

    res_pass = processor.evaluate({"has_ovariancancer": False})
    assert res_pass["passed"] is True
