"""US-02 AC2/AC4: 3 roles x every protected route.

Routes are discovered from the app, so a new route with no declared policy fails
`test_every_route_has_a_declared_policy` until its access rule is added here.
"""

import re
import uuid

import pytest
from fastapi import APIRouter, Depends

from app.core.enums import UserRole
from app.routers.deps import require_admin, require_personnel

PUBLIC = "public"
ANY_ROLE = "any_role"
ADMIN_ONLY = "admin"
PERSONNEL_UP = "personnel"  # personnel and administrators (SECURITY.md: admin does everything)

_EXPLICIT_POLICIES: dict[tuple[str, str], str] = {
    ("POST", "/api/v1/auth/register"): PUBLIC,
    ("POST", "/api/v1/auth/login"): PUBLIC,
    ("POST", "/api/v1/auth/verify-email"): PUBLIC,
    ("POST", "/api/v1/auth/refresh"): PUBLIC,
    ("POST", "/api/v1/auth/logout"): PUBLIC,
    ("POST", "/api/v1/auth/resend-verification"): ANY_ROLE,
    ("GET", "/api/v1/barangays"): PUBLIC,
    ("GET", "/api/v1/me"): ANY_ROLE,
    ("PATCH", "/api/v1/me"): ANY_ROLE,
}
_FRAMEWORK_PATHS = {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}

ALLOWED_ROLES = {
    ANY_ROLE: set(UserRole),
    ADMIN_ONLY: {UserRole.ADMIN},
    PERSONNEL_UP: {UserRole.PERSONNEL, UserRole.ADMIN},
}


def _policy(method: str, path: str) -> str | None:
    if path.startswith("/api/v1/admin/"):
        return ADMIN_ONLY
    if path.startswith("/api/v1/personnel/"):
        return PERSONNEL_UP
    return _EXPLICIT_POLICIES.get((method, path))


def _endpoints(application) -> list[tuple[str, str]]:
    # The OpenAPI document is the stable view of routes across FastAPI versions.
    application.openapi_schema = None
    return sorted(
        (method.upper(), path)
        for path, operations in application.openapi()["paths"].items()
        for method in operations
    )


def _concrete(path: str) -> str:
    """Fill path parameters with random UUIDs."""
    return re.sub(r"\{[^}]+\}", lambda _: str(uuid.uuid4()), path)


@pytest.fixture
def rbac_app(app):
    """The real app plus probe routes: /personnel has no endpoints yet, and future admin
    routes (assign, score) must inherit the same guard as this probe."""
    for prefix, guard, method in (
        ("/api/v1/personnel", require_personnel, "GET"),
        ("/api/v1/admin", require_admin, "POST"),
    ):
        probe = APIRouter(prefix=prefix, dependencies=[Depends(guard)])
        probe.add_api_route("/probe", lambda: {"ok": True}, methods=[method])
        app.include_router(probe)
    return app


def test_every_route_has_a_declared_policy(rbac_app):
    undeclared = [
        endpoint
        for endpoint in _endpoints(rbac_app)
        if _policy(*endpoint) is None and endpoint[1] not in _FRAMEWORK_PATHS
    ]
    assert undeclared == []


def test_rbac_matrix_three_roles_on_every_protected_endpoint(
    rbac_app, client, auth_headers, make_official_headers
):
    tokens = {
        UserRole.RESIDENT: auth_headers,
        UserRole.PERSONNEL: make_official_headers(UserRole.PERSONNEL),
        UserRole.ADMIN: make_official_headers(UserRole.ADMIN),
    }
    protected = [e for e in _endpoints(rbac_app) if _policy(*e) not in (None, PUBLIC)]
    assert len(protected) >= 5

    for method, path in protected:
        policy, url = _policy(method, path), _concrete(path)
        assert client.request(method, url).status_code == 401, (method, path, "anonymous")
        for role, headers in tokens.items():
            status = client.request(method, url, headers=headers, json={}).status_code
            if role in ALLOWED_ROLES[policy]:
                assert status not in (401, 403), (method, path, role, status)
            else:
                assert status == 403, (method, path, role, status)


def test_forbidden_response_uses_the_standard_error_shape(rbac_app, client, auth_headers):
    response = client.post("/api/v1/admin/probe", headers=auth_headers, json={})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_role_changes_take_effect_without_a_new_token(rbac_app, client, db, make_official_headers):
    """The role is read from the database per request, not trusted from the token."""
    from sqlalchemy import select

    from app.models import User

    admin = make_official_headers(UserRole.ADMIN)
    assert client.post("/api/v1/admin/probe", headers=admin).status_code == 200
    db.scalar(select(User).where(User.role == UserRole.ADMIN)).role = UserRole.RESIDENT
    db.commit()
    assert client.post("/api/v1/admin/probe", headers=admin).status_code == 403
