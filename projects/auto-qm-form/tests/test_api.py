import pytest
from src.main import app
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_budget(client):
    budget_data = {
        "budget_code": "API-001",
        "name": "API Test Budget"
    }
    response = client.post("/budgets/", json=budget_data)
    assert response.status_code == 200
    data = response.json()
    assert data["budget_code"] == "API-001"
    assert data["name"] == "API Test Budget"
    assert "id" in data

def test_get_budget(client):
    # 先創建一個預算
    budget_data = {
        "budget_code": "API-002",
        "name": "Another API Test Budget"
    }
    create_response = client.post("/budgets/", json=budget_data)
    created_budget = create_response.json()
    
    # 然後獲取它
    response = client.get(f"/budgets/{created_budget['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_budget["id"]
    assert data["budget_code"] == "API-002"
    assert data["name"] == "Another API Test Budget"