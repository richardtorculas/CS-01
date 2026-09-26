from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models import User
from app.routers.deps import get_current_user
from app.schemas.auth import LoginRequest, TokenResponse, VerifyEmailRequest
from app.schemas.errors import ErrorResponse
from app.schemas.user import RegisterRequest, UserResponse
from app.services import auth_service, email_service
from app.services.email_service import EmailSender, get_email_sender

router = APIRouter(prefix="/auth", tags=["auth"])


def _queue_verification_email(background: BackgroundTasks, sender: EmailSender, user: User) -> None:
    background.add_task(
        email_service.send_verification_email,
        sender,
        user_id=user.id,
        to_email=user.email,
        to_name=user.name,
        token=auth_service.issue_verification_token(user),
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def register(
    payload: RegisterRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    sender: EmailSender = Depends(get_email_sender),
) -> User:
    user = auth_service.register_resident(db, **payload.model_dump())
    _queue_verification_email(background, sender, user)
    return user


@router.post("/login", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    user = auth_service.authenticate(db, email=payload.email, password=payload.password)
    return TokenResponse(
        access_token=auth_service.issue_access_token(user),
        expires_in=settings.access_token_minutes * 60,
    )


@router.post(
    "/verify-email", response_model=UserResponse, responses={400: {"model": ErrorResponse}}
)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)) -> User:
    return auth_service.verify_email(db, payload.token)


@router.post("/resend-verification", status_code=status.HTTP_202_ACCEPTED)
def resend_verification(
    background: BackgroundTasks,
    user: User = Depends(get_current_user),
    sender: EmailSender = Depends(get_email_sender),
) -> Response:
    if not user.email_verified:
        _queue_verification_email(background, sender, user)
    return Response(status_code=status.HTTP_202_ACCEPTED)
