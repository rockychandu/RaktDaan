"""
Test Suite for Endocrinology - CushingsSyndrome Rule.
"""

from app.enterprise.generated_rules.rule_endocrinology_cushingssyndrome import CushingsSyndromeClinicalRuleProcessor


def test_cushingssyndrome_rule_evaluation():
    processor = CushingsSyndromeClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_cushingssyndrome": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_ENDOCRINOLOGY_CUSHINGSSYNDROME"

    res_pass = processor.evaluate({"has_cushingssyndrome": False})
    assert res_pass["passed"] is True
