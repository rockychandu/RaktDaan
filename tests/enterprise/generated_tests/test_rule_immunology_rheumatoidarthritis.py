"""
Test Suite for Immunology - RheumatoidArthritis Rule.
"""

from app.enterprise.generated_rules.rule_immunology_rheumatoidarthritis import RheumatoidArthritisClinicalRuleProcessor


def test_rheumatoidarthritis_rule_evaluation():
    processor = RheumatoidArthritisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_rheumatoidarthritis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_IMMUNOLOGY_RHEUMATOIDARTHRITIS"

    res_pass = processor.evaluate({"has_rheumatoidarthritis": False})
    assert res_pass["passed"] is True
