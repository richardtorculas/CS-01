import os
import re
import uuid
from collections.abc import Iterator

# Must be set before app modules read settings.
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET", "test-secret-test-secret-test-secret-123")
os.environ["BREVO_API_KEY"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, delete  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.enums import UserRole  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import create_app  # noqa: E402
from app.models import Barangay, RefreshToken, User  # noqa: E402
from app.services.email_service import get_email_sender  # noqa: E402

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite://")


class FakeEmailSender:
    def __init__(self) -> None:
        self.sent: list[dict[str, str]] = []
        self.fail = False

    def send(self, *, to_email: str, to_name: str, subject: str, text: str) -> None:
        if self.fail:
            raise RuntimeError("provider down")
        self.sent.append({"to": to_email, "subject": subject, "text": text})

    def last_token(self) -> str:
        match = re.search(r"token=(\S+)", self.sent[-1]["text"])
        assert match, "no token in email"
        return match.group(1)


@pytest.fixture(scope="session")
def engine():
    if TEST_DATABASE_URL.startswith("sqlite"):
        engine = create_engine(
            TEST_DATABASE_URL, poolclass=StaticPool, connect_args={"check_same_thread": False}
        )
    else:
        engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db(engine) -> Iterator[Session]:
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as session:
        yield session
    with factory() as cleanup:
        cleanup.execute(delete(RefreshToken))
        cleanup.execute(delete(User))
        cleanup.execute(delete(Barangay))
        cleanup.commit()


@pytest.fixture
def email_sender() -> FakeEmailSender:
    return FakeEmailSender()


@pytest.fixture
def app(db, email_sender):
    application = create_app()
    application.dependency_overrides[get_db] = lambda: db
    application.dependency_overrides[get_email_sender] = lambda: email_sender
    return application


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


@pytest.fixture
def barangay(db) -> Barangay:
    row = Barangay(name="Barangay Uno")
    db.add(row)
    db.commit()
    return row


def registration_payload(default_barangay_id: uuid.UUID, **overrides) -> dict:
    payload = {
        "name": "Juan Dela Cruz",
        "mobile": "09171234567",
        "email": "juan@example.com",
        "barangay_id": str(default_barangay_id),
        "password": "correct-horse",
    }
    return payload | overrides


@pytest.fixture
def make_payload(barangay):
    return lambda **overrides: registration_payload(barangay.id, **overrides)


@pytest.fixture
def auth_headers(client, make_payload):
    """Register a resident and return Authorization headers for them."""
    payload = make_payload()
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    login = client.post(
        "/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]}
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


OFFICIAL_PASSWORD = "official-password"


@pytest.fixture
def make_official_headers(client, db, barangay):
    """Insert a PERSONNEL or ADMIN user directly (the API has no public path) and log in."""

    def make(role: UserRole) -> dict[str, str]:
        email = f"{role.value.lower()}@example.com"
        db.add(
            User(
                name=f"Test {role.value}",
                mobile="+63917000" + ("1111" if role is UserRole.ADMIN else "2222"),
                email=email,
                barangay_id=barangay.id,
                password_hash=hash_password(OFFICIAL_PASSWORD),
                role=role,
            )
        )
        db.commit()
        login = client.post(
            "/api/v1/auth/login", json={"email": email, "password": OFFICIAL_PASSWORD}
        )
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

    return make
