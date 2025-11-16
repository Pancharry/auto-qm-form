# src/api/routes/budget_complex.py
from fastapi import APIRouter, UploadFile, Form, Depends
from sqlalchemy.orm import Session
from ...db import get_db
from ...services import budget_parser


router = APIRouter() # tags=["budget_complex"]  # 可在 main.py 掛載時指定 tags

@router.post("/import")
async def import_complex_budget(
    budget_id: str = Form(...),
    file: UploadFile = None,
    db: Session = Depends(get_db)
):
    if not file:
        return {"status": False, "message": "file_required"}
    data = await file.read()
    return budget_parser.import_complex_budget(db, data, file.filename, budget_id)
