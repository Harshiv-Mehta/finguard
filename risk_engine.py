from __future__ import annotations

from typing import Dict, List


HIGH_SPEND_RATIO = 0.30
HIGH_RISK_CATEGORIES = {"Shopping", "Entertainment"}


def assess_transaction_risk(
    balance: float,
    expense_amount: float,
    category: str,
    expense_type: str,
    recent_expense_count: int,
    monthly_needs: float,
    savings_goal: float,
) -> Dict:
    """Score a transaction before it happens and explain the reasoning."""
    risk_score = 0
    reasons: List[str] = []
    alerts: List[str] = []

    if balance <= 0:
        return {
            "risk_score": 100,
            "risk_level": "HIGH",
            "message": "🚫 Your current balance is already too low for more spending.",
            "alerts": ["🚫 Transaction blocked in simulation because available balance is zero."],
        }

    remaining_balance = balance - expense_amount
    spend_ratio = expense_amount / balance if balance else 0

    if spend_ratio > HIGH_SPEND_RATIO:
        risk_score += 35
        reasons.append("⚠️ This expense is more than 30% of your current balance.")

    if category in HIGH_RISK_CATEGORIES:
        risk_score += 20
        reasons.append("🛍️ This category is often linked to non-essential spending.")

    if expense_type == "Want":
        risk_score += 10
        reasons.append("🤔 You marked this purchase as a want.")

    if recent_expense_count >= 3:
        risk_score += 20
        reasons.append("⚡ This looks like an impulsive purchase pattern.")
        alerts.append(f"🧠 You already logged {recent_expense_count} recent expenses.")

    if remaining_balance < monthly_needs:
        risk_score += 30
        reasons.append("🏠 This purchase may affect your ability to cover monthly needs.")

    if remaining_balance < savings_goal:
        risk_score += 15
        alerts.append("💸 You may fall below your savings goal.")

    budget_usage = (expense_amount / max(monthly_needs, 1)) * 100
    if budget_usage >= 60:
        alerts.append(f"📊 You have already spent about {budget_usage:.0f}% of your monthly needs budget.")

    if remaining_balance < 0:
        risk_score = 100
        reasons.append("🚨 This transaction would push your balance below zero.")

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "HIGH"
    elif risk_score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    default_message = {
        "LOW": "✅ This expense looks manageable based on your current plan.",
        "MEDIUM": "⚠️ This purchase deserves a second look before you proceed.",
        "HIGH": "🚨 High-risk transaction detected. Consider delaying this purchase.",
    }[risk_level]

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "message": reasons[0] if reasons else default_message,
        "alerts": alerts + reasons[1:],
    }
