"""
RaktDaan Enterprise System Constants & Configuration Enums.
Provides domain constants for Donor Management & Blood Inventory Management.
"""

from enum import Enum


class ComponentType(str, Enum):
    """Supported Blood Component Types."""
    WHOLE_BLOOD = "Whole Blood"
    PACKED_RED_BLOOD_CELLS = "Packed Red Blood Cells (PRBC)"
    FRESH_FROZEN_PLASMA = "Fresh Frozen Plasma (FFP)"
    PLATELET_CONCENTRATE = "Platelet Concentrate"
    CRYOPRECIPITATE = "Cryoprecipitate"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]


# Shelf Life Specifications in Days
COMPONENT_SHELF_LIFE_DAYS = {
    ComponentType.WHOLE_BLOOD.value: 35,
    ComponentType.PACKED_RED_BLOOD_CELLS.value: 42,
    ComponentType.FRESH_FROZEN_PLASMA.value: 365,
    ComponentType.PLATELET_CONCENTRATE.value: 5,
    ComponentType.CRYOPRECIPITATE.value: 365,
}

# Standard Unit Volumes in Milliliters (mL)
COMPONENT_STANDARD_VOLUMES_ML = {
    ComponentType.WHOLE_BLOOD.value: 450,
    ComponentType.PACKED_RED_BLOOD_CELLS.value: 280,
    ComponentType.FRESH_FROZEN_PLASMA.value: 220,
    ComponentType.PLATELET_CONCENTRATE.value: 60,
    ComponentType.CRYOPRECIPITATE.value: 15,
}

# Recommended Storage Temperature Ranges (Min °C, Max °C)
COMPONENT_STORAGE_TEMP_RANGE = {
    ComponentType.WHOLE_BLOOD.value: (2.0, 6.0),
    ComponentType.PACKED_RED_BLOOD_CELLS.value: (2.0, 6.0),
    ComponentType.FRESH_FROZEN_PLASMA.value: (-30.0, -18.0),
    ComponentType.PLATELET_CONCENTRATE.value: (20.0, 24.0),
    ComponentType.CRYOPRECIPITATE.value: (-30.0, -18.0),
}


class BloodBagStatus(str, Enum):
    """Lifecycle status states for Blood Bags."""
    COLLECTED = "COLLECTED"
    PROCESSING = "PROCESSING"
    TESTING = "TESTING"
    QUARANTINED = "QUARANTINED"
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    DISPATCHED = "DISPATCHED"
    EXPIRED = "EXPIRED"
    DISCARDED = "DISCARDED"
    REJECTED = "REJECTED"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]


# Allowed State Transitions for Blood Bags
VALID_BAG_TRANSITIONS = {
    BloodBagStatus.COLLECTED.value: [BloodBagStatus.PROCESSING.value, BloodBagStatus.DISCARDED.value, BloodBagStatus.REJECTED.value],
    BloodBagStatus.PROCESSING.value: [BloodBagStatus.TESTING.value, BloodBagStatus.DISCARDED.value, BloodBagStatus.REJECTED.value],
    BloodBagStatus.TESTING.value: [BloodBagStatus.QUARANTINED.value, BloodBagStatus.AVAILABLE.value, BloodBagStatus.REJECTED.value, BloodBagStatus.DISCARDED.value],
    BloodBagStatus.QUARANTINED.value: [BloodBagStatus.AVAILABLE.value, BloodBagStatus.DISCARDED.value, BloodBagStatus.REJECTED.value],
    BloodBagStatus.AVAILABLE.value: [BloodBagStatus.RESERVED.value, BloodBagStatus.QUARANTINED.value, BloodBagStatus.EXPIRED.value, BloodBagStatus.DISCARDED.value],
    BloodBagStatus.RESERVED.value: [BloodBagStatus.DISPATCHED.value, BloodBagStatus.AVAILABLE.value, BloodBagStatus.EXPIRED.value, BloodBagStatus.DISCARDED.value],
    BloodBagStatus.DISPATCHED.value: [BloodBagStatus.QUARANTINED.value, BloodBagStatus.DISCARDED.value], # Allows recall/return handling
    BloodBagStatus.EXPIRED.value: [BloodBagStatus.DISCARDED.value],
    BloodBagStatus.DISCARDED.value: [],
    BloodBagStatus.REJECTED.value: [],
}


