import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import get_settings

ACCESS_TOKEN = "access"
EMAIL_VERIFICATION_TOKEN = "email_verification"

_hasher = PasswordHasher()
# Verified against when the account does not exist, so login timing does not reveal it.
_DUMMY_HASH = _hasher.hash("not-a-real-password")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def spend_password_check_time(password: str) -> None:
    verify_password(password, _DUMMY_HASH)


def _create_token(user_id: uuid.UUID, token_type: str, lifetime: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    claims = {"sub": str(user_id), "typ": token_type, "iat": now, "exp": now + lifetime}
    return jwt.encode(claims, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: uuid.UUID) -> str:
    minutes = get_settings().access_token_minutes
    return _create_token(user_id, ACCESS_TOKEN, timedelta(minutes=minutes))


def create_email_verification_token(user_id: uuid.UUID) -> str:
    hours = get_settings().email_verification_hours
    return _create_token(user_id, EMAIL_VERIFICATION_TOKEN, timedelta(hours=hours))


def decode_token(token: str, expected_type: str) -> uuid.UUID | None:
    """Return the user id, or None if the token is invalid, expired or of the wrong type.

    The type check stops a verification-link token being used as an access token.
    """
    settings = get_settings()
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub", "typ"]},
        )
        if claims["typ"] != expected_type:
            return None
        return uuid.UUID(claims["sub"])
    except (jwt.PyJWTError, ValueError):
        return None


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    """Only this digest is stored, so a database leak does not yield usable refresh tokens."""
    return hashlib.sha256(token.encode()).hexdigest()
