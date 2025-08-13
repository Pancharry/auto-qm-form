from pydantic import BaseModel

# Material / Equipment
class MaterialEquipmentBase(BaseModel):
    name: str
    type: str
    category: str
    system_type: str | None = None

class MaterialEquipmentCreate(MaterialEquipmentBase):
    pass

class MaterialEquipmentRead(MaterialEquipmentBase):
    id: int
    class Config:
        from_attributes = True

# Budget
class BudgetBase(BaseModel):
    budget_code: str
    name: str

class BudgetCreate(BudgetBase):
    pass

class BudgetRead(BudgetBase):
    id: int
    class Config:
        from_attributes = True

# Technical Spec
class TechnicalSpecBase(BaseModel):
    spec_code: str
    name: str

class TechnicalSpecCreate(TechnicalSpecBase):
    pass

class TechnicalSpecRead(TechnicalSpecBase):
    id: int
    class Config:
        from_attributes = True
