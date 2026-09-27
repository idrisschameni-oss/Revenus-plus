from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


@router.post("/categories", response_model=schemas.CategoryOut, status_code=201)
def add_category(
    payload: schemas.CategoryCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exists = (
        db.query(models.ExpenseCategory)
        .filter(
            models.ExpenseCategory.user_id == current_user.id,
            models.ExpenseCategory.nom.ilike(payload.nom),
        )
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Cette catégorie existe déjà.")

    category = models.ExpenseCategory(
        user_id=current_user.id, nom=payload.nom, plafond=payload.plafond
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/categories", response_model=List[schemas.CategoryOut])
def list_categories(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.ExpenseCategory)
        .filter(models.ExpenseCategory.user_id == current_user.id)
        .all()
    )


@router.post("/items", response_model=schemas.ExpenseOut, status_code=201)
def add_expense(
    payload: schemas.ExpenseCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = models.Expense(
        user_id=current_user.id,
        categorie=payload.categorie,
        montant=round(payload.montant, 2),
        date=payload.date,
        description=payload.description,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/items", response_model=List[schemas.ExpenseOut])
def list_expenses(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Expense)
        .filter(models.Expense.user_id == current_user.id)
        .order_by(models.Expense.date)
        .all()
    )


@router.delete("/{expense_id}", status_code=204)
def delete_expense(
    expense_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = (
        db.query(models.Expense)
        .filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id)
        .first()
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Dépense introuvable.")
    db.delete(expense)
    db.commit()


@router.get("/summary", response_model=schemas.ExpenseSummary)
def summary(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    categories = (
        db.query(models.ExpenseCategory)
        .filter(models.ExpenseCategory.user_id == current_user.id)
        .all()
    )
    expenses = (
        db.query(models.Expense).filter(models.Expense.user_id == current_user.id).all()
    )

    totaux = {c.nom: 0.0 for c in categories}
    for e in expenses:
        totaux[e.categorie] = round(totaux.get(e.categorie, 0.0) + e.montant, 2)

    depassements = {}
    for c in categories:
        if c.plafond is not None:
            depasse = totaux.get(c.nom, 0.0) - c.plafond
            if depasse > 0:
                depassements[c.nom] = round(depasse, 2)

    return schemas.ExpenseSummary(
        total_general=round(sum(e.montant for e in expenses), 2),
        total_par_categorie=totaux,
        depassements=depassements,
    )
