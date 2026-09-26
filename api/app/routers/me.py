from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.routers.deps import get_current_user
from app.schemas.errors import ErrorResponse
from app.schemas.user import UpdateProfileRequest, UserResponse
from app.services import user_service

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=UserResponse, responses={401: {"model": ErrorResponse}})
def get_me(user: User = Depends(get_current_user)) -> User:
    return user


@router.patch(
    "",
    response_model=UserResponse,
    responses={401: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def update_me(
    payload: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    return user_service.update_profile(db, user, **payload.model_dump(exclude_none=True))
