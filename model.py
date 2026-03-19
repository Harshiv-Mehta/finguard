from __future__ import annotations

from typing import Dict, Optional

import pandas as pd

try:
    from sklearn.linear_model import LogisticRegression
except ImportError:  # pragma: no cover
    LogisticRegression = None


FEATURE_COLUMNS = [
    "balance_before",
    "expense_amount",
    "monthly_needs",
    "savings_goal",
    "recent_expense_count",
    "category",
    "expense_type",
]


def predict_risky_probability(history: pd.DataFrame, candidate: Dict) -> Optional[float]:
    """Train a simple classifier from saved examples and predict risk probability."""
    if LogisticRegression is None:
        return None

    if history.empty or len(history) < 8:
        return None

    if "is_risky" not in history.columns or history["is_risky"].nunique() < 2:
        return None

    training_data = history[FEATURE_COLUMNS + ["is_risky"]].dropna().copy()
    if len(training_data) < 8 or training_data["is_risky"].nunique() < 2:
        return None

    x_train = pd.get_dummies(training_data[FEATURE_COLUMNS], columns=["category", "expense_type"])
    y_train = training_data["is_risky"].astype(int)

    model = LogisticRegression(max_iter=500)
    model.fit(x_train, y_train)

    candidate_df = pd.DataFrame([candidate], columns=FEATURE_COLUMNS)
    x_candidate = pd.get_dummies(candidate_df, columns=["category", "expense_type"])
    x_candidate = x_candidate.reindex(columns=x_train.columns, fill_value=0)

    return float(model.predict_proba(x_candidate)[0][1])
