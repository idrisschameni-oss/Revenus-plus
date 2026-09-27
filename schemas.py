from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------- Auth ----------
class UserCreate(BaseModel):
    prenom: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=6)
    referral_code: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    prenom: str
    email: EmailStr
    referral_code: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Parrainage ----------
class ReferralInfo(BaseModel):
    referral_code: str
    referral_link: str
    filleuls_count: int


# ---------- Salaire ----------
class SalaryWeekCreate(BaseModel):
    date: date
    salaire_brut: Optional[float] = None
    heures: Optional[float] = None
    taux_horaire: Optional[float] = None
    taux_cotisations: float = 0
    taux_impot: float = 0
    autres_retenues: float = 0
    devise: str = "EUR"


class SalaryWeekOut(BaseModel):
    id: int
    date: date
    brut: float
    cotisations: float
    impot: float
    autres_retenues: float
    devise: str
    charges: float
    net: float
    model_config = ConfigDict(from_attributes=True)


class SalarySummary(BaseModel):
    nb_semaines: int
    total_brut: float
    total_charges: float
    total_net: float
    moyenne_net: float


# ---------- Dépenses ----------
class CategoryCreate(BaseModel):
    nom: str = Field(min_length=1)
    plafond: Optional[float] = None


class CategoryOut(BaseModel):
    id: int
    nom: str
    plafond: Optional[float]
    model_config = ConfigDict(from_attributes=True)


class ExpenseCreate(BaseModel):
    categorie: str = Field(min_length=1)
    montant: float
    date: date
    description: Optional[str] = None


class ExpenseOut(BaseModel):
    id: int
    categorie: str
    montant: float
    date: date
    description: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class ExpenseSummary(BaseModel):
    total_general: float
    total_par_categorie: dict
    depassements: dict


# ---------- Transactions (calculs sans état) ----------
class FeeRequest(BaseModel):
    montant: float
    frais_fixe: float = 0
    taux_pourcentage: float = 0
    frais_min: Optional[float] = None
    frais_max: Optional[float] = None


class FeeResult(BaseModel):
    montant_initial: float
    frais_fixe: float
    frais_pourcentage: float
    frais_total: float
    montant_final: float


class ConversionRequest(BaseModel):
    montant: float
    taux_change: float
    frais_conversion_pct: float = 0


class ConversionResult(BaseModel):
    montant_initial: float
    taux_change: float
    montant_converti_brut: float
    frais_conversion: float
    montant_final: float


# ---------- Administration ----------
class AdminUserOut(BaseModel):
    id: int
    prenom: str
    email: EmailStr
    referral_code: str
    referred_by: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ActivityOut(BaseModel):
    id: int
    user_id: Optional[int]
    method: str
    path: str
    status_code: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AdminUserDetail(BaseModel):
    user: AdminUserOut
    salaries: list[SalaryWeekOut]
    expenses: list[ExpenseOut]


class AdminOverview(BaseModel):
    user_count: int
    salary_count: int
    expense_count: int
    salary_total: float
    expense_total: float
    activity_count: int
    recent_users: list[AdminUserOut]
