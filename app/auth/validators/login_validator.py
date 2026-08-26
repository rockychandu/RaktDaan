from typing import Dict, Any, Tuple
from app.users.exceptions import ValidationException
from app.utils.formatters import StringFormatter

class LoginValidator:
    """
    Validator for Login & Authentication Requests.
    """

    @classmethod
    def validate(cls, data: Dict[str, Any]) -> Tuple[str, str]:
        if not isinstance(data, dict):
            raise ValidationException({"message": "Invalid request payload format. Expected JSON object."})

        email_raw = data.get("email")
        password_raw = data.get("password")

        errors = {}
        if not email_raw or not str(email_raw).strip():
            errors["email"] = "Email is required."
        if not password_raw:
            errors["password"] = "Password is required."

        if errors:
            raise ValidationException(errors)

        email = StringFormatter.format_email(email_raw)
        password = str(password_raw)

        return email, password
