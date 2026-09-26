"""US-01 AC2: email verification gates the first report."""

from fastapi import Depends

from app.models import User
from app.routers.deps import require_verified_email

REGISTER = "/api/v1/auth/register"
VERIFY = "/api/v1/auth/verify-email"
RESEND = "/api/v1/auth/resend-verification"


def test_register_sends_verification_email_with_token_link(client, make_payload, email_sender):
    client.post(REGISTER, json=make_payload())
    assert len(email_sender.sent) == 1
    assert email_sender.sent[0]["to"] == "juan@example.com"
    assert "ugnay://verify-email?token=" in email_sender.sent[0]["text"]


def test_register_still_succeeds_when_email_delivery_fails(client, make_payload, email_sender):
    email_sender.fail = True
    assert client.post(REGISTER, json=make_payload()).status_code == 201


def test_verify_email_marks_account_verified(client, make_payload, email_sender, auth_headers):
    token = email_sender.last_token()
    response = client.post(VERIFY, json={"token": token})
    assert response.status_code == 200
    assert response.json()["email_verified"] is True
    assert client.get("/api/v1/me", headers=auth_headers).json()["email_verified"] is True


def test_verify_email_is_idempotent(client, make_payload, email_sender, auth_headers):
    token = email_sender.last_token()
    assert client.post(VERIFY, json={"token": token}).status_code == 200
    assert client.post(VERIFY, json={"token": token}).status_code == 200


def test_verify_email_rejected_when_token_invalid(client):
    response = client.post(VERIFY, json={"token": "garbage"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_VERIFICATION_TOKEN"


def test_verify_email_rejected_when_token_is_an_access_token(client, auth_headers):
    access_token = auth_headers["Authorization"].removeprefix("Bearer ")
    assert client.post(VERIFY, json={"token": access_token}).status_code == 400


def test_resend_verification_sends_another_email_when_unverified(
    client, auth_headers, email_sender
):
    before = len(email_sender.sent)
    assert client.post(RESEND, headers=auth_headers).status_code == 202
    assert len(email_sender.sent) == before + 1


def test_resend_verification_sends_nothing_when_already_verified(
    client, auth_headers, email_sender
):
    client.post(VERIFY, json={"token": email_sender.last_token()})
    before = len(email_sender.sent)
    assert client.post(RESEND, headers=auth_headers).status_code == 202
    assert len(email_sender.sent) == before


def test_resend_verification_requires_authentication(client):
    assert client.post(RESEND).status_code == 401


def _add_gated_route(app) -> None:
    @app.post("/test-only/submit")
    def submit(user: User = Depends(require_verified_email)) -> dict:
        return {"ok": True}


def test_report_gate_blocks_unverified_email_then_allows_after_verification(
    app, client, auth_headers, email_sender
):
    _add_gated_route(app)
    blocked = client.post("/test-only/submit", headers=auth_headers)
    assert blocked.status_code == 403
    assert blocked.json()["error"]["code"] == "EMAIL_NOT_VERIFIED"

    client.post(VERIFY, json={"token": email_sender.last_token()})
    assert client.post("/test-only/submit", headers=auth_headers).status_code == 200


def test_report_gate_requires_authentication(app, client):
    _add_gated_route(app)
    assert client.post("/test-only/submit").status_code == 401
