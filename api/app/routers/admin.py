from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.routers.deps import require_admin
from app.schemas.errors import ErrorResponse
from app.schemas.user import CreateOfficialRequest, UserResponse
from app.services import auth_service

# The router-level dependency guards every route added here, present and future.
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def create_official(payload: CreateOfficialRequest, db: Session = Depends(get_db)) -> User:
    # Admin-vouched accounts skip email verification, which only gates residents' reports.
    return auth_service.create_user(db, email_verified=True, **payload.model_dump())
