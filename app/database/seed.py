import logging
from app.config import Config
from app.database.connection import db
from app.database.models import User
from app.users.models import UserRole, UserStatus
from app.utils.security import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_initial_admin() -> User:
    """
    Seeds initial system admin account if none exists.
    Admin registration is NOT exposed via public registration API.
    """
    admin_email = Config.ADMIN_EMAIL.lower().strip()
    existing_admin = User.query.filter_by(email=admin_email).first()
    
    if existing_admin:
        logger.info(f"Admin user already exists: {admin_email}")
        return existing_admin

    admin_user = User(
        name=Config.ADMIN_NAME,
        email=admin_email,
        password_hash=hash_password(Config.ADMIN_PASSWORD),
        role=UserRole.ADMIN.value,
        phone=Config.ADMIN_PHONE,
        status=UserStatus.ACTIVE.value
    )
    db.session.add(admin_user)
    db.session.commit()
    logger.info(f"Successfully created initial Admin account: {admin_email}")
    return admin_user
