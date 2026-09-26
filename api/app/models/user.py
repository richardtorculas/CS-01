import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import UserRole
from app.db.base import Base
from app.models.mixins import TimestampMixin, UuidPrimaryKeyMixin


class User(UuidPrimaryKeyMixin, TimestampMixin, Base):
    """Personal data is limited to name, mobile, email and barangay (RA 10173 proportionality).

    Do not add address, birthdate or ID-number columns.
    """

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(120))
    mobile: Mapped[str] = mapped_column(String(16), unique=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    barangay_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("barangays.id"), index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), default=UserRole.RESIDENT
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @property
    def email_verified(self) -> bool:
        return self.email_verified_at is not None
