from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Barangay
from app.schemas.barangay import BarangayResponse
from app.services import user_service

router = APIRouter(prefix="/barangays", tags=["reference"])


@router.get("", response_model=list[BarangayResponse])
def list_barangays(db: Session = Depends(get_db)) -> list[Barangay]:
    """Public so the registration form can offer a choice before an account exists."""
    return user_service.list_barangays(db)
