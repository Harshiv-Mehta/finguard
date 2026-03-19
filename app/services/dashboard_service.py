from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.user import User
from app.services.analysis_service import transactions_to_dataframe


def build_dashboard(db: Session, user: User) -> dict:
    rows = (
        db.query(Transaction)
        .filter(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.asc())
        .all()
    )
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

    df = transactions_to_dataframe(rows)
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
    risky_share = float(df["is_risky"].mean() * 100)

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
