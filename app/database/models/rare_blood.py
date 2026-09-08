"""
Rare Blood Registry & Cryogenic Storage Models (Member 3 & Member 4).
Tracks rare blood phenotype donors (Bombay Oh, Rh-null, Para-Bombay, Vel-neg, Duffy-null)
and liquid nitrogen cryogenic frozen red cell bag archives (-80°C / -196°C).
"""

from datetime import datetime, timezone
from app.database.connection import db
from app.database.base import BaseModelMixin


class RareDonorRegistry(db.Model, BaseModelMixin):
    """
    National / Regional Rare Blood Group Donor Registry.
    """
    __tablename__ = "rare_donor_registries"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("donor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    rare_phenotype_code = db.Column(db.String(50), nullable=False, index=True) # BOMBAY_OH, RH_NULL, PARA_BOMBAY, VEL_NEGATIVE, DUFFY_NULL, KELL_NULL
    rarity_classification = db.Column(db.String(30), nullable=False, default="EXTREMELY_RARE") # RARE, VERY_RARE, EXTREMELY_RARE
    antigen_profile_summary = db.Column(db.String(255), nullable=False)
    is_available_for_emergency = db.Column(db.Boolean, default=True, nullable=False)
    registered_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "donor_id": self.donor_id,
            "rare_phenotype_code": self.rare_phenotype_code,
            "rarity_classification": self.rarity_classification,
            "antigen_profile_summary": self.antigen_profile_summary,
            "is_available_for_emergency": self.is_available_for_emergency,
            "registered_by_user_id": self.registered_by_user_id,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class CryoFrozenBagArchive(db.Model, BaseModelMixin):
    """
    Cryopreserved Red Blood Cell Bag Storage (Glycerolized -80°C / Liquid Nitrogen).
    Shelf life up to 10 YEARS.
    """
    __tablename__ = "cryo_frozen_bag_archives"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    archive_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    bag_id = db.Column(db.Integer, db.ForeignKey("blood_bags.id"), nullable=False)
    glycerol_concentration_percent = db.Column(db.Float, nullable=False, default=40.0) # 40% High Glycerol Protocol
    freezing_temp_celsius = db.Column(db.Float, nullable=False, default=-80.0)
    tank_number = db.Column(db.String(50), nullable=False, default="TANK-LN2-01")
    canister_position = db.Column(db.String(50), nullable=False, default="Rack-1 / Box-A")
    frozen_date = db.Column(db.Date, nullable=False)
    max_expiry_date = db.Column(db.Date, nullable=False) # 10 Years from collection
    thawing_status = db.Column(db.String(30), nullable=False, default="FROZEN") # FROZEN, THAWING, DEGLYCEROLIZED, TRANSFUSED, DISCARDED
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "archive_code": self.archive_code,
            "bag_id": self.bag_id,
            "glycerol_concentration_percent": self.glycerol_concentration_percent,
            "freezing_temp_celsius": self.freezing_temp_celsius,
            "tank_number": self.tank_number,
            "canister_position": self.canister_position,
            "frozen_date": self.frozen_date.isoformat() if self.frozen_date else None,
            "max_expiry_date": self.max_expiry_date.isoformat() if self.max_expiry_date else None,
            "thawing_status": self.thawing_status,
            "notes": self.notes
        }
