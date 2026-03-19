from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import RiskLevel, TransactionInput
from model import predict_risky_probability
from risk_engine import assess_transaction_risk
from simulation import simulate_financial_impact


def get_recent_expense_count(db: Session, user: User, days: int = 3) -> int:
    cutoff = datetime.now(UTC) - timedelta(days=days)
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == user.id, Transaction.created_at >= cutoff)
        .count()
    )


def build_recommendation(risk_level: str, remaining_balance: float, ml_probability: float | None) -> str:
    if remaining_balance < 0:
        return "Do not proceed because this purchase would overdraw your balance."
    if risk_level == RiskLevel.HIGH.value:
        return "Delay this purchase and focus on essential expenses first."
    if ml_probability is not None and ml_probability >= 0.65:
        return "Your transaction history suggests this purchase resembles earlier risky behavior."
    if risk_level == RiskLevel.MEDIUM.value:
        return "Wait a day before completing this purchase and revisit the decision."
    return "This transaction looks manageable if it still fits your goals."


def transactions_to_dataframe(rows: list[Transaction]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(
            columns=[
                "balance_before",
                "expense_amount",
                "monthly_needs",
                "savings_goal",
                "recent_expense_count",
                "category",
                "expense_type",
                "remaining_balance",
                "risk_score",
                "risk_level",
                "is_risky",
                "message",
                "created_at",
            ]
        )

    return pd.DataFrame(
        [
            {
                "balance_before": row.balance_before,
                "expense_amount": row.expense_amount,
                "monthly_needs": row.monthly_needs,
                "savings_goal": row.savings_goal,
                "recent_expense_count": row.recent_expense_count,
                "category": row.category,
                "expense_type": row.expense_type,
                "remaining_balance": row.remaining_balance,
                "risk_score": row.risk_score,
                "risk_level": row.risk_level,
                "is_risky": row.is_risky,
                "message": row.message,
                "created_at": row.created_at,
            }
            for row in rows
        ]
    )


def analyze_transaction(db: Session, user: User, payload: TransactionInput) -> dict:
    recent_expense_count = get_recent_expense_count(db, user)
    risk_result = assess_transaction_risk(
        balance=payload.balance,
        expense_amount=payload.expense_amount,
        category=payload.category.value,
        expense_type=payload.expense_type.value,
        recent_expense_count=recent_expense_count,
        monthly_needs=payload.monthly_needs,
        savings_goal=payload.savings_goal,
    )
    impact_result = simulate_financial_impact(
        balance=payload.balance,
        expense_amount=payload.expense_amount,
        monthly_needs=payload.monthly_needs,
        savings_goal=payload.savings_goal,
    )

    rows = (
        db.query(Transaction)
        .filter(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.asc())
        .all()
    )
    history_df = transactions_to_dataframe(rows)
    ml_probability = predict_risky_probability(
        history_df,
        {
            "balance_before": payload.balance,
            "expense_amount": payload.expense_amount,
            "monthly_needs": payload.monthly_needs,
            "savings_goal": payload.savings_goal,
            "recent_expense_count": recent_expense_count,
            "category": payload.category.value,
            "expense_type": payload.expense_type.value,
        },
    )

    return {
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
        "message": risk_result["message"],
        "alerts": risk_result["alerts"],
        "remaining_balance": impact_result["remaining_balance"],
        "impact_messages": impact_result["impact_messages"],
        "needs_gap": impact_result["needs_gap"],
        "savings_gap": impact_result["savings_gap"],
        "recommendation": build_recommendation(
            risk_result["risk_level"],
            impact_result["remaining_balance"],
            ml_probability,
        ),
        "recent_expense_count": recent_expense_count,
        "ml_probability": ml_probability,
    }
