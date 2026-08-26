import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Set
from app.config import Config

class JWTManager:
    """
    Enterprise JWT Token Engine.
    Handles JWT access token creation, refresh tokens, signature verification,
    and in-memory/revocation blacklist tracking.
    """

    _revoked_token_jti_cache: Set[str] = set()

    @classmethod
    def generate_token_pair(cls, user_id: int, role: str, email: str, additional_claims: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generates both an Access Token and a Refresh Token for authenticated user.
        """
        now = datetime.now(timezone.utc)
        jti_access = f"access_{user_id}_{int(now.timestamp())}"
        jti_refresh = f"refresh_{user_id}_{int(now.timestamp())}"

        # Access Token Payload
        access_payload = {
            "sub": str(user_id),
            "role": role,
            "email": email,
            "jti": jti_access,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        if additional_claims:
            access_payload.update(additional_claims)

        # Refresh Token Payload
        refresh_payload = {
            "sub": str(user_id),
            "role": role,
            "jti": jti_refresh,
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=Config.REFRESH_TOKEN_EXPIRE_DAYS)
        }

        access_token = jwt.encode(access_payload, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, Config.SECRET_KEY, algorithm=Config.ALGORITHM)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": Config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "role": role
        }

    @classmethod
    def decode_and_verify(cls, token: str, expected_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Decodes token, validates signature, expiration, type, and checks revocation blacklist.
        """
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
            
            # Check token type match
            if payload.get("type") != expected_type:
                return None

            # Check revocation
            jti = payload.get("jti")
            if jti and jti in cls._revoked_token_jti_cache:
                return None

            return payload
        except (jwt.PyJWTError, Exception):
            return None

    @classmethod
    def revoke_token(cls, jti: str):
        """
        Blacklists a token JTI.
        """
        if jti:
            cls._revoked_token_jti_cache.add(jti)

    @classmethod
    def is_token_revoked(cls, jti: str) -> bool:
        """
        Checks if token JTI has been revoked.
        """
        return jti in cls._revoked_token_jti_cache
