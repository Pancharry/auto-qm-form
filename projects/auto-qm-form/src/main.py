from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db import Base, engine, get_db
from src import schemas, crud, models
from src.config import get_settings

settings = get_settings()

# 啟動時建立資料表（初期簡化，未來換 Alembic）# 已改用 Alembic migration
# def init_models():
#     Base.metadata.create_all(bind=engine)

init_models()

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.APP_ENV}

# MaterialEquipment Endpoints
@app.post("/material-equipment", response_model=schemas.MaterialEquipmentRead)
def create_material_equipment(payload: schemas.MaterialEquipmentCreate, db: Session = Depends(get_db)):
    return crud.create_material_equipment(db, payload)

@app.get("/material-equipment", response_model=list[schemas.MaterialEquipmentRead])
def list_material_equipment(limit: int = 50, db: Session = Depends(get_db)):
    return crud.list_material_equipment(db, limit)

@app.get("/material-equipment/{item_id}", response_model=schemas.MaterialEquipmentRead)
def get_material_equipment(item_id: int, db: Session = Depends(get_db)):
    obj = crud.get_material_equipment(db, item_id)
    if not obj:
        raise HTTPException(404, "Not found")
    return obj

# Budget
@app.post("/budgets", response_model=schemas.BudgetRead)
def create_budget(payload: schemas.BudgetCreate, db: Session = Depends(get_db)):
    return crud.create_budget(db, payload)

@app.get("/budgets", response_model=list[schemas.BudgetRead])
def list_budgets(limit: int = 50, db: Session = Depends(get_db)):
    return crud.list_budgets(db, limit)

@app.get("/budgets/{item_id}", response_model=schemas.BudgetRead)
def get_budget(item_id: int, db: Session = Depends(get_db)):
    obj = crud.get_budget(db, item_id)
    if not obj:
        raise HTTPException(404, "Not found")
    return obj

# Technical Spec
@app.post("/technical-specs", response_model=schemas.TechnicalSpecRead)
def create_technical_spec(payload: schemas.TechnicalSpecCreate, db: Session = Depends(get_db)):
    return crud.create_technical_spec(db, payload)

@app.get("/technical-specs", response_model=list[schemas.TechnicalSpecRead])
def list_technical_specs(limit: int = 50, db: Session = Depends(get_db)):
    return crud.list_technical_specs(db, limit)

@app.get("/technical-specs/{item_id}", response_model=schemas.TechnicalSpecRead)
def get_technical_spec(item_id: int, db: Session = Depends(get_db)):
    obj = crud.get_technical_spec(db, item_id)
    if not obj:
        raise HTTPException(404, "Not found")
    return obj
