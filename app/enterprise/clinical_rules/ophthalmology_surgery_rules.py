"""
Ophthalmology & Ocular Surgery Clinical Screening Rules.
Evaluates corneal transplants, intraocular injections, and laser refractive procedures.
"""

from typing import Dict, Any


class CornealGraftRule:
    """Evaluates human donor cornea transplants (vCJD prion transmission risk)."""
    rule_code = "RULE_OPHTHAL_CORNEA"
    rule_name = "Corneal Graft Prion Deferral Rule"
    category = "OPHTHALMOLOGY"

    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        has_corneal_graft = data.get("has_corneal_transplant", False)

        if has_corneal_graft:
            return {
                "passed": False,
                "rule_code": self.rule_code,
                "reason": "History of human corneal tissue transplant declared (vCJD prion risk). Permanent deferral.",
                "deferral_days": 36500
            }

        return {
            "passed": True,
            "rule_code": self.rule_code,
            "reason": "No corneal tissue graft reported.",
            "deferral_days": 0
        }
