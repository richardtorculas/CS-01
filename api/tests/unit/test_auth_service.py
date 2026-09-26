import uuid

import pytest
from sqlalchemy import select

from app.core.enums import UserRole
from app.core.exceptions import (
    AuthenticationRequiredError,
    BarangayNotFoundError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidVerificationTokenError,
    MobileAlreadyRegisteredError,
)
from app.core.security import create_access_token
from app.models import User
from app.services import auth_service, user_service


def _register(db, barangay, **overrides):
    fields = {
        "name": "Juan Dela Cruz",
        "mobile": "+639171234567",
        "email": "juan@example.com",
        "barangay_id": barangay.id,
        "password": "correct-horse",
    } | overrides
    return auth_service.register_resident(db, **fields)


def test_register_creates_unverified_resident_with_hashed_password(db, barangay):
    user = _register(db, barangay)
    assert user.role == UserRole.RESIDENT
    assert user.email_verified_at is None
    assert user.password_hash.startswith("$argon2")


def test_register_rejected_when_email_already_used(db, barangay):
    _register(db, barangay)
    with pytest.raises(EmailAlreadyRegisteredError):
        _register(db, barangay, mobile="+639179999999")


def test_register_rejected_when_mobile_already_used(db, barangay):
    _register(db, barangay)
    with pytest.raises(MobileAlreadyRegisteredError):
        _register(db, barangay, email="other@example.com")


def test_register_rejected_when_barangay_unknown(db, barangay):
    with pytest.raises(BarangayNotFoundError):
        _register(db, barangay, barangay_id=uuid.uuid4())
    assert db.scalar(select(User.id)) is None


def test_authenticate_succeeds_with_correct_password(db, barangay):
    user = _register(db, barangay)
    assert auth_service.authenticate(db, email="juan@example.com", password="correct-horse") == user


@pytest.mark.parametrize("email", ["juan@example.com", "nobody@example.com"])
def test_authenticate_rejected_when_credentials_wrong(db, barangay, email):
    _register(db, barangay)
    with pytest.raises(InvalidCredentialsError):
        auth_service.authenticate(db, email=email, password="wrong-password")


def test_access_token_lookup_rejected_when_user_missing(db):
    with pytest.raises(AuthenticationRequiredError):
        auth_service.get_user_from_access_token(db, create_access_token(uuid.uuid4()))


def test_verify_email_marks_verified_and_is_idempotent(db, barangay):
    user = _register(db, barangay)
    token = auth_service.issue_verification_token(user)
    auth_service.verify_email(db, token)
    first = user.email_verified_at
    assert first is not None
    auth_service.verify_email(db, token)
    assert user.email_verified_at == first


def test_verify_email_rejected_when_token_is_an_access_token(db, barangay):
    user = _register(db, barangay)
    with pytest.raises(InvalidVerificationTokenError):
        auth_service.verify_email(db, create_access_token(user.id))


def test_update_profile_changes_only_given_fields(db, barangay):
    user = _register(db, barangay)
    user_service.update_profile(db, user, name="Juan D. Cruz")
    assert (user.name, user.mobile) == ("Juan D. Cruz", "+639171234567")


def test_update_profile_rejected_when_mobile_belongs_to_another_user(db, barangay):
    _register(db, barangay)
    other = _register(db, barangay, email="ana@example.com", mobile="+639170000000")
    with pytest.raises(MobileAlreadyRegisteredError):
        user_service.update_profile(db, other, mobile="+639171234567")


def test_update_profile_allows_resubmitting_own_mobile(db, barangay):
    user = _register(db, barangay)
    user_service.update_profile(db, user, mobile="+639171234567")
    assert user.mobile == "+639171234567"


def test_update_profile_rejected_when_barangay_unknown(db, barangay):
    user = _register(db, barangay)
    with pytest.raises(BarangayNotFoundError):
        user_service.update_profile(db, user, barangay_id=uuid.uuid4())
