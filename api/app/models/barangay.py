from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UuidPrimaryKeyMixin


class Barangay(UuidPrimaryKeyMixin, TimestampMixin, Base):
    """Minimal for now; US-07 adds the boundary geometry."""

    __tablename__ = "barangays"

    name: Mapped[str] = mapped_column(String(120), unique=True)
