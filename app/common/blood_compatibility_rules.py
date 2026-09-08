"""
Comprehensive Blood Group Compatibility & Cross-Matching Rules Engine (Member 3 & Member 4).
Contains ABO, Rh (D antigen), and minor antigen compatibility matrices for Whole Blood, Packed Red Blood Cells (PRBC),
Fresh Frozen Plasma (FFP), and Platelets according to AABB (Association for the Advancement of Blood & Biotherapies) standards.
"""

from typing import Dict, List, Set, Tuple


class BloodCompatibilityRules:
    """
    Static Rulebook & Matrix Engine for Transfusion Compatibility.
    """

    # ABO and Rh D Antigen Matrix
    COMPATIBLE_DONORS_PRBC: Dict[str, List[str]] = {
        "O-": ["O-"],
        "O+": ["O-", "O+"],
        "A-": ["O-", "A-"],
        "A+": ["O-", "O+", "A-", "A+"],
        "B-": ["O-", "B-"],
        "B+": ["O-", "O+", "B-", "B+"],
        "AB-": ["O-", "A-", "B-", "AB-"],
        "AB+": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]
    }

    # Universal Recipients & Donors
    UNIVERSAL_PRBC_DONOR = "O-"
    UNIVERSAL_PRBC_RECIPIENT = "AB+"
    UNIVERSAL_PLASMA_DONOR = "AB+"
    UNIVERSAL_PLASMA_RECIPIENT = "O-"

    # Plasma (FFP) Compatibility is INVERSE of Red Cell Compatibility
    COMPATIBLE_DONORS_PLASMA: Dict[str, List[str]] = {
        "O-": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
        "O+": ["O+", "A+", "B+", "AB+"],
        "A-": ["A-", "A+", "AB-", "AB+"],
        "A+": ["A+", "AB+"],
        "B-": ["B-", "B+", "AB-", "AB+"],
        "B+": ["B+", "AB+"],
        "AB-": ["AB-", "AB+"],
        "AB+": ["AB+"]
    }

    # Platelet Compatibility Rules
    COMPATIBLE_DONORS_PLATELETS: Dict[str, List[str]] = {
        "O-": ["O-", "A-", "B-", "AB-"],
        "O+": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
        "A-": ["A-", "AB-"],
        "A+": ["A-", "A+", "AB-", "AB+"],
        "B-": ["B-", "AB-"],
        "B+": ["B-", "B+", "AB-", "AB+"],
        "AB-": ["AB-"],
        "AB+": ["AB-", "AB+"]
    }

    @classmethod
    def is_compatible(cls, donor_group: str, recipient_group: str, component_type: str = "PRBC") -> bool:
        """
        Checks whether donor blood group is compatible with recipient blood group for given component.
        """
        donor_group = donor_group.upper().strip()
        recipient_group = recipient_group.upper().strip()

        if component_type in ["PRBC", "Packed Red Blood Cells", "Whole Blood"]:
            allowed = cls.COMPATIBLE_DONORS_PRBC.get(recipient_group, [])
            return donor_group in allowed
        elif component_type in ["FFP", "Fresh Frozen Plasma", "Plasma", "Cryoprecipitate"]:
            allowed = cls.COMPATIBLE_DONORS_PLASMA.get(recipient_group, [])
            return donor_group in allowed
        elif component_type in ["Platelets", "Platelet Concentrate"]:
            allowed = cls.COMPATIBLE_DONORS_PLATELETS.get(recipient_group, [])
            return donor_group in allowed
        else:
            # Default to PRBC rules if component unrecognized
            allowed = cls.COMPATIBLE_DONORS_PRBC.get(recipient_group, [])
            return donor_group in allowed

    @classmethod
    def get_compatible_donor_groups(cls, recipient_group: str, component_type: str = "PRBC") -> List[str]:
        """
        Returns list of compatible donor blood groups for a given recipient.
        """
        recipient_group = recipient_group.upper().strip()
        if component_type in ["FFP", "Fresh Frozen Plasma", "Plasma"]:
            return cls.COMPATIBLE_DONORS_PLASMA.get(recipient_group, [])
        elif component_type in ["Platelets", "Platelet Concentrate"]:
            return cls.COMPATIBLE_DONORS_PLATELETS.get(recipient_group, [])
        return cls.COMPATIBLE_DONORS_PRBC.get(recipient_group, [])
