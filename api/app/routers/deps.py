from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationRequiredError, EmailNotVerifiedError
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


def require_verified_email(user: User = Depends(get_current_user)) -> User:
    """Gate for report submission (US-01 AC2). Combine with role checks once US-02 lands."""
    if not user.email_verified:
        raise EmailNotVerifiedError
    return user
