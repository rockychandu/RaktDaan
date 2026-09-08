"""
Test Suite for Toxicology - AnabolicSteroids Rule.
"""

from app.enterprise.generated_rules.rule_toxicology_anabolicsteroids import AnabolicSteroidsClinicalRuleProcessor


def test_anabolicsteroids_rule_evaluation():
    processor = AnabolicSteroidsClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_anabolicsteroids": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_TOXICOLOGY_ANABOLICSTEROIDS"

    res_pass = processor.evaluate({"has_anabolicsteroids": False})
    assert res_pass["passed"] is True
