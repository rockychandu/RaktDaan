import re
import math
from typing import Tuple, List, Dict
from werkzeug.security import generate_password_hash, check_password_hash
from app.config import Config

class PasswordPolicyEngine:
    """
    Advanced Enterprise Password Policy & Quality Enforcement Engine.
    Handles entropy calculations, complexity requirements, dictionary attack protection,
    and password history validation.
    """

    COMMON_PASSWORDS = {
        "password", "password123", "admin123", "raktdaan123", "12345678",
        "letmein123", "welcome123", "bloodbank123", "donor12345"
    }

    @classmethod
    def evaluate_entropy(cls, password: str) -> float:
        """
        Calculates Shannon Entropy of a password string in bits.
        """
        if not password:
            return 0.0

        charset_size = 0
        if re.search(r"[a-z]", password):
            charset_size += 26
        if re.search(r"[A-Z]", password):
            charset_size += 26
        if re.search(r"[0-9]", password):
            charset_size += 10
        if re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
            charset_size += 32

        if charset_size == 0:
            return 0.0

        entropy = len(password) * math.log2(charset_size)
        return round(entropy, 2)

    @classmethod
    def validate_password_strength(cls, password: str) -> Tuple[bool, List[str]]:
        """
        Validates password against enterprise complexity requirements.
        Returns (is_valid, list_of_violation_messages).
        """
        violations = []

        if len(password) < Config.MIN_PASSWORD_LENGTH:
            violations.append(f"Password must be at least {Config.MIN_PASSWORD_LENGTH} characters long.")

        if Config.REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
            violations.append("Password must contain at least one uppercase letter (A-Z).")

        if Config.REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
            violations.append("Password must contain at least one lowercase letter (a-z).")

        if Config.REQUIRE_DIGIT and not re.search(r"[0-9]", password):
            violations.append("Password must contain at least one numeric digit (0-9).")

        if Config.REQUIRE_SPECIAL_CHAR and not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
            violations.append("Password must contain at least one special character (e.g. !@#$%^&*).")

        if password.lower() in cls.COMMON_PASSWORDS:
            violations.append("Password is too common or easily guessable.")

        entropy = cls.evaluate_entropy(password)
        if entropy < 30.0:
            violations.append("Password entropy is too low. Use a diverse combination of characters.")

        return len(violations) == 0, violations

    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hashes password using secure PBKDF2/scrypt/bcrypt algorithm.
        """
        return generate_password_hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies plain text password against stored hash.
        """
        if not plain_password or not hashed_password:
            return False
        return check_password_hash(hashed_password, plain_password)

    @classmethod
    def check_password_history(cls, new_password: str, history_hashes: List[str]) -> bool:
        """
        Verifies that new_password does not match any of the previous N password hashes.
        Returns True if password is fresh (not in history), False if recycled.
        """
        for old_hash in history_hashes:
            if cls.verify_password(new_password, old_hash):
                return False
        return True
