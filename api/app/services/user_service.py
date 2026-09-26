import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BarangayNotFoundError, MobileAlreadyRegisteredError
from app.models import Barangay, User
from app.services.auth_service import duplicate_error_from


def list_barangays(db: Session) -> list[Barangay]:
    return list(db.scalars(select(Barangay).order_by(Barangay.name)))


def update_profile(
    db: Session,
    user: User,
    *,
    name: str | None = None,
    mobile: str | None = None,
    barangay_id: uuid.UUID | None = None,
) -> User:
    """Update the caller's own profile. Role is not a parameter, so it cannot be changed here."""
    if barangay_id is not None and db.get(Barangay, barangay_id) is None:
        raise BarangayNotFoundError
    if mobile is not None and mobile != user.mobile:
        taken = db.scalar(select(User.id).where(User.mobile == mobile, User.id != user.id))
        if taken is not None:
            raise MobileAlreadyRegisteredError

    for field, value in (("name", name), ("mobile", mobile), ("barangay_id", barangay_id)):
        if value is not None:
            setattr(user, field, value)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise duplicate_error_from(error) from error
    db.refresh(user)
    return user
