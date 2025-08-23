# src/services/ingestion.py
import io
import pandas as pd
from sqlalchemy.orm import Session
from ..models import BudgetItem, SpecificationItem
from ..core.llm import get_llm_client

def import_budget_details(db: Session, file_bytes: bytes, file_type: str, budget_id: str):
    if file_type not in ("excel", "csv"):
        return {"status": False, "message": "unsupported file_type"}
    if file_type == "excel":
        df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        df = pd.read_csv(io.BytesIO(file_bytes))

    # 預期欄位：Name, Type, Unit, Qty, UnitPrice, Desc (可調整)
    inserted = 0
    for _, r in df.iterrows():
        name = str(r.get("Name") or "").strip()
        if not name:
            continue
        bi = BudgetItem(
            budget_id=budget_id,
            name=name,
            type=str(r.get("Type") or "material"),
            unit=str(r.get("Unit") or ""),
            quantity=float(r.get("Qty")) if r.get("Qty") else None,
            unit_price=float(r.get("UnitPrice")) if r.get("UnitPrice") else None,
            total_price=float(r.get("TotalPrice")) if r.get("TotalPrice") else None,
            description=str(r.get("Desc") or "")
        )
        db.add(bi)
        inserted += 1
    db.commit()
    return {"status": True, "message": f"imported {inserted} items", "budget_id": budget_id}

def parse_budget_items(db: Session, budget_id: str):
    q = db.query(BudgetItem).filter(BudgetItem.budget_id == budget_id).all()
    materials = [b for b in q if b.type == "material"]
    equipment = [b for b in q if b.type == "equipment"]
    return {
        "status": True,
        "message": "ok",
        "materials": [{"id": m.item_id, "name": m.name} for m in materials],
        "equipment": [{"id": e.item_id, "name": e.name} for e in equipment]
    }

def import_technical_specs(db: Session, file_bytes: bytes, file_type: str, spec_id: str):
    text = ""
    if file_type in ("txt", "text"):
        text = file_bytes.decode("utf-8", errors="ignore")
    elif file_type == "docx":
        import docx
        f = io.BytesIO(file_bytes)
        doc = docx.Document(f)
        text = "\n".join(p.text for p in doc.paragraphs)
    elif file_type == "pdf":
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
            text = "\n".join(pages)
    else:
        return {"status": False, "message": "unsupported file_type"}

    llm = get_llm_client()
    parsed = llm.parse_text(text, task_type="extract_specs")
    raw_items = parsed["result"].get("raw_items", [])
    count = 0
    for it in raw_items:
        db.add(SpecificationItem(
            spec_id=spec_id,
            item_name=it.get("name"),
            item_type=None,
            requirements=[it.get("spec")],
            standards=None
        ))
        count += 1
    db.commit()
    return {"status": True, "message": f"parsed {count} spec items", "spec_id": spec_id}

def parse_technical_specs(db: Session, spec_id: str):
    # 已在 import 階段解析，這裡可以再做結構化聚合
    items = db.query(SpecificationItem).filter_by(spec_id=spec_id).all()
    return {
        "status": True,
        "message": "ok",
        "specs_data": [
            {"id": i.id, "name": i.item_name, "requirements": i.requirements} for i in items
        ]
    }
