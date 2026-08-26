from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.users.models import UserRole
from app.utils.security import create_access_token
from app.auth.validators import (
    DonorRegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse
)
from app.auth.services import register_donor_service, authenticate_user_service
from app.auth.dependencies import get_current_user, require_login, require_donor, require_admin

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & Authorization"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_donor(req: DonorRegisterRequest, db: Session = Depends(get_db)):
    """
    Public Donor Registration Endpoint.
    Validates input fields, checks email uniqueness, hashes password, and creates donor profile.
    """
    user = register_donor_service(db, req)
    return user


@router.post("/donor/login", response_model=TokenResponse)
def donor_login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Donor Login Endpoint.
    Verifies credentials and ensures account has DONOR role before generating token.
    """
    user = authenticate_user_service(db, req, expected_role=UserRole.DONOR.value)
    
    # Create JWT token with user id, role, and email
    token_data = {
        "sub": str(user.id),
        "role": user.role,
        "email": user.email
    }
    access_token = create_access_token(data=token_data)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user=user
    )


@router.post("/admin/login", response_model=TokenResponse)
def admin_login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Admin Login Endpoint.
    Verifies credentials and ensures account has ADMIN role.
    Rejects normal donor accounts attempting admin login.
    """
    user = authenticate_user_service(db, req, expected_role=UserRole.ADMIN.value)

    token_data = {
        "sub": str(user.id),
        "role": user.role,
        "email": user.email
    }
    access_token = create_access_token(data=token_data)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user=user
    )


@router.post("/logout")
def logout(current_user: User = Depends(require_login)):
    """
    Logout Endpoint.
    Informs client to discard session/token.
    """
    return {
        "success": True,
        "message": f"Successfully logged out user {current_user.email}."
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(require_login)):
    """
    Get current logged in user profile (Donor or Admin).
    Requires valid authentication token. Excludes sensitive password_hash.
    """
    return current_user


# Sample Protected Test Routes for Team Integration & Verification

@router.get("/donor/dashboard-data")
def donor_dashboard_sample(current_user: User = Depends(require_donor)):
    """
    Protected Donor-only route test. Returns donor details.
    """
    return {
        "message": f"Welcome to Donor Dashboard, {current_user.name}!",
        "donor_id": current_user.donor_profile.id if current_user.donor_profile else None,
        "blood_group": current_user.donor_profile.blood_group if current_user.donor_profile else None
    }


@router.get("/admin/dashboard-data")
def admin_dashboard_sample(current_user: User = Depends(require_admin)):
    """
    Protected Admin-only route test. Returns admin details.
    """
    return {
        "message": f"Welcome to Admin Dashboard, {current_user.name}!",
        "admin_email": current_user.email
    }
