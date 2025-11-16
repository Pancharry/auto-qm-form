# src/api/routes/specs.py
from fastapi import APIRouter, UploadFile, Form, Depends
from sqlalchemy.orm import Session
from ...db import get_db
from ...services import ingestion

router = APIRouter() # tags=["specs"]  # 可在 main.py 掛載時指定 prefix="/specs", tags=["specs"]


@router.post("/import")
async def import_specs(
    spec_id: str = Form(...),
    file: UploadFile = None,
    db: Session = Depends(get_db)
):
    if not file:
        return {"status": False, "message": "file required"}
    ext = file.filename.lower().rsplit(".", 1)[-1]
    ft = "pdf" if ext == "pdf" else ("docx" if ext == "docx" else "txt")
    data = await file.read()
    return ingestion.import_technical_specs(db, data, ft, spec_id)

@router.get("/{spec_id}/parsed")
def get_spec_parsed(spec_id: str, db: Session = Depends(get_db)):
    return ingestion.parse_technical_specs(db, spec_id)
