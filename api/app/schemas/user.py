import uuid
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from app.core.enums import UserRole
from app.core.validators import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    normalize_email,
    normalize_ph_mobile,
)
from app.schemas.common import UtcDatetime

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)]
Mobile = Annotated[str, AfterValidator(normalize_ph_mobile)]
Email = Annotated[EmailStr, AfterValidator(normalize_email)]
Password = Annotated[str, Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)]


class RegisterRequest(BaseModel):
    # No role field: public signup always creates a resident. Extras are rejected, not ignored.
    model_config = ConfigDict(extra="forbid")

    name: Name
    mobile: Mobile
    email: Email
    barangay_id: uuid.UUID
    password: Password


class CreateOfficialRequest(BaseModel):
    """Admin-only. Officials are never created through public registration."""

    model_config = ConfigDict(extra="forbid")

    role: Literal[UserRole.PERSONNEL, UserRole.ADMIN]
    name: Name
    mobile: Mobile
    email: Email
    barangay_id: uuid.UUID
    password: Password


class UpdateProfileRequest(BaseModel):
    """Partial update. Role and email are deliberately absent and rejected if sent."""

    model_config = ConfigDict(extra="forbid")

    name: Name | None = None
    mobile: Mobile | None = None
    barangay_id: uuid.UUID | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    mobile: str
    email: str
    barangay_id: uuid.UUID
    role: UserRole
    email_verified: bool
    created_at: UtcDatetime
