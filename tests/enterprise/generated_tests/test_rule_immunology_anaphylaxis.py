"""
Test Suite for Immunology - Anaphylaxis Rule.
"""

from app.enterprise.generated_rules.rule_immunology_anaphylaxis import AnaphylaxisClinicalRuleProcessor


def test_anaphylaxis_rule_evaluation():
    processor = AnaphylaxisClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_anaphylaxis": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_IMMUNOLOGY_ANAPHYLAXIS"

    res_pass = processor.evaluate({"has_anaphylaxis": False})
    assert res_pass["passed"] is True
