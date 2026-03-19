from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionInput


def save_transaction(db: Session, user: User, payload: TransactionInput, analysis: dict) -> Transaction:
    transaction = Transaction(
        user_id=user.id,
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
    user: User,
    *,
    limit: int = 10,
    offset: int = 0,
    category: str | None = None,
) -> list[Transaction]:
    query = db.query(Transaction).filter(Transaction.user_id == user.id).order_by(Transaction.created_at.desc())
    if category:
        query = query.filter(Transaction.category == category)
    return query.offset(offset).limit(limit).all()


def clear_transactions(db: Session, user: User) -> None:
    db.query(Transaction).filter(Transaction.user_id == user.id).delete()
    db.commit()
