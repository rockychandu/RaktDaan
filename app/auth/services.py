from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.database.models import User, DonorProfile
from app.users.models import UserRole, UserStatus
from app.utils.security import hash_password, verify_password, create_access_token
from app.auth.validators import DonorRegisterRequest, LoginRequest

def register_donor_service(db: Session, req: DonorRegisterRequest) -> User:
    """
    Service to register a new donor with unique email validation and password hashing.
    """
    # 1. Check for duplicate email
    existing_user = db.query(User).filter(User.email == req.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered. Please login or use a different email."
        )

    # 2. Hash password securely
    hashed_pwd = hash_password(req.password)

    # 3. Create User record
    new_user = User(
        name=req.name,
        email=req.email.lower(),
        password_hash=hashed_pwd,
        role=UserRole.DONOR.value,
        phone=req.phone,
        status=UserStatus.ACTIVE.value
    )
    db.add(new_user)
    db.flush() # Populate new_user.id before committing

    # 4. Create DonorProfile record
    new_profile = DonorProfile(
        user_id=new_user.id,
        date_of_birth=req.date_of_birth,
        gender=req.gender,
        blood_group=req.blood_group,
        address=req.address,
        city=req.city,
        state=req.state,
        emergency_contact=req.emergency_contact
    )
    db.add(new_profile)

    # 5. Commit transaction
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user_service(db: Session, login_data: LoginRequest, expected_role: str) -> User:
    """
    Authenticates user credentials and enforces strict role verification.
    Generic failure messages are returned for security.
    """
    email_clean = login_data.email.strip().lower()
    user = db.query(User).filter(User.email == email_clean).first()

    # Generic error message to prevent user enumeration attacks
    generic_auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        raise generic_auth_error

    if not verify_password(login_data.password, user.password_hash):
        raise generic_auth_error

    if user.status != UserStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Please contact system administrator."
        )

    # Verify role match (Donor attempting Admin login or vice versa)
    if user.role != expected_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unauthorized access. Account is not registered as {expected_role.lower()}.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
