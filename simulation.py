from __future__ import annotations

from typing import Dict, List


def simulate_financial_impact(
    balance: float,
    expense_amount: float,
    monthly_needs: float,
    savings_goal: float,
) -> Dict:
    """Estimate how this expense affects short-term resilience."""
    remaining_balance = balance - expense_amount
    impact_messages: List[str] = []

    if remaining_balance < 0:
        impact_messages.append("🚫 This purchase would overdraw your account.")
    elif remaining_balance < monthly_needs:
        impact_messages.append("🏠 This purchase may affect your ability to pay rent or bills.")
    else:
        impact_messages.append("✅ You still remain above your estimated monthly needs.")

    if remaining_balance < savings_goal:
        impact_messages.append("💰 You may fall below your savings goal.")
    else:
        impact_messages.append("🌱 Your savings target still looks protected.")

    return {
        "remaining_balance": remaining_balance,
        "needs_gap": remaining_balance - monthly_needs,
        "savings_gap": remaining_balance - savings_goal,
        "impact_messages": impact_messages,
    }
