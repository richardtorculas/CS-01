import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import security
from app.core.enums import UserRole
from app.core.exceptions import (
    AuthenticationRequiredError,
    BarangayNotFoundError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidVerificationTokenError,
    MobileAlreadyRegisteredError,
)
from app.models import Barangay, User


def register_resident(
    db: Session, *, name: str, mobile: str, email: str, barangay_id: uuid.UUID, password: str
) -> User:
    """Create a resident account. Inputs are already normalized by the request schema."""
    if db.get(Barangay, barangay_id) is None:
        raise BarangayNotFoundError
    if db.scalar(select(User.id).where(User.email == email)) is not None:
        raise EmailAlreadyRegisteredError
    if db.scalar(select(User.id).where(User.mobile == mobile)) is not None:
        raise MobileAlreadyRegisteredError

    user = User(
        name=name,
        mobile=mobile,
        email=email,
        barangay_id=barangay_id,
        password_hash=security.hash_password(password),
        role=UserRole.RESIDENT,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as error:
        # A concurrent registration won the race past the checks above.
        db.rollback()
        raise duplicate_error_from(error) from error
    return user


def duplicate_error_from(error: IntegrityError) -> Exception:
    """Map a unique-constraint violation to the field-specific domain error."""
    message = str(error.orig).lower()
    if "email" in message:
        return EmailAlreadyRegisteredError()
    if "mobile" in message:
        return MobileAlreadyRegisteredError()
    return error


def authenticate(db: Session, *, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        security.spend_password_check_time(password)
        raise InvalidCredentialsError
    if not security.verify_password(password, user.password_hash):
        raise InvalidCredentialsError
    return user


def get_user_from_access_token(db: Session, token: str) -> User:
    user_id = security.decode_token(token, security.ACCESS_TOKEN)
    user = db.get(User, user_id) if user_id is not None else None
    if user is None:
        raise AuthenticationRequiredError("Invalid or expired token.")
    return user


def issue_access_token(user: User) -> str:
    return security.create_access_token(user.id)


def issue_verification_token(user: User) -> str:
    return security.create_email_verification_token(user.id)


def verify_email(db: Session, token: str) -> User:
    """Idempotent: verifying an already-verified account succeeds without changing it."""
    user_id = security.decode_token(token, security.EMAIL_VERIFICATION_TOKEN)
    user = db.get(User, user_id) if user_id is not None else None
    if user is None:
        raise InvalidVerificationTokenError
    if user.email_verified_at is None:
        user.email_verified_at = datetime.now(UTC)
        db.commit()
    return user
