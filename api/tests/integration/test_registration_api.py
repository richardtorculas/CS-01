"""US-01 AC1 and AC4: registration rules and the data-minimal schema."""

from sqlalchemy import select

from app.models import Barangay, User

REGISTER = "/api/v1/auth/register"


def test_register_returns_created_resident_without_password(client, make_payload):
    response = client.post(REGISTER, json=make_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "juan@example.com"
    assert body["mobile"] == "+639171234567"
    assert body["role"] == "RESIDENT"
    assert body["email_verified"] is False
    assert not {"password", "password_hash"} & body.keys()
    assert "correct-horse" not in response.text
    assert "argon2" not in response.text


def test_register_stores_argon2_hash_not_plaintext(client, make_payload, db):
    client.post(REGISTER, json=make_payload())
    stored = db.scalar(select(User.password_hash))
    assert stored.startswith("$argon2")
    assert "correct-horse" not in stored


def test_register_conflict_when_email_exists_ignoring_case(client, make_payload):
    client.post(REGISTER, json=make_payload())
    response = client.post(
        REGISTER, json=make_payload(email="JUAN@Example.com", mobile="09179999999")
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EMAIL_ALREADY_REGISTERED"


def test_register_conflict_when_mobile_exists_in_another_format(client, make_payload):
    client.post(REGISTER, json=make_payload())
    response = client.post(
        REGISTER, json=make_payload(email="other@example.com", mobile="+63 917 123 4567")
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "MOBILE_ALREADY_REGISTERED"


def test_register_rejected_when_password_shorter_than_8(client, make_payload):
    response = client.post(REGISTER, json=make_payload(password="short7!"))
    assert response.status_code == 422
    fields = response.json()["error"]["details"]["fields"]
    assert [f["field"] for f in fields] == ["password"]
    assert "short7!" not in response.text


def test_register_accepts_password_of_exactly_8(client, make_payload):
    assert client.post(REGISTER, json=make_payload(password="12345678")).status_code == 201


def test_register_rejected_when_mobile_not_ph_format(client, make_payload):
    response = client.post(REGISTER, json=make_payload(mobile="12345"))
    assert response.status_code == 422
    assert response.json()["error"]["details"]["fields"][0]["field"] == "mobile"


def test_register_rejected_when_email_malformed(client, make_payload):
    assert client.post(REGISTER, json=make_payload(email="not-an-email")).status_code == 422


def test_register_rejected_when_barangay_unknown(client, make_payload):
    response = client.post(
        REGISTER, json=make_payload(barangay_id="00000000-0000-4000-8000-000000000000")
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "BARANGAY_NOT_FOUND"


def test_register_rejected_when_role_supplied(client, make_payload):
    response = client.post(REGISTER, json=make_payload(role="ADMIN"))
    assert response.status_code == 422


def test_register_rejects_extra_personal_fields(client, make_payload):
    for extra in ({"address": "1 Rizal St"}, {"birthdate": "1990-01-01"}, {"id_number": "123"}):
        assert client.post(REGISTER, json=make_payload(**extra)).status_code == 422


def test_users_table_holds_only_permitted_columns():
    """AC4: no address, birthdate or ID-number columns. Extend deliberately, never casually."""
    assert {c.name for c in User.__table__.columns} == {
        "id",
        "name",
        "mobile",
        "email",
        "barangay_id",
        "password_hash",
        "role",
        "email_verified_at",
        "created_at",
        "updated_at",
    }


def test_barangays_endpoint_lists_names_without_auth(client, barangay, db):
    db.add(Barangay(name="Barangay Dos"))
    db.commit()
    response = client.get("/api/v1/barangays")
    assert response.status_code == 200
    assert [b["name"] for b in response.json()] == ["Barangay Dos", "Barangay Uno"]
