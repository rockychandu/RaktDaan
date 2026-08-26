import logging
from sqlalchemy.orm import Session
from app.config import settings
from app.database.connection import SessionLocal, init_db
from app.database.models import User
from app.users.models import UserRole, UserStatus
from app.utils.security import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_initial_admin(db: Session) -> User:
    """
    Seeds initial system admin account if none exists.
    Admin registration is NOT exposed via public registration API.
    """
    admin_email = settings.ADMIN_EMAIL.lower().strip()
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    
    if existing_admin:
        logger.info(f"Admin user already exists: {admin_email}")
        return existing_admin

    admin_user = User(
        name=settings.ADMIN_NAME,
        email=admin_email,
        password_hash=hash_password(settings.ADMIN_PASSWORD),
        role=UserRole.ADMIN.value,
        phone=settings.ADMIN_PHONE,
        status=UserStatus.ACTIVE.value
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    logger.info(f"Successfully created initial Admin account: {admin_email}")
    return admin_user

def run_seed():
    """
    Initializes tables and seeds default data.
    Can be executed via CLI or application startup.
    """
    init_db()
    db = SessionLocal()
    try:
        seed_initial_admin(db)
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
