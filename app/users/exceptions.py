class DomainException(Exception):
    """Base domain exception for RaktDaan system."""
    def __init__(self, message: str, status_code: int = 400, errors: dict = None):
        self.message = message
        self.status_code = status_code
        self.errors = errors or {}
        super().__init__(self.message)


class UserNotFoundException(DomainException):
    def __init__(self, message: str = "User account not found."):
        super().__init__(message, status_code=404)


class DuplicateUserException(DomainException):
    def __init__(self, message: str = "Email is already registered."):
        super().__init__(message, status_code=422, errors={"email": message})


class ValidationException(DomainException):
    def __init__(self, errors: dict, message: str = "Validation failed for request data."):
        super().__init__(message, status_code=422, errors=errors)


class SecurityException(DomainException):
    def __init__(self, message: str = "Security violation detected.", status_code: int = 401):
        super().__init__(message, status_code=status_code)


class AccountLockedException(SecurityException):
    def __init__(self, message: str = "Account is temporarily locked due to multiple failed login attempts."):
        super().__init__(message, status_code=423)


class UnauthorizedRoleException(SecurityException):
    def __init__(self, message: str = "Unauthorized role access for this endpoint."):
        super().__init__(message, status_code=401)


class InsufficientPermissionException(DomainException):
    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(message, status_code=403)
