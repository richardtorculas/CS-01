"""US-02 AC3: personnel and administrator accounts are created only by an administrator."""

from app.core.enums import UserRole

USERS = "/api/v1/admin/users"


def _payload(barangay, **overrides) -> dict:
    return {
        "role": "PERSONNEL",
        "name": "Maria Santos",
        "mobile": "09181112222",
        "email": "maria@example.com",
        "barangay_id": str(barangay.id),
        "password": "official-pass-1",
    } | overrides


def test_admin_creates_personnel_who_can_then_log_in(client, make_official_headers, barangay):
    admin = make_official_headers(UserRole.ADMIN)
    response = client.post(USERS, headers=admin, json=_payload(barangay))
    assert response.status_code == 201
    body = response.json()
    assert body["role"] == "PERSONNEL"
    assert "password" not in body and "password_hash" not in body
    login = client.post(
        "/api/v1/auth/login", json={"email": "maria@example.com", "password": "official-pass-1"}
    )
    assert login.status_code == 200


def test_admin_creates_another_administrator(client, make_official_headers, barangay):
    admin = make_official_headers(UserRole.ADMIN)
    response = client.post(USERS, headers=admin, json=_payload(barangay, role="ADMIN"))
    assert response.status_code == 201
    assert response.json()["role"] == "ADMIN"


def test_created_official_email_is_pre_verified(client, make_official_headers, barangay):
    admin = make_official_headers(UserRole.ADMIN)
    body = client.post(USERS, headers=admin, json=_payload(barangay)).json()
    assert body["email_verified"] is True


def test_creating_a_resident_through_admin_endpoint_is_rejected(
    client, make_official_headers, barangay
):
    admin = make_official_headers(UserRole.ADMIN)
    response = client.post(USERS, headers=admin, json=_payload(barangay, role="RESIDENT"))
    assert response.status_code == 422


def test_duplicate_email_rejected(client, make_official_headers, barangay):
    admin = make_official_headers(UserRole.ADMIN)
    client.post(USERS, headers=admin, json=_payload(barangay))
    response = client.post(USERS, headers=admin, json=_payload(barangay, mobile="09183334444"))
    assert response.status_code == 409


def test_public_registration_cannot_set_role(client, make_payload):
    response = client.post("/api/v1/auth/register", json=make_payload() | {"role": "ADMIN"})
    assert response.status_code == 422


def test_only_admin_route_creates_officials(app):
    creators = [
        path
        for path, operations in app.openapi()["paths"].items()
        if "post" in operations and path.endswith("/users")
    ]
    assert creators == [USERS]
