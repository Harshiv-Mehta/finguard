from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionInput


def save_transaction(db: Session, payload: TransactionInput, analysis: dict) -> Transaction:
    transaction = Transaction(
        balance_before=payload.balance,
        expense_amount=payload.expense_amount,
        category=payload.category.value,
        expense_type=payload.expense_type.value,
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


def list_transactions(
    db: Session,
    *,
    limit: int = 10,
    offset: int = 0,
    category: str | None = None,
) -> list[Transaction]:
    query = db.query(Transaction).order_by(Transaction.created_at.desc())
    if category:
        query = query.filter(Transaction.category == category)
    return query.offset(offset).limit(limit).all()


def clear_transactions(db: Session) -> None:
    db.query(Transaction).delete()
    db.commit()
