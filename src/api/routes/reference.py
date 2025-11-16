# src/api/routes/reference.py
from fastapi import APIRouter, UploadFile, Form, Depends
from sqlalchemy.orm import Session
from ...db import get_db
from ...services import reference_data

router = APIRouter() # 可在 main.py 掛載時指定 prefix="/reference", tags=["reference"]

@router.post("/upload")
async def upload_reference(
    category: str = Form(...),
    description: str | None = Form(None),
    file: UploadFile = None,
    db: Session = Depends(get_db)
):
    data = await file.read()
    return reference_data.import_reference_data(db, data, file.filename, category, description)

@router.post("/template/upload")
async def upload_template(
    template_name: str = Form(...),
    description: str | None = Form(None),
    file: UploadFile = None,
    db: Session = Depends(get_db)
):
    data = await file.read()
    return reference_data.import_blank_qm_template(db, data, file.filename, template_name, description)

@router.get("/template/list")
def list_templates(db: Session = Depends(get_db)):
    return reference_data.get_templates(db)

@router.get("/search")
def search_ref(keyword: str | None = None, category: str | None = None, db: Session = Depends(get_db)):
    return reference_data.search_reference_data(db, keyword, category)
