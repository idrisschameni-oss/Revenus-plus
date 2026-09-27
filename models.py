from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    prenom = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    referral_code = Column(String, unique=True, index=True, nullable=False)
    referred_by = Column(String, ForeignKey("users.referral_code"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    salary_weeks = relationship("SalaryWeek", back_populates="owner", cascade="all, delete-orphan")
    expense_categories = relationship("ExpenseCategory", back_populates="owner", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="owner", cascade="all, delete-orphan")


class SalaryWeek(Base):
    __tablename__ = "salary_weeks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    brut = Column(Float, nullable=False)
    cotisations = Column(Float, nullable=False)
    impot = Column(Float, nullable=False)
    autres_retenues = Column(Float, nullable=False, default=0)
    devise = Column(String, default="EUR")

    owner = relationship("User", back_populates="salary_weeks")

    @property
    def charges(self) -> float:
        return round(self.cotisations + self.impot + self.autres_retenues, 2)

    @property
    def net(self) -> float:
        return round(self.brut - self.charges, 2)


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nom = Column(String, nullable=False)
    plafond = Column(Float, nullable=True)

    owner = relationship("User", back_populates="expense_categories")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    categorie = Column(String, nullable=False)
    montant = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=True)

    owner = relationship("User", back_populates="expenses")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    method = Column(String, nullable=False)
    path = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
