"""
Test Suite for Immunology - PsoriaticArthritis Rule.
"""

from app.enterprise.generated_rules.rule_immunology_psoriaticarthritis import PsoriaticArthritisClinicalRuleProcessor


def test_psoriaticarthritis_rule_evaluation():
    processor = PsoriaticArthritisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_psoriaticarthritis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_IMMUNOLOGY_PSORIATICARTHRITIS"

    res_pass = processor.evaluate({"has_psoriaticarthritis": False})
    assert res_pass["passed"] is True
