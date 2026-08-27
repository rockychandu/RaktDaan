"""
Auth Validators Package Exports.
"""
from app.users.exceptions import ValidationException

class ValidationError(ValidationException):
    """Alias for ValidationException to support legacy imports."""
    pass

from app.auth.validators.registration_validator import RegistrationValidator
from app.auth.validators.login_validator import LoginValidator

__all__ = ["RegistrationValidator", "LoginValidator", "ValidationError", "ValidationException"]
