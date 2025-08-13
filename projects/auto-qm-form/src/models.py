from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.db import Base

class MaterialEquipment(Base):
    __tablename__ = "material_equipment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    type: Mapped[str] = mapped_column(String(50))          # material / equipment
    category: Mapped[str] = mapped_column(String(100))     # 自由分類
    system_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

class Budget(Base):
    __tablename__ = "budget"
    id: Mapped[int] = mapped_column(primary_key=True)
    budget_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))

class TechnicalSpec(Base):
    __tablename__ = "technical_spec"
    id: Mapped[int] = mapped_column(primary_key=True)
    spec_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
