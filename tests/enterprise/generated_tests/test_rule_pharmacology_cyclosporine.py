"""
Test Suite for Pharmacology - Cyclosporine Rule.
"""

from app.enterprise.generated_rules.rule_pharmacology_cyclosporine import CyclosporineClinicalRuleProcessor


def test_cyclosporine_rule_evaluation():
    processor = CyclosporineClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_cyclosporine": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_PHARMACOLOGY_CYCLOSPORINE"

    res_pass = processor.evaluate({"has_cyclosporine": False})
    assert res_pass["passed"] is True
