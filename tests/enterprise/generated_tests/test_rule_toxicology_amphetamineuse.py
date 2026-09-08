"""
Test Suite for Toxicology - AmphetamineUse Rule.
"""

from app.enterprise.generated_rules.rule_toxicology_amphetamineuse import AmphetamineUseClinicalRuleProcessor


def test_amphetamineuse_rule_evaluation():
    processor = AmphetamineUseClinicalRuleProcessor()
    res_fail = processor.evaluate({"has_amphetamineuse": True})
    assert res_fail["passed"] is False
    assert res_fail["rule_code"] == "RULE_TOXICOLOGY_AMPHETAMINEUSE"

    res_pass = processor.evaluate({"has_amphetamineuse": False})
    assert res_pass["passed"] is True
