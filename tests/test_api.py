from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app


TEST_TRANSACTION = {
    "balance": 5000,
    "expense_amount": 1500,
    "category": "Shopping",
    "expense_type": "Want",
    "monthly_needs": 2500,
    "savings_goal": 1500,
}


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def register_and_login(client: TestClient, email: str, password: str = "supersecure123") -> None:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201


def test_protected_endpoints_require_login(client: TestClient):
    response = client.post("/api/analyze", json=TEST_TRANSACTION)

    assert response.status_code == 401
    assert response.json()["detail"] == "Please log in to continue."


def test_register_login_and_analyze_flow(client: TestClient):
    register_and_login(client, "user1@example.com")

    page_response = client.get("/")
    assert page_response.status_code == 200
    assert "Signed in as" in page_response.text
    assert "user1@example.com" in page_response.text

    response = client.post("/api/analyze", json=TEST_TRANSACTION)

    assert response.status_code == 200
    payload = response.json()
    assert "risk_level" in payload
    assert "remaining_balance" in payload


def test_transactions_are_isolated_by_user(client: TestClient):
    register_and_login(client, "user1@example.com")
    save_response = client.post("/api/transactions", json=TEST_TRANSACTION)
    assert save_response.status_code == 200

    dashboard_response = client.get("/api/dashboard")
    assert dashboard_response.status_code == 200
    assert dashboard_response.json()["total_transactions"] == 1

    logout_response = client.post("/api/auth/logout")
    assert logout_response.status_code == 204

    register_and_login(client, "user2@example.com")
    second_dashboard = client.get("/api/dashboard")
    second_transactions = client.get("/api/transactions")

    assert second_dashboard.status_code == 200
    assert second_dashboard.json()["total_transactions"] == 0
    assert second_transactions.status_code == 200
    assert second_transactions.json() == []
