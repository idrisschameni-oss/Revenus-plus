from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..config import settings
from ..database import get_db

router = APIRouter(prefix="/api/admin", tags=["admin"])


def is_admin_user(user: models.User) -> bool:
    emails = {e.strip().lower() for e in settings.ADMIN_EMAILS if e.strip()}
    # If ADMIN_EMAILS is configured, it is authoritative. Otherwise the first
    # registered account (id=1) is the bootstrap administrator for this demo.
    return user.email.lower() in emails if emails else user.id == 1


def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Accès administrateur requis.")
    return current_user


@router.get("/me")
def admin_me(current_user: models.User = Depends(get_current_user)):
    return {"is_admin": is_admin_user(current_user)}


@router.get("/overview", response_model=schemas.AdminOverview)
def overview(
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user_count = db.query(models.User).count()
    salary_count = db.query(models.SalaryWeek).count()
    expense_count = db.query(models.Expense).count()
    salary_total = db.query(func.coalesce(func.sum(models.SalaryWeek.brut), 0)).scalar() or 0
    expense_total = db.query(func.coalesce(func.sum(models.Expense.montant), 0)).scalar() or 0
    activity_count = db.query(models.ActivityLog).count()
    recent_users = db.query(models.User).order_by(models.User.created_at.desc()).limit(8).all()
    return schemas.AdminOverview(
        user_count=user_count,
        salary_count=salary_count,
        expense_count=expense_count,
        salary_total=round(float(salary_total), 2),
        expense_total=round(float(expense_total), 2),
        activity_count=activity_count,
        recent_users=[schemas.AdminUserOut.model_validate(u) for u in recent_users],
    )


@router.get("/users", response_model=List[schemas.AdminUserOut])
def users(
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    result = []
    for u in db.query(models.User).order_by(models.User.created_at.desc()).all():
        result.append(schemas.AdminUserOut.model_validate(u))
    return result


@router.get("/users/{user_id}", response_model=schemas.AdminUserDetail)
def user_detail(
    user_id: int,
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    u = db.query(models.User).filter(models.User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    salaries = db.query(models.SalaryWeek).filter(models.SalaryWeek.user_id == user_id).order_by(models.SalaryWeek.date.desc()).all()
    expenses = db.query(models.Expense).filter(models.Expense.user_id == user_id).order_by(models.Expense.date.desc()).all()
    return schemas.AdminUserDetail(
        user=schemas.AdminUserOut.model_validate(u),
        salaries=[schemas.SalaryWeekOut.model_validate(x) for x in salaries],
        expenses=[schemas.ExpenseOut.model_validate(x) for x in expenses],
    )


@router.get("/activities", response_model=List[schemas.ActivityOut])
def activities(
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
):
    rows = db.query(models.ActivityLog).order_by(models.ActivityLog.created_at.desc()).limit(limit).all()
    return [schemas.ActivityOut.model_validate(x) for x in rows]


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte administrateur.")
    u = db.query(models.User).filter(models.User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    db.delete(u)
    db.commit()
