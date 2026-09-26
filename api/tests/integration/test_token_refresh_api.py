"""US-02 AC1: access token 15 min, refresh token 7 d, rotation invalidates the used token."""

from datetime import UTC, datetime, timedelta

import jwt
from sqlalchemy import select

from app.core.config import get_settings
from app.models import RefreshToken

REFRESH = "/api/v1/auth/refresh"
LOGOUT = "/api/v1/auth/logout"
ME = "/api/v1/me"


def _login(client, make_payload) -> dict:
    payload = make_payload()
    client.post("/api/v1/auth/register", json=payload)
    response = client.post(
        "/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]}
    )
    return response.json()


def _bearer(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def test_login_returns_access_and_refresh_tokens(client, make_payload):
    body = _login(client, make_payload)
    assert body["refresh_token"] and body["access_token"]
    assert body["expires_in"] == 15 * 60


def test_access_token_expires_in_15_minutes(client, make_payload):
    claims = jwt.decode(
        _login(client, make_payload)["access_token"],
        get_settings().jwt_secret,
        algorithms=["HS256"],
    )
    assert claims["exp"] - claims["iat"] == 15 * 60


def test_refresh_token_lasts_7_days(client, make_payload, db):
    _login(client, make_payload)
    expires = db.scalar(select(RefreshToken)).expires_at
    remaining = expires.replace(tzinfo=expires.tzinfo or UTC) - datetime.now(UTC)
    assert timedelta(days=6, hours=23) < remaining <= timedelta(days=7)


def test_refresh_token_is_stored_hashed(client, make_payload, db):
    body = _login(client, make_payload)
    assert db.scalar(select(RefreshToken)).token_hash != body["refresh_token"]


def test_refresh_returns_working_new_pair(client, make_payload):
    first = _login(client, make_payload)
    response = client.post(REFRESH, json={"refresh_token": first["refresh_token"]})
    assert response.status_code == 200
    second = response.json()
    assert second["refresh_token"] != first["refresh_token"]
    assert client.get(ME, headers=_bearer(second["access_token"])).status_code == 200


def test_refresh_rejects_token_already_used(client, make_payload):
    first = _login(client, make_payload)
    client.post(REFRESH, json={"refresh_token": first["refresh_token"]})
    response = client.post(REFRESH, json={"refresh_token": first["refresh_token"]})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


def test_reusing_a_used_token_revokes_the_whole_family(client, make_payload):
    first = _login(client, make_payload)
    second = client.post(REFRESH, json={"refresh_token": first["refresh_token"]}).json()
    client.post(REFRESH, json={"refresh_token": first["refresh_token"]})  # replay
    response = client.post(REFRESH, json={"refresh_token": second["refresh_token"]})
    assert response.status_code == 401


def test_refresh_rejects_unknown_token(client):
    assert client.post(REFRESH, json={"refresh_token": "nope"}).status_code == 401


def test_refresh_rejects_expired_token(client, make_payload, db):
    body = _login(client, make_payload)
    stored = db.scalar(select(RefreshToken))
    stored.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db.commit()
    assert client.post(REFRESH, json={"refresh_token": body["refresh_token"]}).status_code == 401


def test_logout_revokes_refresh_token(client, make_payload):
    body = _login(client, make_payload)
    assert client.post(LOGOUT, json={"refresh_token": body["refresh_token"]}).status_code == 204
    assert client.post(REFRESH, json={"refresh_token": body["refresh_token"]}).status_code == 401


def test_logout_is_idempotent_for_unknown_token(client):
    assert client.post(LOGOUT, json={"refresh_token": "nope"}).status_code == 204


def test_access_token_cannot_be_used_as_refresh_token(client, make_payload):
    body = _login(client, make_payload)
    assert client.post(REFRESH, json={"refresh_token": body["access_token"]}).status_code == 401
