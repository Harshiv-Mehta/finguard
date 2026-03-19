from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from db_models import Transaction
from model import predict_risky_probability
from risk_engine import assess_transaction_risk
from simulation import simulate_financial_impact


def get_recent_expense_count(db: Session, days: int = 3) -> int:
    cutoff = datetime.utcnow() - timedelta(days=days)
    return db.query(Transaction).filter(Transaction.created_at >= cutoff).count()


def build_recommendation(risk_level: str, remaining_balance: float, ml_probability: Optional[float]) -> str:
    if remaining_balance < 0:
        return "Do not proceed because this purchase would overdraw your balance."
    if risk_level == "HIGH":
        return "Delay this purchase and focus on essential expenses first."
    if ml_probability is not None and ml_probability >= 0.65:
        return "Your transaction history suggests this purchase resembles earlier risky behavior."
    if risk_level == "MEDIUM":
        return "Wait a day before completing this purchase and revisit the decision."
    return "This transaction looks manageable if it still fits your goals."


def transactions_to_dataframe(db: Session) -> pd.DataFrame:
    rows = db.query(Transaction).order_by(Transaction.created_at.asc()).all()
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


def analyze_transaction(db: Session, payload) -> dict:
    recent_expense_count = get_recent_expense_count(db)
    risk_result = assess_transaction_risk(
        balance=payload.balance,
        expense_amount=payload.expense_amount,
        category=payload.category,
        expense_type=payload.expense_type,
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

    history_df = transactions_to_dataframe(db)
    ml_probability = predict_risky_probability(
        history_df,
        {
            "balance_before": payload.balance,
            "expense_amount": payload.expense_amount,
            "monthly_needs": payload.monthly_needs,
            "savings_goal": payload.savings_goal,
            "recent_expense_count": recent_expense_count,
            "category": payload.category,
            "expense_type": payload.expense_type,
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


def save_transaction(db: Session, payload, analysis: dict) -> Transaction:
    transaction = Transaction(
        balance_before=payload.balance,
        expense_amount=payload.expense_amount,
        category=payload.category,
        expense_type=payload.expense_type,
        monthly_needs=payload.monthly_needs,
        savings_goal=payload.savings_goal,
        remaining_balance=analysis["remaining_balance"],
        recent_expense_count=analysis["recent_expense_count"],
        risk_score=analysis["risk_score"],
        risk_level=analysis["risk_level"],
        is_risky=int(analysis["risk_level"] in {"MEDIUM", "HIGH"}),
        message=analysis["message"],
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def build_dashboard(db: Session) -> dict:
    rows = db.query(Transaction).order_by(Transaction.created_at.asc()).all()
    if not rows:
        return {
            "total_transactions": 0,
            "total_spending": 0.0,
            "average_expense": 0.0,
            "risky_share": 0.0,
            "latest_balance": 0.0,
            "top_category": "None yet",
            "category_breakdown": [],
            "balance_timeline": [],
            "recent_transactions": [],
        }

    df = transactions_to_dataframe(db)
    category_breakdown = (
        df.groupby("category", dropna=False)["expense_amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"expense_amount": "amount"})
        .to_dict(orient="records")
    )
    balance_timeline = [
        {"label": row.created_at.strftime("%d %b %H:%M"), "balance": row.remaining_balance}
        for row in rows
    ]

    top_category = df.groupby("category")["expense_amount"].sum().idxmax()
    risky_share = float(df["is_risky"].mean() * 100) if len(df) else 0.0

    return {
        "total_transactions": int(len(rows)),
        "total_spending": float(df["expense_amount"].sum()),
        "average_expense": float(df["expense_amount"].mean()),
        "risky_share": risky_share,
        "latest_balance": float(rows[-1].remaining_balance),
        "top_category": str(top_category),
        "category_breakdown": category_breakdown,
        "balance_timeline": balance_timeline,
        "recent_transactions": list(reversed(rows[-10:])),
    }
