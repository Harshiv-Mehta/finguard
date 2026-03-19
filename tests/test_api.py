from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyze_endpoint_returns_risk_payload():
    response = client.post(
        "/api/analyze",
        json={
            "balance": 5000,
            "expense_amount": 1500,
            "category": "Shopping",
            "expense_type": "Want",
            "monthly_needs": 2500,
            "savings_goal": 1500,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "risk_level" in payload
    assert "remaining_balance" in payload
