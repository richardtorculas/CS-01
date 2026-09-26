from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.exceptions import (
    AuthenticationRequiredError,
    EmailNotVerifiedError,
    InsufficientRoleError,
)
from app.db.session import get_db
from app.models import User
from app.services import auth_service

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AuthenticationRequiredError
    return auth_service.get_user_from_access_token(db, credentials.credentials)


def require_roles(*allowed: UserRole) -> Callable[..., User]:
    """Dependency factory: 401 without a valid token, 403 when the role is not allowed."""

    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise InsufficientRoleError
        return user

    return dependency


# SECURITY.md: administrators can do everything personnel can.
require_admin = require_roles(UserRole.ADMIN)
require_personnel = require_roles(UserRole.PERSONNEL, UserRole.ADMIN)


def require_verified_email(user: User = Depends(get_current_user)) -> User:
    """Gate for report submission (US-01 AC2)."""
    if not user.email_verified:
        raise EmailNotVerifiedError
    return user
