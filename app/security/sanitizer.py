import html
import re
from typing import Any, Dict, Union

class InputSanitizer:
    """
    Sanitizes request parameters and strings against XSS attacks and SQL injection patterns.
    """

    SQL_INJECTION_PATTERNS = [
        r"(--)",
        r"(\/\*)",
        r"(\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|EXEC|TRUNCATE)\b)",
        r"(OR\s+1\s*=\s*1)",
        r"(';)"
    ]

    @classmethod
    def sanitize_string(cls, text: str) -> str:
        """
        Escapes HTML entities to prevent XSS attacks.
        """
        if not text or not isinstance(text, str):
            return text
        cleaned = text.strip()
        return html.escape(cleaned)

    @classmethod
    def contains_sql_injection(cls, text: str) -> bool:
        """
        Checks if text contains potential SQL injection patterns.
        """
        if not text or not isinstance(text, str):
            return False

        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively sanitizes dictionary strings.
        """
        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            clean_key = cls.sanitize_string(str(key))
            if isinstance(value, str):
                sanitized[clean_key] = cls.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[clean_key] = cls.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[clean_key] = [
                    cls.sanitize_string(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                sanitized[clean_key] = value
        return sanitized
