from simulation import simulate_financial_impact


def test_simulation_flags_when_balance_drops_below_monthly_needs():
    result = simulate_financial_impact(balance=2000, expense_amount=800, monthly_needs=1500, savings_goal=1000)

    assert result["remaining_balance"] == 1200
    assert any("rent" in message or "bills" in message for message in result["impact_messages"])
