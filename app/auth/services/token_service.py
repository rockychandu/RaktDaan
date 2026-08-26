from app.database.connection import db
from app.database.models.user import UserSession
from app.security.jwt_manager import JWTManager

class TokenService:
    """
    Token Revocation & Management Service.
    """

    @classmethod
    def revoke_session(cls, jti: str) -> bool:
        """
        Revokes an active user session by JTI token string.
        """
        if not jti:
            return False

        # Add JTI to Security Revocation Cache
        JWTManager.revoke_token(jti)

        # Update DB session
        session = UserSession.query.filter_by(session_token_jti=jti).first()
        if session:
            session.is_active = False
            db.session.commit()
            return True
        return False
