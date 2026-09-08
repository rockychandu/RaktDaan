"""
Test Suite for Immunology - SjogrensSyndrome Rule.
"""

from app.enterprise.generated_rules.rule_immunology_sjogrenssyndrome import SjogrensSyndromeClinicalRuleProcessor


def test_sjogrenssyndrome_rule_evaluation():
    processor = SjogrensSyndromeClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_sjogrenssyndrome": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_IMMUNOLOGY_SJOGRENSSYNDROME"

    res_pass = processor.evaluate({"has_sjogrenssyndrome": False})
    assert res_pass["passed"] is True
