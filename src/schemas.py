# src/schemas.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

# ---- Budget ----
class BudgetItemCreate(BaseModel):
    budget_id: str
    name: str
    type: str
    unit: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None

class BudgetItemRead(BudgetItemCreate):
    item_id: int
    class Config:
        orm_mode = True

# ---- Spec ----
class SpecificationItemCreate(BaseModel):
    spec_id: str
    item_name: str
    item_type: Optional[str] = None
    requirements: Optional[List[str]] = None
    standards: Optional[List[str]] = None
    testing_methods: Optional[List[str]] = None
    acceptance_criteria: Optional[List[str]] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None

class SpecificationItemRead(SpecificationItemCreate):
    id: int
    class Config:
        orm_mode = True

# ---- Quality Standard ----
class QualityStandardCreate(BaseModel):
    item_name: str
    item_type: str
    source: Optional[str] = None
    inspection_items: Optional[List[str]] = None
    inspection_methods: Optional[List[str]] = None
    acceptance_criteria: Optional[List[str]] = None
    frequency: Optional[str] = None
    responsible_party: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None

class QualityStandardRead(QualityStandardCreate):
    standard_id: int
    class Config:
        orm_mode = True

# ---- Template ----
class BlankTemplateCreate(BaseModel):
    template_name: str
    file_id: str
    description: Optional[str] = None

class BlankTemplateRead(BlankTemplateCreate):
    template_id: int
    created_at: datetime
    class Config:
        orm_mode = True

# ---- Temp Standard ----
class TempStandardItemUpdate(BaseModel):
    inspection_items: Optional[List[str]] = None
    inspection_methods: Optional[List[str]] = None
    acceptance_criteria: Optional[List[str]] = None
    frequency: Optional[str] = None
    responsible_party: Optional[str] = None
    notes: Optional[str] = None
    is_modified: Optional[bool] = True

class TempStandardItemRead(BaseModel):
    temp_item_id: int
    budget_item_id: int
    item_name: str
    item_type: str
    reference_standard_id: Optional[int]
    inspection_items: Optional[List[str]]
    inspection_methods: Optional[List[str]]
    acceptance_criteria: Optional[List[str]]
    frequency: Optional[str]
    responsible_party: Optional[str]
    notes: Optional[str]
    is_modified: bool
    last_modified: datetime
    class Config:
        orm_mode = True

class TempStandardFileRead(BaseModel):
    temp_file_id: int
    budget_id: str
    spec_id: Optional[str]
    items: list[TempStandardItemRead]
    class Config:
        orm_mode = True

# ---- Generated Form ----
class GeneratedFormRead(BaseModel):
    form_id: int
    form_name: str
    file_id: str
    file_format: str
    creation_date: datetime
    class Config:
        orm_mode = True
