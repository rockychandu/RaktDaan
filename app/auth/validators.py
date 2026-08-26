import re
from datetime import datetime, date
from app.users.models import BloodGroup

class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(str(errors))

def validate_donor_registration(data: dict) -> dict:
    """
    Validates donor registration input data according to all requirements.
    Raises ValidationError if invalid.
    Returns cleaned data if valid.
    """
    if not isinstance(data, dict):
        raise ValidationError({"message": "Invalid payload format. Expected JSON object."})

    required_fields = [
        "name", "email", "phone", "password", "confirm_password",
        "date_of_birth", "gender", "blood_group", "address", "city",
        "state", "emergency_contact"
    ]

    errors = {}

    # 1. Check required fields
    for field in required_fields:
        val = data.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            errors[field] = f"Field '{field}' is required and cannot be empty."

    if errors:
        raise ValidationError(errors)

    # Clean string inputs
    name = str(data["name"]).strip()
    email = str(data["email"]).strip().lower()
    phone = str(data["phone"]).strip()
    password = str(data["password"])
    confirm_password = str(data["confirm_password"])
    date_of_birth_raw = str(data["date_of_birth"]).strip()
    gender = str(data["gender"]).strip().capitalize()
    blood_group = str(data["blood_group"]).strip().upper()
    address = str(data["address"]).strip()
    city = str(data["city"]).strip()
    state = str(data["state"]).strip()
    emergency_contact = str(data["emergency_contact"]).strip()

    # 2. Email format
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        errors["email"] = "Invalid email format."

    # 3. Phone & Emergency Contact format
    phone_pattern = r"^\+?[0-9]{10,15}$"
    if not re.match(phone_pattern, phone):
        errors["phone"] = "Invalid phone number. Must contain 10 to 15 digits."
    if not re.match(phone_pattern, emergency_contact):
        errors["emergency_contact"] = "Invalid emergency contact. Must contain 10 to 15 digits."

    # 4. Password Strength
    if len(password) < 8:
        errors["password"] = "Password must be at least 8 characters long."
    elif not re.search(r"[A-Z]", password):
        errors["password"] = "Password must contain at least one uppercase letter."
    elif not re.search(r"[a-z]", password):
        errors["password"] = "Password must contain at least one lowercase letter."
    elif not re.search(r"[0-9]", password):
        errors["password"] = "Password must contain at least one digit."
    elif not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        errors["password"] = "Password must contain at least one special character."

    # 5. Password Match
    if password != confirm_password:
        errors["confirm_password"] = "Password and confirm password do not match."

    # 6. Date of Birth & Age
    try:
        dob = datetime.strptime(date_of_birth_raw, "%Y-%m-%d").date()
        today = date.today()
        if dob >= today:
            errors["date_of_birth"] = "Date of birth must be in the past."
        else:
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                errors["date_of_birth"] = "Donor must be at least 18 years old."
            elif age > 100:
                errors["date_of_birth"] = "Invalid date of birth."
    except ValueError:
        errors["date_of_birth"] = "Date of birth must be in YYYY-MM-DD format."
        dob = None

    # 7. Gender
    if gender not in ["Male", "Female", "Other"]:
        errors["gender"] = "Gender must be one of: Male, Female, Other."

    # 8. Blood Group
    allowed_groups = BloodGroup.list_values()
    if blood_group not in allowed_groups:
        errors["blood_group"] = f"Invalid blood group. Must be one of: {', '.join(allowed_groups)}"

    if errors:
        raise ValidationError(errors)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "password": password,
        "date_of_birth": dob,
        "gender": gender,
        "blood_group": blood_group,
        "address": address,
        "city": city,
        "state": state,
        "emergency_contact": emergency_contact
    }

def validate_login_request(data: dict) -> tuple:
    """
    Validates login input data. Returns (email, password).
    """
    if not isinstance(data, dict):
        raise ValidationError({"message": "Invalid payload format. Expected JSON object."})

    email = data.get("email")
    password = data.get("password")

    errors = {}
    if not email or not str(email).strip():
        errors["email"] = "Email is required."
    if not password:
        errors["password"] = "Password is required."

    if errors:
        raise ValidationError(errors)

    return str(email).strip().lower(), str(password)
