from risk_engine import assess_transaction_risk


def test_high_risk_when_expense_exceeds_thirty_percent_and_is_shopping():
    result = assess_transaction_risk(
        balance=1000,
        expense_amount=400,
        category="Shopping",
        expense_type="Want",
        recent_expense_count=4,
        monthly_needs=700,
        savings_goal=500,
    )

    assert result["risk_level"] == "HIGH"
    assert result["risk_score"] >= 70
    assert result["alerts"]