class DonationStatus(str, Enum):
    """Donation Process Workflow States."""
    REGISTERED = "REGISTERED"
    SCREENING = "SCREENING"
    ELIGIBLE = "ELIGIBLE"
    DEFERRED = "DEFERRED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]


class DonationType(str, Enum):
    """Types of Donation Procedures."""
    WHOLE_BLOOD = "Whole Blood"
    POWER_RED = "Power Red (Double RBC)"
    PLATELETPHERESIS = "Plateletpheresis"
    PLASMAPHERESIS = "Plasmapheresis"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]


class DeferralType(str, Enum):
    """Eligibility Deferral Classifications."""
    NONE = "NONE"
    TEMPORARY = "TEMPORARY"
    PERMANENT = "PERMANENT"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]


class StockLevelStatus(str, Enum):
    """Inventory Stock Warning Levels."""
    NORMAL = "NORMAL"
    LOW = "LOW"
    CRITICAL = "CRITICAL"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]


class NotificationPriority(str, Enum):
    """Internal Alert Notification Priorities."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]


class NotificationCategory(str, Enum):
    """Categories of Internal System Notifications."""
    LOW_STOCK = "LOW_STOCK"
    CRITICAL_STOCK = "CRITICAL_STOCK"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED_STOCK = "EXPIRED_STOCK"
    PENDING_TESTING = "PENDING_TESTING"
    QUARANTINE_ALERT = "QUARANTINE_ALERT"
    RESERVATION_EXPIRY = "RESERVATION_EXPIRY"
    RECONCILIATION_DISCREPANCY = "RECONCILIATION_DISCREPANCY"
    VALIDATION_FAILURE = "VALIDATION_FAILURE"
    IMPORTANT_EVENT = "IMPORTANT_EVENT"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]


class TransactionType(str, Enum):
    """Inventory Audit Transaction Types."""
    DONATION = "DONATION"
    STOCK_ADDITION = "STOCK_ADDITION"
    RESERVATION = "RESERVATION"
    RELEASE = "RELEASE"
    DISPATCH = "DISPATCH"
    TRANSFER = "TRANSFER"
    EXPIRY = "EXPIRY"
    DISPOSAL = "DISPOSAL"
    ADJUSTMENT = "ADJUSTMENT"
    RETURN = "RETURN"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]


class StorageType(str, Enum):
    """Storage Unit Hardware Equipment Types."""
    BLOOD_REFRIGERATOR = "Blood Bank Refrigerator"
    DEEP_FREEZER = "Deep Freezer (-30C)"
    ULTRA_LOW_FREEZER = "Ultra-Low Freezer (-80C)"
    PLATELET_AGITATOR = "Platelet Incubator & Agitator"
    ROOM_TEMP_RACK = "Ambient Room Storage"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]


# Default Thresholds by Blood Group (Minimum & Critical Unit Counts)
DEFAULT_STOCK_THRESHOLDS = {
    "A+": {"minimum": 15, "critical": 5},
    "A-": {"minimum": 8, "critical": 3},
    "B+": {"minimum": 15, "critical": 5},
    "B-": {"minimum": 8, "critical": 3},
    "AB+": {"minimum": 10, "critical": 4},
    "AB-": {"minimum": 5, "critical": 2},
    "O+": {"minimum": 20, "critical": 8},
    "O-": {"minimum": 12, "critical": 4},
}

# Configurable Default Expiry Warning Days
DEFAULT_EXPIRY_WARNING_DAYS = 7

# Mandatory Donation Interval Rules (Days)
DONATION_INTERVAL_MALE_DAYS = 56
DONATION_INTERVAL_FEMALE_DAYS = 84

# Universal Compatibility Reference Map
UNIVERSAL_COMPATIBILITY_MAP = {
    "O-": ["O-"],
    "O+": ["O-", "O+"],
    "A-": ["O-", "A-"],
    "A+": ["O-", "O+", "A-", "A+"],
    "B-": ["O-", "B-"],
    "B+": ["O-", "O+", "B-", "B+"],
    "AB-": ["O-", "A-", "B-", "AB-"],
    "AB+": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
}
