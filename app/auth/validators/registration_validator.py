import re
from datetime import datetime, date
from typing import Dict, Any
from app.users.models import BloodGroup, Gender
from app.users.exceptions import ValidationException
from app.security.password_policy import PasswordPolicyEngine
from app.utils.formatters import StringFormatter

class RegistrationValidator:
    """
    Comprehensive 12-Field Donor Registration Validation Engine.
    Enforces required fields, email format, phone format, age limits,
    blood group enums, and password entropy rules.
    """

    REQUIRED_FIELDS = [
        "name", "email", "phone", "password", "confirm_password",
        "date_of_birth", "gender", "blood_group", "address", "city",
        "state", "emergency_contact"
    ]

    @classmethod
    def validate(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise ValidationException({"message": "Invalid request body format. Expected JSON object."})

        errors = {}

        # 1. Required Fields Check
        for field in cls.REQUIRED_FIELDS:
            val = data.get(field)
            if val is None or (isinstance(val, str) and not val.strip()):
                errors[field] = f"Field '{field}' is required and cannot be empty."

        if errors:
            raise ValidationException(errors)

        # 2. String Cleaning
        name = StringFormatter.clean_string(data["name"])
        email = StringFormatter.format_email(data["email"])
        phone = StringFormatter.format_phone(data["phone"])
        password = str(data["password"])
        confirm_password = str(data["confirm_password"])
        dob_raw = str(data["date_of_birth"]).strip()
        gender = StringFormatter.clean_string(data["gender"]).capitalize()
        blood_group = StringFormatter.format_blood_group(data["blood_group"])
        address = StringFormatter.clean_string(data["address"])
        city = StringFormatter.clean_string(data["city"])
        state = StringFormatter.clean_string(data["state"])
        emergency_contact = StringFormatter.format_phone(data["emergency_contact"])

        # 3. Name Length Validation
        if len(name) < 2 or len(name) > 100:
            errors["name"] = "Full Name must be between 2 and 100 characters."

        # 4. Email Format
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            errors["email"] = "Invalid email format."

        # 5. Phone & Emergency Contact Format (10-15 digits)
        phone_pattern = r"^\+?[0-9]{10,15}$"
        if not re.match(phone_pattern, phone):
            errors["phone"] = "Invalid phone number. Must contain 10 to 15 numeric digits."
        if not re.match(phone_pattern, emergency_contact):
            errors["emergency_contact"] = "Invalid emergency contact number. Must contain 10 to 15 numeric digits."

        # 6. Password Strength & Confirmation
        is_strong, pwd_violations = PasswordPolicyEngine.validate_password_strength(password)
        if not is_strong:
            errors["password"] = " ".join(pwd_violations)

        if password != confirm_password:
            errors["confirm_password"] = "Password and Confirm Password do not match."

        # 7. Date of Birth & Age Check
        parsed_dob = StringFormatter.parse_date(dob_raw)
        if not parsed_dob:
            errors["date_of_birth"] = "Date of Birth must be in valid YYYY-MM-DD format."
        else:
            today = date.today()
            if parsed_dob >= today:
                errors["date_of_birth"] = "Date of birth must be in the past."
            else:
                age = today.year - parsed_dob.year - ((today.month, today.day) < (parsed_dob.month, parsed_dob.day))
                if age < 18:
                    errors["date_of_birth"] = "Donor must be at least 18 years old."
                elif age > 100:
                    errors["date_of_birth"] = "Invalid date of birth."

        # 8. Gender Check
        if gender not in Gender.list_values():
            errors["gender"] = f"Gender must be one of: {', '.join(Gender.list_values())}"

        # 9. Blood Group Check
        if blood_group not in BloodGroup.list_values():
            errors["blood_group"] = f"Invalid blood group. Must be one of: {', '.join(BloodGroup.list_values())}"

        if errors:
            raise ValidationException(errors)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "password": password,
            "date_of_birth": parsed_dob,
            "gender": gender,
            "blood_group": blood_group,
            "address": address,
            "city": city,
            "state": state,
            "emergency_contact": emergency_contact
        }
