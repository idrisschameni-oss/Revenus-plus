from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..config import settings
from ..database import get_db

router = APIRouter(prefix="/api/referral", tags=["referral"])


@router.get("/me", response_model=schemas.ReferralInfo)
def my_referral(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    count = (
        db.query(models.User)
        .filter(models.User.referred_by == current_user.referral_code)
        .count()
    )
    base_url = settings.FRONTEND_URL or str(request.base_url)
    link = f"{base_url.rstrip('/')}/?ref={current_user.referral_code}"
    return schemas.ReferralInfo(
        referral_code=current_user.referral_code,
        referral_link=link,
        filleuls_count=count,
    )
