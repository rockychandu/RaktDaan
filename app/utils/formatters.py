import re
from datetime import datetime, date
from typing import Optional

class StringFormatter:
    """
    Utility helpers for cleaning and standardizing strings, dates, and phone numbers.
    """

    @classmethod
    def clean_string(cls, text: Optional[str]) -> Optional[str]:
        if text is None:
            return None
        return str(text).strip()

    @classmethod
    def format_email(cls, email: str) -> str:
        if not email:
            return ""
        return str(email).strip().lower()

    @classmethod
    def format_phone(cls, phone: str) -> str:
        if not phone:
            return ""
        cleaned = re.sub(r"[^\d+]", "", str(phone).strip())
        return cleaned

    @classmethod
    def parse_date(cls, date_str: str) -> Optional[date]:
        if not date_str:
            return None
        try:
            return datetime.strptime(str(date_str).strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

    @classmethod
    def format_blood_group(cls, blood_group: str) -> str:
        if not blood_group:
            return ""
        return str(blood_group).strip().upper()
