from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ExpenseCategory(str, Enum):
    FOOD = "Food"
    SHOPPING = "Shopping"
    BILLS = "Bills"
    TRAVEL = "Travel"
    ENTERTAINMENT = "Entertainment"
    HEALTH = "Health"
    EDUCATION = "Education"
    OTHER = "Other"


class ExpenseType(str, Enum):
    NEED = "Need"
    WANT = "Want"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TransactionInput(BaseModel):
    balance: float = Field(gt=0)
    expense_amount: float = Field(gt=0)
    category: ExpenseCategory
    expense_type: ExpenseType
    monthly_needs: float = Field(ge=0)
    savings_goal: float = Field(ge=0)


class AnalysisResponse(BaseModel):
    risk_score: int
    risk_level: RiskLevel
    message: str
    alerts: list[str]
    remaining_balance: float
    impact_messages: list[str]
    needs_gap: float
    savings_gap: float
    recommendation: str
    recent_expense_count: int
    ml_probability: float | None = None


class TransactionResponse(BaseModel):
    id: int
    created_at: datetime
    balance_before: float
    expense_amount: float
    category: ExpenseCategory
    expense_type: ExpenseType
    monthly_needs: float
    savings_goal: float
    remaining_balance: float
    recent_expense_count: int
    risk_score: int
    risk_level: RiskLevel
    is_risky: int
    message: str

    model_config = {"from_attributes": True}


class CategoryBreakdownItem(BaseModel):
    category: str
    amount: float


class BalanceTimelineItem(BaseModel):
    label: str
    balance: float


class DashboardResponse(BaseModel):
    total_transactions: int
    total_spending: float
    average_expense: float
    risky_share: float
    latest_balance: float
    top_category: str
    category_breakdown: list[CategoryBreakdownItem]
    balance_timeline: list[BalanceTimelineItem]
    recent_transactions: list[TransactionResponse]
