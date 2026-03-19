from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TransactionInput(BaseModel):
    balance: float = Field(gt=0)
    expense_amount: float = Field(gt=0)
    category: str
    expense_type: str
    monthly_needs: float = Field(ge=0)
    savings_goal: float = Field(ge=0)


class AnalysisResponse(BaseModel):
    risk_score: int
    risk_level: str
    message: str
    alerts: List[str]
    remaining_balance: float
    impact_messages: List[str]
    needs_gap: float
    savings_gap: float
    recommendation: str
    recent_expense_count: int
    ml_probability: Optional[float] = None


class TransactionResponse(BaseModel):
    id: int
    created_at: datetime
    balance_before: float
    expense_amount: float
    category: str
    expense_type: str
    monthly_needs: float
    savings_goal: float
    remaining_balance: float
    recent_expense_count: int
    risk_score: int
    risk_level: str
    is_risky: int
    message: str

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    total_transactions: int
    total_spending: float
    average_expense: float
    risky_share: float
    latest_balance: float
    top_category: str
    category_breakdown: List[dict]
    balance_timeline: List[dict]
    recent_transactions: List[TransactionResponse]
