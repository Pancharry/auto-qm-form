# src/services/reference_data.py
from sqlalchemy.orm import Session
from ..models import QualityStandard, BlankTemplate, ReferenceFile
from ..core.file_storage import save_file
import difflib

def import_reference_data(db: Session, file_bytes: bytes, filename: str, category: str, description: str | None):
    # 簡化：直接存檔 (原始參考文件)，不做解析
    r = save_file(file_bytes, filename, "reference/"+category, db=db)
    rf = ReferenceFile(
        category=category,
        description=description,
        file_id=r["file_id"]
    )
    db.add(rf)
    db.commit()
    return {"status": True, "reference_id": rf.id, "message": "uploaded"}

def import_blank_qm_template(db: Session, file_bytes: bytes, filename: str, template_name: str, description: str | None):
    r = save_file(file_bytes, filename, "template", db=db)
    tpl = BlankTemplate(template_name=template_name, file_id=r["file_id"], description=description)
    db.add(tpl)
    db.commit()
    return {"status": True, "template_id": tpl.template_id}

def search_reference_data(db: Session, keyword: str | None, category: str | None):
    q = db.query(QualityStandard)
    if category:
        q = q.filter(QualityStandard.item_type == category)
    results = q.all()
    if keyword:
        # fuzzy filter
        names = [r.item_name for r in results]
        matches = set(difflib.get_close_matches(keyword, names, n=20, cutoff=0.2))
        results = [r for r in results if r.item_name in matches or keyword.lower() in r.item_name.lower()]
    return {"status": True, "results": [
        {
            "standard_id": r.standard_id,
            "item_name": r.item_name,
            "item_type": r.item_type,
            "source": r.source
        } for r in results
    ]}

def get_templates(db: Session):
    tpls = db.query(BlankTemplate).all()
    return {"status": True, "templates": [
        {"template_id": t.template_id, "name": t.template_name} for t in tpls
    ]}
