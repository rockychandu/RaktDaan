"""
Test Suite for Oncology - PancreaticCancer Rule.
"""

from app.enterprise.generated_rules.rule_oncology_pancreaticcancer import PancreaticCancerClinicalRuleProcessor


def test_pancreaticcancer_rule_evaluation():
    processor = PancreaticCancerClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_pancreaticcancer": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ONCOLOGY_PANCREATICCANCER"

    res_pass = processor.evaluate({"has_pancreaticcancer": False})
    assert res_pass["passed"] is True
