import random
from datetime import date, timedelta
from app.main import create_app
from app.database.connection import db
from app.database.models.user import User
from app.database.models.donor import DonorProfile
from app.users.models import UserRole, UserStatus, BloodGroup, Gender
from app.security.password_policy import PasswordPolicyEngine

FIRST_NAMES = ["Aarav", "Vihaan", "Aditya", "Sai", "Reyansh", "Ananya", "Diya", "Isha", "Riya", "Kavya"]
LAST_NAMES = ["Sharma", "Verma", "Patel", "Mehta", "Gupta", "Nair", "Rao", "Joshi", "Singh", "Kumar"]
CITIES = [("Mumbai", "Maharashtra"), ("Delhi", "Delhi"), ("Bengaluru", "Karnataka"), ("Pune", "Maharashtra"), ("Chennai", "Tamil Nadu")]

def generate_mock_donors(count: int = 50):
    app = create_app()
    with app.app_context():
        print(f"Generating {count} realistic mock donor accounts...")
        created_count = 0

        for i in range(count):
            fname = random.choice(FIRST_NAMES)
            lname = random.choice(LAST_NAMES)
            name = f"{fname} {lname}"
            email = f"donor_{random.randint(10000, 99999)}@example.com"
            phone = f"98{random.randint(10000000, 99999999)}"
            city, state = random.choice(CITIES)
            blood_group = random.choice(BloodGroup.list_values())
            gender = random.choice(Gender.list_values())

            # Generate random DOB (age 19 to 55)
            days_old = random.randint(19*365, 55*365)
            dob = date.today() - timedelta(days=days_old)

            user = User(
                name=name,
                email=email,
                password_hash=PasswordPolicyEngine.hash_password("MockDonor123!"),
                role=UserRole.DONOR.value,
                phone=phone,
                status=UserStatus.ACTIVE.value
            )
            db.session.add(user)
            db.session.flush()

            profile = DonorProfile(
                user_id=user.id,
                date_of_birth=dob,
                gender=gender,
                blood_group=blood_group,
                address=f"{random.randint(10, 999)} Healthcare Road",
                city=city,
                state=state,
                emergency_contact=f"97{random.randint(10000000, 99999999)}"
            )
            db.session.add(profile)
            created_count += 1

        db.session.commit()
        print(f"Successfully created {created_count} mock donor accounts.")

if __name__ == "__main__":
    generate_mock_donors(50)
