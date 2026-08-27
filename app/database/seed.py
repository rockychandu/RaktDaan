import logging
from app.config import Config
from app.database.connection import db
from app.database.models.user import User
from app.database.models.blood_bank import BloodInventory, BloodCompatibilityMatrix
from app.users.models import UserRole, UserStatus, BloodGroup
from app.security.password_policy import PasswordPolicyEngine
from app.database.seed_extended import seed_extended_data
from app.database.seed_enterprise_modules import seed_enterprise_modules_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COMPATIBILITY_MAP = [
    ("O-", "O-"),
    ("O+", "O-"), ("O+", "O+"),
    ("A-", "O-"), ("A-", "A-"),
    ("A+", "O-"), ("A+", "O+"), ("A+", "A-"), ("A+", "A+"),
    ("B-", "O-"), ("B-", "B-"),
    ("B+", "O-"), ("B+", "O+"), ("B+", "B-"), ("B+", "B+"),
    ("AB-", "O-"), ("AB-", "A-"), ("AB-", "B-"), ("AB-", "AB-"),
    ("AB+", "O-"), ("AB+", "O+"), ("AB+", "A-"), ("AB+", "A+"), ("AB+", "B-"), ("AB+", "B+"), ("AB+", "AB-"), ("AB+", "AB+")
]

def seed_initial_admin() -> User:
    """
    Seeds initial system admin accounts if none exist.
    """
    admin_emails = [Config.ADMIN_EMAIL.lower().strip(), "admin@raktdaan.com"]
    
    for email in admin_emails:
        existing_admin = User.query.filter_by(email=email).first()
        if not existing_admin:
            admin_user = User(
                name=Config.ADMIN_NAME,
                email=email,
                password_hash=PasswordPolicyEngine.hash_password(Config.ADMIN_PASSWORD),
                role=UserRole.ADMIN.value,
                phone=Config.ADMIN_PHONE,
                status=UserStatus.ACTIVE.value
            )
            db.session.add(admin_user)
            logger.info(f"Successfully created initial Admin account: {email}")
        else:
            existing_admin.password_hash = PasswordPolicyEngine.hash_password(Config.ADMIN_PASSWORD)
    
    db.session.commit()
    return User.query.filter_by(email="admin@raktdaan.com").first()




def seed_blood_inventory():
    """
    Initializes aggregate inventory rows for all 8 blood groups.
    """
    for bg in BloodGroup.list_values():
        existing = BloodInventory.query.filter_by(blood_group=bg).first()
        if not existing:
            inv = BloodInventory(blood_group=bg, units_available=0, units_reserved=0, units_expired=0)
            db.session.add(inv)
    db.session.commit()


def seed_compatibility_matrix():
    """
    Seeds universal blood compatibility matrix.
    """
    if BloodCompatibilityMatrix.query.first():
        return

    for recipient, donor in COMPATIBILITY_MAP:
        matrix_entry = BloodCompatibilityMatrix(
            recipient_blood_group=recipient,
            compatible_donor_blood_group=donor
        )
        db.session.add(matrix_entry)
    db.session.commit()


def seed_all():
    """
    Executes full database seed pipeline.
    """
    seed_initial_admin()
    seed_blood_inventory()
    seed_compatibility_matrix()
    seed_extended_data()
    seed_enterprise_modules_data()
