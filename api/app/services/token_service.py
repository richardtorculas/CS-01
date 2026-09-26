import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import get_settings
from app.core.exceptions import InvalidRefreshTokenError
from app.models import RefreshToken, User


def _as_utc(value: datetime) -> datetime:
    # SQLite returns naive datetimes; they are stored as UTC.
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def issue_token_pair(
    db: Session, user: User, *, family_id: uuid.UUID | None = None
) -> tuple[str, str]:
    """Return (access_token, refresh_token). A new login starts a new token family."""
    refresh_token = security.generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            family_id=family_id or uuid.uuid4(),
            token_hash=security.hash_refresh_token(refresh_token),
            expires_at=datetime.now(UTC) + timedelta(days=get_settings().refresh_token_days),
        )
    )
    db.commit()
    return security.create_access_token(user.id), refresh_token


def _revoke_family(db: Session, family_id: uuid.UUID) -> None:
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )
    db.commit()


def _find(db: Session, raw_token: str) -> RefreshToken | None:
    digest = security.hash_refresh_token(raw_token)
    return db.scalar(select(RefreshToken).where(RefreshToken.token_hash == digest))


def rotate(db: Session, raw_token: str) -> tuple[str, str]:
    """Exchange a refresh token for a new pair; the presented token can never be used again.

    Presenting an already-used token means it may have been stolen, so the whole family
    is revoked and the legitimate holder must log in again.
    """
    stored = _find(db, raw_token)
    if stored is None or stored.revoked_at is not None:
        raise InvalidRefreshTokenError
    if _as_utc(stored.expires_at) <= datetime.now(UTC):
        raise InvalidRefreshTokenError

    # Atomic claim: of two concurrent requests with the same token, only one updates a row.
    claimed = db.execute(
        update(RefreshToken)
        .where(RefreshToken.id == stored.id, RefreshToken.used_at.is_(None))
        .values(used_at=datetime.now(UTC))
    )
    if claimed.rowcount == 0:
        _revoke_family(db, stored.family_id)
        raise InvalidRefreshTokenError

    user = db.get(User, stored.user_id)
    if user is None:
        db.rollback()
        raise InvalidRefreshTokenError
    # issue_token_pair commits, which also commits the claim above.
    return issue_token_pair(db, user, family_id=stored.family_id)


def revoke(db: Session, raw_token: str) -> None:
    """Log out: revoke the token's whole family. Unknown tokens are ignored (idempotent)."""
    stored = _find(db, raw_token)
    if stored is not None:
        _revoke_family(db, stored.family_id)
