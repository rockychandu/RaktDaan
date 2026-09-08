"""
Test Suite for Toxicology - NicotineDependence Rule.
"""

from app.enterprise.generated_rules.rule_toxicology_nicotinedependence import NicotineDependenceClinicalRuleProcessor


def test_nicotinedependence_rule_evaluation():
    processor = NicotineDependenceClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_nicotinedependence": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_TOXICOLOGY_NICOTINEDEPENDENCE"

    res_pass = processor.evaluate({"has_nicotinedependence": False})
    assert res_pass["passed"] is True
