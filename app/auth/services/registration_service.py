from app.database.connection import db
from app.database.models.user import User, UserAuditLog
from app.database.models.donor import DonorProfile, DonorPreference
from app.users.models import UserRole, UserStatus, AuditActionType, EligibilityStatus
from app.users.exceptions import DuplicateUserException
from app.security.password_policy import PasswordPolicyEngine

class RegistrationService:
    """
    Business Service handling Donor Onboarding and Profile Creation.
    """

    @classmethod
    def register_donor(cls, validated_data: dict, ip_address: str = None) -> User:
        """
        Atomically creates User account, DonorProfile, initial Preferences, and Audit Log entry.
        """
        email = validated_data["email"]

        # 1. Duplicate email check
        existing_user = User.query.filter_by(email=email, is_deleted=False).first()
        if existing_user:
            raise DuplicateUserException("Email is already registered. Please login or use a different email.")

        # 2. Secure password hashing
        hashed_password = PasswordPolicyEngine.hash_password(validated_data["password"])

        # 3. Create User entity
        new_user = User(
            name=validated_data["name"],
            email=email,
            password_hash=hashed_password,
            role=UserRole.DONOR.value,
            phone=validated_data["phone"],
            status=UserStatus.ACTIVE.value
        )
        db.session.add(new_user)
        db.session.flush() # Populate new_user.id

        # 4. Create DonorProfile entity (AES-256 encrypted fields handled via property setters)
        new_profile = DonorProfile(
            user_id=new_user.id,
            date_of_birth=validated_data["date_of_birth"],
            gender=validated_data["gender"],
            blood_group=validated_data["blood_group"],
            address=validated_data["address"],
            city=validated_data["city"],
            state=validated_data["state"],
            emergency_contact=validated_data["emergency_contact"],
            eligibility_status=EligibilityStatus.ELIGIBLE.value
        )
        db.session.add(new_profile)
        db.session.flush()

        # 5. Create Donor Preferences
        preferences = DonorPreference(donor_profile_id=new_profile.id)
        db.session.add(preferences)

        # 6. Record Audit Log
        audit_log = UserAuditLog(
            user_id=new_user.id,
            action_type=AuditActionType.USER_REGISTERED.value,
            description=f"Donor account registered successfully: {email}",
            ip_address=ip_address
        )
        db.session.add(audit_log)

        # 7. Commit Transaction
        db.session.commit()
        return new_user
