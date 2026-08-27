"""
Donor Management Core Service Layer (Member 3).
Handles donor registration, profile management, unique donor code generation (DNR-2026-XXXXXX),
duplicate detection, search, filter, pagination, soft-delete, and restoration.
"""

import logging
from datetime import datetime, date, timezone
from typing import Dict, Any, Tuple, List, Optional
from sqlalchemy import or_, and_, desc, asc

from app.database.connection import db
from app.database.models.user import User
from app.database.models.donor import DonorProfile, DonorMedicalHistory, DonorEmergencyContact, DonorPreference
from app.users.models import UserRole, UserStatus, EligibilityStatus
from app.security.password_policy import PasswordPolicyEngine
from app.common.exceptions import (
    DonorNotFoundException, DuplicateDonorException, InvalidBloodGroupException
)
from app.schemas.donor_schemas import DonorRegistrationSchema, DonorUpdateSchema, DonorSearchFilterSchema

logger = logging.getLogger(__name__)


def generate_unique_donor_code() -> str:
    """
    Generates a unique production donor code in format DNR-YYYY-XXXXXX.
    """
    year = datetime.now(timezone.utc).strftime("%Y")
    count = db.session.query(DonorProfile).count() + 1
    return f"DNR-{year}-{count:06d}"


class DonorService:
    """
    Comprehensive Business Logic Layer for Donor Management.
    """

    @staticmethod
    def register_donor(data_dict: Dict[str, Any]) -> Tuple[User, DonorProfile]:
        """
        Registers a new voluntary blood donor.
        Performs validation, email/phone duplicate checks, user creation, and donor profile creation.
        """
        schema = DonorRegistrationSchema(**data_dict)

        # Duplicate email check
        email_clean = schema.email.lower().strip()
        existing_user = User.query.filter_by(email=email_clean, is_deleted=False).first()
        if existing_user:
            raise DuplicateDonorException("email", email_clean)

        # Duplicate phone check
        existing_phone = User.query.filter_by(phone=schema.phone, is_deleted=False).first()
        if existing_phone:
            raise DuplicateDonorException("phone", schema.phone)

        # Create User Entity
        hashed_password = PasswordPolicyEngine.hash_password(schema.password)
        user = User(
            name=schema.name,
            email=email_clean,
            password_hash=hashed_password,
            role=UserRole.DONOR.value,
            phone=schema.phone,
            status=UserStatus.ACTIVE.value
        )
        db.session.add(user)
        db.session.flush()

        # Create DonorProfile Entity
        donor_profile = DonorProfile(
            user_id=user.id,
            date_of_birth=schema.date_of_birth,
            gender=schema.gender,
            blood_group=schema.blood_group,
            address=schema.address,
            city=schema.city,
            state=schema.state,
            emergency_contact=schema.emergency_contact,
            eligibility_status=EligibilityStatus.ELIGIBLE.value
        )
        db.session.add(donor_profile)
        db.session.flush()

        # Create Default Preferences
        default_pref = DonorPreference(
            donor_profile_id=donor_profile.id,
            allow_emergency_sms=True,
            allow_email_notifications=True
        )
        db.session.add(default_pref)

        db.session.commit()
        logger.info(f"Successfully registered Donor ID: {donor_profile.id}, User Email: {user.email}")
        return user, donor_profile

    @staticmethod
    def get_donor_by_id(donor_id: int) -> DonorProfile:
        """
        Retrieves a donor by DonorProfile ID.
        """
        donor = DonorProfile.query.filter_by(id=donor_id, is_deleted=False).first()
        if not donor:
            raise DonorNotFoundException(donor_id)
        return donor

    @staticmethod
    def get_donor_by_user_id(user_id: int) -> DonorProfile:
        """
        Retrieves a donor profile by User ID.
        """
        donor = DonorProfile.query.filter_by(user_id=user_id, is_deleted=False).first()
        if not donor:
            raise DonorNotFoundException(f"User ID {user_id}")
        return donor

    @staticmethod
    def update_donor_profile(donor_id: int, update_data: Dict[str, Any]) -> DonorProfile:
        """
        Updates donor profile details.
        """
        donor = DonorService.get_donor_by_id(donor_id)
        user = donor.user

        schema = DonorUpdateSchema(**update_data)

        if schema.name:
            user.name = schema.name
        if schema.phone:
            # Check phone duplicate
            existing_phone = User.query.filter(User.phone == schema.phone, User.id != user.id, User.is_deleted == False).first()
            if existing_phone:
                raise DuplicateDonorException("phone", schema.phone)
            user.phone = schema.phone

        if schema.address:
            donor.address = schema.address
        if schema.city:
            donor.city = schema.city
        if schema.state:
            donor.state = schema.state
        if schema.emergency_contact:
            donor.emergency_contact = schema.emergency_contact
        if schema.blood_group:
            donor.blood_group = schema.blood_group
        if schema.gender:
            donor.gender = schema.gender

        db.session.commit()
        logger.info(f"Updated Donor Profile ID: {donor.id}")
        return donor

    @staticmethod
    def soft_delete_donor(donor_id: int, reason: str = "Admin soft-deactivation") -> bool:
        """
        Soft deletes (deactivates) donor profile and user account.
        """
        donor = DonorService.get_donor_by_id(donor_id)
        user = donor.user

        donor.is_deleted = True
        user.is_deleted = True
        user.status = UserStatus.INACTIVE.value

        db.session.commit()
        logger.info(f"Soft deleted Donor Profile ID: {donor_id}. Reason: {reason}")
        return True

    @staticmethod
    def restore_donor(donor_id: int) -> DonorProfile:
        """
        Restores a soft-deleted donor account.
        """
        donor = DonorProfile.query.filter_by(id=donor_id).first()
        if not donor:
            raise DonorNotFoundException(donor_id)

        donor.is_deleted = False
        if donor.user:
            donor.user.is_deleted = False
            donor.user.status = UserStatus.ACTIVE.value

        db.session.commit()
        logger.info(f"Restored Donor Profile ID: {donor_id}")
        return donor

    @staticmethod
    def search_donors(filter_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Searches, filters, sorts, and paginates donors.
        """
        schema = DonorSearchFilterSchema(**filter_params)

        query = db.session.query(DonorProfile).join(User, DonorProfile.user_id == User.id)

        if schema.is_active:
            query = query.filter(DonorProfile.is_deleted == False, User.is_deleted == False)

        if schema.query:
            term = f"%{schema.query.strip()}%"
            query = query.filter(
                or_(
                    User.name.ilike(term),
                    User.email.ilike(term),
                    User.phone.ilike(term),
                    DonorProfile.city.ilike(term),
                    DonorProfile.blood_group.ilike(term)
                )
            )

        if schema.blood_group:
            query = query.filter(DonorProfile.blood_group == schema.blood_group)

        if schema.gender:
            query = query.filter(DonorProfile.gender == schema.gender)

        if schema.city:
            query = query.filter(DonorProfile.city.ilike(f"%{schema.city}%"))

        if schema.state:
            query = query.filter(DonorProfile.state.ilike(f"%{schema.state}%"))

        if schema.eligibility_status:
            query = query.filter(DonorProfile.eligibility_status == schema.eligibility_status)

        # Sorting
        if schema.sort_by == "name":
            sort_col = User.name
        elif schema.sort_by == "blood_group":
            sort_col = DonorProfile.blood_group
        elif schema.sort_by == "last_donation_date":
            sort_col = DonorProfile.last_donation_date
        else:
            sort_col = DonorProfile.created_at

        if schema.sort_order.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        total_count = query.count()
        donors = query.offset((schema.page - 1) * schema.per_page).limit(schema.per_page).all()

        return {
            "items": [d.to_dict() for d in donors],
            "total": total_count,
            "page": schema.page,
            "per_page": schema.per_page,
            "total_pages": (total_count + schema.per_page - 1) // schema.per_page
        }
