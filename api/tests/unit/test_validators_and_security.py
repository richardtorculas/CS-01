import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core import security
from app.core.config import get_settings
from app.core.validators import normalize_email, normalize_ph_mobile


@pytest.mark.parametrize(
    "raw",
    ["09171234567", "+639171234567", "639171234567", "0917 123 4567", "0917-123-4567"],
)
def test_mobile_normalized_to_e164_when_accepted_format(raw):
    assert normalize_ph_mobile(raw) == "+639171234567"


@pytest.mark.parametrize("raw", ["", "12345", "08171234567", "091712345678", "+15551234567", "abc"])
def test_mobile_rejected_when_not_a_ph_mobile_number(raw):
    with pytest.raises(ValueError):
        normalize_ph_mobile(raw)


def test_email_lowercased_and_trimmed():
    assert normalize_email("  Juan@Example.COM ") == "juan@example.com"


def test_password_hash_is_argon2_and_verifies():
    hashed = security.hash_password("correct-horse")
    assert hashed.startswith("$argon2")
    assert "correct-horse" not in hashed
    assert security.verify_password("correct-horse", hashed)
    assert not security.verify_password("wrong-horse", hashed)


def test_verify_password_false_when_hash_is_malformed():
    assert not security.verify_password("anything", "not-a-hash")


def test_access_token_round_trips_user_id():
    user_id = uuid.uuid4()
    token = security.create_access_token(user_id)
    assert security.decode_token(token, security.ACCESS_TOKEN) == user_id


def test_token_rejected_when_used_as_the_wrong_type():
    token = security.create_email_verification_token(uuid.uuid4())
    assert security.decode_token(token, security.ACCESS_TOKEN) is None


def test_token_rejected_when_expired():
    settings = get_settings()
    past = datetime.now(UTC) - timedelta(minutes=1)
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "typ": security.ACCESS_TOKEN, "exp": past},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    assert security.decode_token(token, security.ACCESS_TOKEN) is None


def test_token_rejected_when_signed_with_another_secret():
    token = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "typ": security.ACCESS_TOKEN,
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        },
        "some-other-secret-some-other-secret-1234",
        algorithm="HS256",
    )
    assert security.decode_token(token, security.ACCESS_TOKEN) is None


def test_token_rejected_when_garbage():
    assert security.decode_token("not.a.jwt", security.ACCESS_TOKEN) is None
