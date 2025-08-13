from sqlalchemy.orm import Session
from sqlalchemy import select
from src import models
from src import schemas

# Generic helpers (可後續泛型化)

# MaterialEquipment
def create_material_equipment(db: Session, data: schemas.MaterialEquipmentCreate):
    obj = models.MaterialEquipment(**data.model_fields_set, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_material_equipment(db: Session, limit: int = 50):
    return db.execute(select(models.MaterialEquipment).limit(limit)).scalars().all()

def get_material_equipment(db: Session, item_id: int):
    return db.get(models.MaterialEquipment, item_id)

# Budget
def create_budget(db: Session, data: schemas.BudgetCreate):
    obj = models.Budget(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_budgets(db: Session, limit: int = 50):
    return db.execute(select(models.Budget).limit(limit)).scalars().all()

def get_budget(db: Session, item_id: int):
    return db.get(models.Budget, item_id)

# TechnicalSpec
def create_technical_spec(db: Session, data: schemas.TechnicalSpecCreate):
    obj = models.TechnicalSpec(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_technical_specs(db: Session, limit: int = 50):
    return db.execute(select(models.TechnicalSpec).limit(limit)).scalars().all()

def get_technical_spec(db: Session, item_id: int):
    return db.get(models.TechnicalSpec, item_id)
