# src/services/form_generation.py
from sqlalchemy.orm import Session
from ..models import (
    BudgetItem, QualityStandard, TempStandardFile, TempStandardItem,
    GeneratedForm, BlankTemplate
)
from ..core.file_storage import save_file
import difflib
import io
from openpyxl import Workbook
from datetime import datetime

def identify_management_items(db: Session, budget_id: str):
    q = db.query(BudgetItem).filter(BudgetItem.budget_id == budget_id).all()
    items = [{"budget_item_id": b.item_id, "name": b.name, "type": b.type} for b in q if b.type in ("material", "equipment")]
    return {"status": True, "items": items, "message": "ok"}

def search_quality_standards(db: Session, item_type: str, item_name: str, fuzzy: bool = True):
    q = db.query(QualityStandard).filter(QualityStandard.item_type == item_type).all()
    if not fuzzy:
        matched = [r for r in q if r.item_name.lower() == item_name.lower()]
    else:
        names = [r.item_name for r in q]
        close = set(difflib.get_close_matches(item_name, names, n=10, cutoff=0.3))
        matched = [r for r in q if r.item_name in close or item_name.lower() in r.item_name.lower()]
    return {"status": True, "standards": [
        {
            "standard_id": r.standard_id,
            "item_name": r.item_name,
            "source": r.source
        } for r in matched
    ]}

def create_temp_standards(db: Session, budget_id: str, spec_id: str | None = None):
    # 取得預算項目
    b_items = db.query(BudgetItem).filter(BudgetItem.budget_id == budget_id).all()
    tfile = TempStandardFile(budget_id=budget_id, spec_id=spec_id)
    db.add(tfile)
    db.flush()

    # 預設：嘗試匹配同名標準（簡單策略）
    all_stds = db.query(QualityStandard).all()
    std_map = {}
    for s in all_stds:
        std_map.setdefault(s.item_type, []).append(s)

    matched_count = 0
    for b in b_items:
        if b.type not in ("material", "equipment"):
            continue
        candidates = std_map.get(b.type, [])
        chosen = None
        for c in candidates:
            if c.item_name.lower() == b.name.lower():
                chosen = c
                break
        item = TempStandardItem(
            temp_file_id=tfile.temp_file_id,
            budget_item_id=b.item_id,
            item_name=b.name,
            item_type=b.type,
            reference_standard_id=chosen.standard_id if chosen else None,
            inspection_items=chosen.inspection_items if chosen else None,
            inspection_methods=chosen.inspection_methods if chosen else None,
            acceptance_criteria=chosen.acceptance_criteria if chosen else None,
            frequency=chosen.frequency if chosen else None,
            responsible_party=chosen.responsible_party if chosen else None,
            notes=chosen.notes if chosen else None
        )
        if chosen:
            matched_count += 1
        db.add(item)
    db.commit()
    return {
        "status": True,
        "message": "temp created",
        "temp_file_id": tfile.temp_file_id,
        "items_count": len(b_items),
        "matched_count": matched_count
    }

def get_temp_standards(db: Session, temp_file_id: int, item_id: int | None = None):
    q = db.query(TempStandardItem).filter(TempStandardItem.temp_file_id == temp_file_id)
    if item_id:
        q = q.filter(TempStandardItem.temp_item_id == item_id)
    items = q.all()
    def serialize(i):
        return {
            "temp_item_id": i.temp_item_id,
            "budget_item_id": i.budget_item_id,
            "item_name": i.item_name,
            "item_type": i.item_type,
            "reference_standard_id": i.reference_standard_id,
            "inspection_items": i.inspection_items,
            "inspection_methods": i.inspection_methods,
            "acceptance_criteria": i.acceptance_criteria,
            "frequency": i.frequency,
            "responsible_party": i.responsible_party,
            "notes": i.notes,
            "is_modified": i.is_modified,
            "last_modified": i.last_modified.isoformat()
        }
    return {"status": True, "standards": [serialize(i) for i in items]}

def update_temp_standard_item(db: Session, temp_item_id: int, updated: dict):
    item = db.query(TempStandardItem).filter_by(temp_item_id=temp_item_id).first()
    if not item:
        return {"status": False, "message": "not found"}
    for k, v in updated.items():
        if hasattr(item, k) and v is not None:
            setattr(item, k, v)
    item.is_modified = True
    db.commit()
    return {"status": True, "message": "updated"}

def generate_final_form(db: Session, temp_file_id: int, template_id: int, form_name: str):
    tfile = db.query(TempStandardFile).filter_by(temp_file_id=temp_file_id).first()
    tpl = db.query(BlankTemplate).filter_by(template_id=template_id).first()
    if not tfile or not tpl:
        return {"status": False, "message": "temp_file or template not found"}
    items = db.query(TempStandardItem).filter_by(temp_file_id=temp_file_id).all()

    # 生成 Excel (簡易)
    wb = Workbook()
    ws = wb.active
    ws.title = "品質管理標準"
    headers = ["項目名稱", "類型", "檢驗項目", "檢驗方法", "驗收標準", "頻率", "責任單位", "備註"]
    ws.append(headers)
    for it in items:
        ws.append([
            it.item_name,
            it.item_type,
            ", ".join(it.inspection_items or []),
            ", ".join(it.inspection_methods or []),
            ", ".join(it.acceptance_criteria or []),
            it.frequency or "",
            it.responsible_party or "",
            it.notes or ""
        ])

    bio = io.BytesIO()
    wb.save(bio)
    excel_bytes = bio.getvalue()
    r = save_file(excel_bytes, f"{form_name}.xlsx", "generated/form", db=db)

    gf = GeneratedForm(
        temp_file_id=temp_file_id,
        template_id=template_id,
        form_name=form_name,
        file_id=r["file_id"],
        file_format="excel",
        metadata_json={"generated_at": datetime.utcnow().isoformat()}
    )
    db.add(gf)
    db.commit()
    return {
        "status": True,
        "message": "form generated",
        "form_id": gf.form_id,
        "download_file_id": gf.file_id
    }
