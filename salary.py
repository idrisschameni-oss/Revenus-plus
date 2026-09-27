from statistics import mean
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db
from ..simulators import salary_calc

router = APIRouter(prefix="/api/salary", tags=["salary"])


@router.post("/weeks", response_model=schemas.SalaryWeekOut, status_code=201)
def add_week(
    payload: schemas.SalaryWeekCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        brut = salary_calc.calculer_brut(
            salaire_brut=payload.salaire_brut,
            heures=payload.heures,
            taux_horaire=payload.taux_horaire,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    resultat = salary_calc.calculer_semaine(
        brut=brut,
        taux_cotisations=payload.taux_cotisations,
        taux_impot=payload.taux_impot,
        autres_retenues=payload.autres_retenues,
    )

    week = models.SalaryWeek(
        user_id=current_user.id,
        date=payload.date,
        brut=brut,
        cotisations=resultat["cotisations"],
        impot=resultat["impot"],
        autres_retenues=round(payload.autres_retenues, 2),
        devise=payload.devise,
    )
    db.add(week)
    db.commit()
    db.refresh(week)
    return week


@router.get("/weeks", response_model=List[schemas.SalaryWeekOut])
def list_weeks(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.SalaryWeek)
        .filter(models.SalaryWeek.user_id == current_user.id)
        .order_by(models.SalaryWeek.date)
        .all()
    )


@router.delete("/weeks/{week_id}", status_code=204)
def delete_week(
    week_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    week = (
        db.query(models.SalaryWeek)
        .filter(models.SalaryWeek.id == week_id, models.SalaryWeek.user_id == current_user.id)
        .first()
    )
    if not week:
        raise HTTPException(status_code=404, detail="Semaine introuvable.")
    db.delete(week)
    db.commit()


@router.get("/summary", response_model=schemas.SalarySummary)
def summary(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    weeks = (
        db.query(models.SalaryWeek).filter(models.SalaryWeek.user_id == current_user.id).all()
    )
    if not weeks:
        return schemas.SalarySummary(
            nb_semaines=0, total_brut=0, total_charges=0, total_net=0, moyenne_net=0
        )
    return schemas.SalarySummary(
        nb_semaines=len(weeks),
        total_brut=round(sum(w.brut for w in weeks), 2),
        total_charges=round(sum(w.charges for w in weeks), 2),
        total_net=round(sum(w.net for w in weeks), 2),
        moyenne_net=round(mean(w.net for w in weeks), 2),
    )
