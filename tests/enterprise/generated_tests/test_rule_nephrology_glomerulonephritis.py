"""
Test Suite for Nephrology - Glomerulonephritis Rule.
"""

from app.enterprise.generated_rules.rule_nephrology_glomerulonephritis import GlomerulonephritisClinicalRuleProcessor


def test_glomerulonephritis_rule_evaluation():
    processor = GlomerulonephritisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_glomerulonephritis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_NEPHROLOGY_GLOMERULONEPHRITIS"

    res_pass = processor.evaluate({"has_glomerulonephritis": False})
    assert res_pass["passed"] is True
