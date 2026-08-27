"""
Test Suite for Immunology - SevereCombinedImmunodeficiency Rule.
"""

from app.enterprise.generated_rules.rule_immunology_severecombinedimmunodeficiency import SevereCombinedImmunodeficiencyClinicalRuleProcessor


def test_severecombinedimmunodeficiency_rule_evaluation():
    processor = SevereCombinedImmunodeficiencyClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_severecombinedimmunodeficiency": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_IMMUNOLOGY_SEVERECOMBINEDIMMUNODEFICIENCY"

    res_pass = processor.evaluate({"has_severecombinedimmunodeficiency": False})
    assert res_pass["passed"] is True
