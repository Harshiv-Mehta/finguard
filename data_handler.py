from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
TRANSACTIONS_FILE = BASE_DIR / "transactions.csv"

TRANSACTION_COLUMNS = [
    "timestamp",
    "balance_before",
    "expense_amount",
    "category",
    "expense_type",
    "monthly_needs",
    "savings_goal",
    "remaining_balance",
    "recent_expense_count",
    "risk_score",
    "risk_level",
    "is_risky",
    "message",
]


def ensure_storage() -> Path:
    """Create a CSV file with the expected headers if it does not exist."""
    if not TRANSACTIONS_FILE.exists():
        pd.DataFrame(columns=TRANSACTION_COLUMNS).to_csv(TRANSACTIONS_FILE, index=False)
    return TRANSACTIONS_FILE


def load_transactions() -> pd.DataFrame:
    """Load saved transaction history into a dataframe."""
    csv_path = ensure_storage()
    df = pd.read_csv(csv_path)

    if df.empty:
        return pd.DataFrame(columns=TRANSACTION_COLUMNS)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    numeric_columns = [
        "balance_before",
        "expense_amount",
        "monthly_needs",
        "savings_goal",
        "remaining_balance",
        "recent_expense_count",
        "risk_score",
        "is_risky",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    df["category"] = df["category"].fillna("Other")
    df["expense_type"] = df["expense_type"].fillna("Need")
    df["risk_level"] = df["risk_level"].fillna("LOW")
    df["message"] = df["message"].fillna("")
    return df


def save_transaction(transaction: Dict) -> None:
    """Append a new transaction row to the CSV file."""
    ensure_storage()
    row = pd.DataFrame([transaction], columns=TRANSACTION_COLUMNS)
    row.to_csv(TRANSACTIONS_FILE, mode="a", header=False, index=False)


def reset_transactions() -> None:
    """Reset the CSV storage to headers only."""
    pd.DataFrame(columns=TRANSACTION_COLUMNS).to_csv(TRANSACTIONS_FILE, index=False)


def count_recent_expenses(df: pd.DataFrame, days: int = 3) -> int:
    """Count recent transactions to help detect impulsive spending patterns."""
    if df.empty or "timestamp" not in df.columns:
        return 0

    timestamps = pd.to_datetime(df["timestamp"], errors="coerce").dropna()
    if timestamps.empty:
        return 0

    cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
    return int((timestamps >= cutoff).sum())
