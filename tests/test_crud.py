import pytest
from src import crud, schemas
from src.models import Budget, MaterialEquipment, TechnicalSpec

def test_create_budget(db_session):
    # 創建測試數據
    budget_data = schemas.BudgetCreate(
        budget_code="TEST-001",
        name="Test Budget"
    )
    
    # 調用要測試的函數
    budget = crud.create_budget(db_session, budget_data)
    
    # 驗證結果
    assert budget.budget_code == "TEST-001"
    assert budget.name == "Test Budget"
    assert budget.id is not None

def test_get_budget(db_session):
    # 創建測試數據
    budget_data = schemas.BudgetCreate(
        budget_code="TEST-002",
        name="Another Test Budget"
    )
    created_budget = crud.create_budget(db_session, budget_data)
    
    # 調用要測試的函數
    budget = crud.get_budget(db_session, created_budget.id)
    
    # 驗證結果
    assert budget.id == created_budget.id
    assert budget.budget_code == "TEST-002"
    assert budget.name == "Another Test Budget"

def test_list_budgets(db_session):
    # 創建測試數據
    budget_data1 = schemas.BudgetCreate(
        budget_code="TEST-003",
        name="Budget 3"
    )
    budget_data2 = schemas.BudgetCreate(
        budget_code="TEST-004",
        name="Budget 4"
    )
    crud.create_budget(db_session, budget_data1)
    crud.create_budget(db_session, budget_data2)
    
    # 調用要測試的函數
    budgets = crud.list_budgets(db_session, limit=10)
    
    # 驗證結果
    assert len(budgets) >= 2  # 至少包含我們剛創建的兩個預算