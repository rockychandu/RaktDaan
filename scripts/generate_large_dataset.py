import random
from datetime import date, timedelta
from app.main import create_app
from app.database.connection import db
from app.database.models.user import User, UserAuditLog
from app.database.models.donor import DonorProfile, DonorMedicalHistory, DonorEligibility
from app.database.models.blood_bank import BloodBag, BloodDrive
from app.users.models import UserRole, UserStatus, BloodGroup, Gender, EligibilityStatus
from app.security.password_policy import PasswordPolicyEngine

INDIAN_CITIES = [
    ("Mumbai", "Maharashtra"), ("Delhi", "Delhi"), ("Bengaluru", "Karnataka"),
    ("Hyderabad", "Telangana"), ("Ahmedabad", "Gujarat"), ("Chennai", "Tamil Nadu"),
    ("Kolkata", "West Bengal"), ("Surat", "Gujarat"), ("Pune", "Maharashtra"),
    ("Jaipur", "Rajasthan"), ("Lucknow", "Uttar Pradesh"), ("Kanpur", "Uttar Pradesh"),
    ("Nagpur", "Maharashtra"), ("Indore", "Madhya Pradesh"), ("Thane", "Maharashtra"),
    ("Bhopal", "Madhya Pradesh"), ("Visakhapatnam", "Andhra Pradesh"), ("Pimpri-Chinchwad", "Maharashtra"),
    ("Patna", "Bihar"), ("Vadodara", "Gujarat"), ("Ghaziabad", "Uttar Pradesh"),
    ("Ludhiana", "Punjab"), ("Agra", "Uttar Pradesh"), ("Nashik", "Maharashtra")
]

FIRST_NAMES = [
    "Aarav", "Vihaan", "Aditya", "Sai", "Reyansh", "Mohammad", "Arjun", "Kabir", "Rohan", "Ishaan",
    "Ananya", "Diya", "Isha", "Riya", "Kavya", "Aadhya", "Pari", "Anushka", "Saanvi", "Aditi",
    "Rahul", "Amit", "Priya", "Neha", "Vikram", "Suresh", "Ramesh", "Pooja", "Deepak", "Rajesh"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Mehta", "Gupta", "Nair", "Rao", "Joshi", "Singh", "Kumar",
    "Deshmukh", "Kulkarni", "Chowdhury", "Banerjee", "Reddy", "Iyer", "Pillai", "Agarwal", "Bhat", "Shah"
]

def seed_enterprise_dataset(donor_count: int = 150):
    app = create_app()
    with app.app_context():
        print(f"Generating enterprise dataset with {donor_count} donor profiles and associated entities...")

        created_donors = 0
        for i in range(donor_count):
            fname = random.choice(FIRST_NAMES)
            lname = random.choice(LAST_NAMES)
            name = f"{fname} {lname}"
            email = f"donor.onboarding.{i+1000}@raktdaan-enterprise.org"
            phone = f"98{random.randint(10000000, 99999999)}"
            city, state = random.choice(INDIAN_CITIES)
            blood_group = random.choice(BloodGroup.list_values())
            gender = random.choice(Gender.list_values())

            # Calculate random DOB between 18 and 60 years old
            days_old = random.randint(18*365 + 10, 60*365)
            dob = date.today() - timedelta(days=days_old)

            user = User(
                name=name,
                email=email,
                password_hash=PasswordPolicyEngine.hash_password("EnterpriseDonor123!"),
                role=UserRole.DONOR.value,
                phone=phone,
                status=UserStatus.ACTIVE.value
            )
            db.session.add(user)
            db.session.flush()

            # Create Donor Profile
            profile = DonorProfile(
                user_id=user.id,
                date_of_birth=dob,
                gender=gender,
                blood_group=blood_group,
                address=f"Flat {random.randint(101, 909)}, Block {random.choice(['A','B','C','D'])}, Healthcare Enclave",
                city=city,
                state=state,
                emergency_contact=f"97{random.randint(10000000, 99999999)}",
                eligibility_status=EligibilityStatus.ELIGIBLE.value
            )
            db.session.add(profile)
            db.session.flush()

            # Create Medical History
            med_history = DonorMedicalHistory(
                donor_profile_id=profile.id,
                weight_kg=random.uniform(55.0, 90.0),
                hemoglobin_level=random.uniform(12.5, 16.5),
                blood_pressure_sys=random.randint(110, 130),
                blood_pressure_dia=random.randint(70, 85),
                pulse_rate=random.randint(65, 80),
                has_chronic_illness=False,
                is_on_medication=False,
                medical_notes="Passed routine pre-donation screening."
            )
            db.session.add(med_history)

            # Create Audit Log
            audit = UserAuditLog(
                user_id=user.id,
                action_type="ENTERPRISE_DATA_SEEDED",
                description=f"Enterprise mock donor record generated for {email}"
            )
            db.session.add(audit)
            created_donors += 1

        db.session.commit()
        print(f"Enterprise dataset generation complete! Created {created_donors} donors.")

if __name__ == "__main__":
    seed_enterprise_dataset(150)
