# src/models.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import (
    String,
    Integer,
    Float,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
    Index,
)

from src.db import Base  # 使用專案統一的 Base（含 naming_convention）


# ---- Budget ----
class BudgetItem(Base):
    __tablename__ = "budget_items"

    item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    budget_id: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    type: Mapped[str] = mapped_column(String(32))  # material/equipment/work
    unit: Mapped[str | None] = mapped_column(String(32))
    # 修正：使用 Python 型別 float | None 並在 mapped_column 指定 Float
    quantity: Mapped[float | None] = mapped_column(Float)
    unit_price: Mapped[float | None] = mapped_column(Float)
    total_price: Mapped[float | None] = mapped_column(Float)
    description: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON)

    temp_items: Mapped[list["TempStandardItem"]] = relationship(
        back_populates="budget_item",
        cascade="all, delete-orphan",
    )


Index("ix_budget_items_name_type", BudgetItem.name, BudgetItem.type)


# ---- Specifications ----
class SpecificationItem(Base):
    __tablename__ = "spec_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    spec_id: Mapped[str] = mapped_column(String(64), index=True)
    item_name: Mapped[str] = mapped_column(String(255), index=True)
    item_type: Mapped[str | None] = mapped_column(String(32))
    # JSON 欄位可再細化型別，如 list[str] | None；暫留寬鬆
    requirements: Mapped[list | None] = mapped_column(JSON)
    standards: Mapped[list | None] = mapped_column(JSON)
    testing_methods: Mapped[list | None] = mapped_column(JSON)
    acceptance_criteria: Mapped[list | None] = mapped_column(JSON)
    notes: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON)


# ---- Quality Standards (Reference) ----
class QualityStandard(Base):
    __tablename__ = "quality_standards"

    standard_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_name: Mapped[str] = mapped_column(String(255), index=True)
    item_type: Mapped[str] = mapped_column(String(32), index=True)
    source: Mapped[str | None] = mapped_column(String(255))
    inspection_items: Mapped[list | None] = mapped_column(JSON)
    inspection_methods: Mapped[list | None] = mapped_column(JSON)
    acceptance_criteria: Mapped[list | None] = mapped_column(JSON)
    frequency: Mapped[str | None] = mapped_column(String(128))
    responsible_party: Mapped[str | None] = mapped_column(String(128))
    notes: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON)


Index(
    "ix_quality_standards_item",
    QualityStandard.item_name,
    QualityStandard.item_type,
)


# ---- Templates ----
class BlankTemplate(Base):
    __tablename__ = "blank_templates"

    template_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    template_name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    file_id: Mapped[str] = mapped_column(String(64), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ---- Uploaded Reference Raw File ----
class ReferenceFile(Base):
    __tablename__ = "reference_files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(32))  # material/equipment/other
    description: Mapped[str | None] = mapped_column(Text)
    file_id: Mapped[str] = mapped_column(String(64), index=True)
    project_name: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON)


# ---- Temp Standards ----
class TempStandardFile(Base):
    __tablename__ = "temp_standard_files"
    temp_file_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    budget_id: Mapped[str] = mapped_column(String(64), index=True)
    spec_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    items: Mapped[list["TempStandardItem"]] = relationship(
        back_populates="temp_file", cascade="all, delete-orphan"
    )

class TempStandardItem(Base):
    __tablename__ = "temp_standard_items"

    temp_item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    temp_file_id: Mapped[int] = mapped_column(ForeignKey("temp_standard_files.temp_file_id"))
    budget_item_id: Mapped[int] = mapped_column(ForeignKey("budget_items.item_id"))

    item_name: Mapped[str] = mapped_column(String(255), index=True)
    item_type: Mapped[str] = mapped_column(String(32), index=True)
    reference_standard_id: Mapped[int | None] = mapped_column(ForeignKey("quality_standards.standard_id"))

    inspection_items: Mapped[list | None] = mapped_column(JSON)
    inspection_methods: Mapped[list | None] = mapped_column(JSON)
    acceptance_criteria: Mapped[list | None] = mapped_column(JSON)
    frequency: Mapped[str | None] = mapped_column(String(128))
    responsible_party: Mapped[str | None] = mapped_column(String(128))
    notes: Mapped[str | None] = mapped_column(Text)
    is_modified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_modified: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON)

    temp_file: Mapped[TempStandardFile] = relationship(back_populates="items")
    budget_item: Mapped[BudgetItem] = relationship(back_populates="temp_items")
    reference_standard: Mapped[QualityStandard | None] = relationship()


# ---- Generated Forms ----
class GeneratedForm(Base):
    __tablename__ = "generated_forms"

    form_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    temp_file_id: Mapped[int] = mapped_column(
        ForeignKey("temp_standard_files.temp_file_id")
    )
    template_id: Mapped[int] = mapped_column(ForeignKey("blank_templates.template_id"))
    form_name: Mapped[str] = mapped_column(String(255), index=True)
    creation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    file_id: Mapped[str] = mapped_column(String(64), index=True)
    file_format: Mapped[str] = mapped_column(String(16))
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON)


# ---- Stored Files (metadata only) ----
class StoredFile(Base):
    __tablename__ = "stored_files"

    file_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    original_name: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(512))
    mime_type: Mapped[str | None] = mapped_column(String(128))
    size_bytes: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON)
