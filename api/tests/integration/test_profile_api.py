"""US-01 AC3: residents update their profile but cannot change their role."""

from sqlalchemy import select

from app.core.enums import UserRole
from app.models import Barangay, User

ME = "/api/v1/me"
LOGIN = "/api/v1/auth/login"


def test_me_requires_authentication(client):
    response = client.get(ME)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_rejected_when_token_invalid(client):
    assert client.get(ME, headers={"Authorization": "Bearer nope"}).status_code == 401


def test_me_returns_own_profile(client, auth_headers):
    body = client.get(ME, headers=auth_headers).json()
    assert body["name"] == "Juan Dela Cruz"
    assert "password_hash" not in body


def test_profile_update_changes_name_mobile_and_barangay(client, auth_headers, db):
    other = Barangay(name="Barangay Dos")
    db.add(other)
    db.commit()
    response = client.patch(
        ME,
        headers=auth_headers,
        json={"name": "Juan D. Cruz", "mobile": "0918 555 0101", "barangay_id": str(other.id)},
    )
    assert response.status_code == 200
    body = response.json()
    assert (body["name"], body["mobile"], body["barangay_id"]) == (
        "Juan D. Cruz",
        "+639185550101",
        str(other.id),
    )


def test_timestamps_are_utc_after_reload_from_database(client, auth_headers):
    client.patch(ME, headers=auth_headers, json={"name": "Reloaded Name"})
    assert client.get(ME, headers=auth_headers).json()["created_at"].endswith("Z")
    patched = client.patch(ME, headers=auth_headers, json={"name": "Again Reloaded"})
    assert patched.json()["created_at"].endswith("Z")


def test_profile_update_cannot_change_role(client, auth_headers, db):
    response = client.patch(ME, headers=auth_headers, json={"role": "ADMIN"})
    assert response.status_code == 422
    assert db.scalar(select(User.role)) == UserRole.RESIDENT
    assert client.get(ME, headers=auth_headers).json()["role"] == "RESIDENT"


def test_profile_update_cannot_change_email_or_verification(client, auth_headers):
    for body in ({"email": "new@example.com"}, {"email_verified": True}, {"password": "x" * 9}):
        assert client.patch(ME, headers=auth_headers, json=body).status_code == 422


def test_profile_update_conflict_when_mobile_belongs_to_another_resident(
    client, auth_headers, make_payload
):
    client.post(
        "/api/v1/auth/register",
        json=make_payload(email="ana@example.com", mobile="09170000000"),
    )
    response = client.patch(ME, headers=auth_headers, json={"mobile": "09170000000"})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "MOBILE_ALREADY_REGISTERED"


def test_profile_update_requires_authentication(client):
    assert client.patch(ME, json={"name": "Someone"}).status_code == 401


def test_empty_profile_update_changes_nothing(client, auth_headers):
    response = client.patch(ME, headers=auth_headers, json={})
    assert response.status_code == 200
    assert response.json()["name"] == "Juan Dela Cruz"


def test_login_returns_bearer_token_for_correct_credentials(client, make_payload):
    client.post("/api/v1/auth/register", json=make_payload())
    response = client.post(LOGIN, json={"email": "JUAN@example.com", "password": "correct-horse"})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 15 * 60


def test_login_rejected_with_same_error_for_wrong_password_and_unknown_email(client, make_payload):
    client.post("/api/v1/auth/register", json=make_payload())
    wrong_password = client.post(LOGIN, json={"email": "juan@example.com", "password": "nope-nope"})
    unknown_email = client.post(LOGIN, json={"email": "x@example.com", "password": "nope-nope"})
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()
