"""
Test Suite for Immunology - AnkylosingSpondylitis Rule.
"""

from app.enterprise.generated_rules.rule_immunology_ankylosingspondylitis import AnkylosingSpondylitisClinicalRuleProcessor


def test_ankylosingspondylitis_rule_evaluation():
    processor = AnkylosingSpondylitisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_ankylosingspondylitis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_IMMUNOLOGY_ANKYLOSINGSPONDYLITIS"

    res_pass = processor.evaluate({"has_ankylosingspondylitis": False})
    assert res_pass["passed"] is True
