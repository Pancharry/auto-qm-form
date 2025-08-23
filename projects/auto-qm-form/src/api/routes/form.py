# src/api/routes/form.py
from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from ...db import get_db
from ...services import form_generation

router = APIRouter(prefix="/form", tags=["form"])

@router.get("/identify/{budget_id}")
def identify(budget_id: str, db: Session = Depends(get_db)):
    return form_generation.identify_management_items(db, budget_id)

@router.post("/temp/create")
def create_temp(
    budget_id: str = Form(...),
    spec_id: str | None = Form(None),
    db: Session = Depends(get_db)
):
    return form_generation.create_temp_standards(db, budget_id, spec_id)

@router.get("/temp/{temp_file_id}")
def get_temp(temp_file_id: int, db: Session = Depends(get_db)):
    return form_generation.get_temp_standards(db, temp_file_id)

@router.post("/temp/item/update")
def update_temp_item(
    temp_item_id: int = Form(...),
    inspection_items: str | None = Form(None),
    inspection_methods: str | None = Form(None),
    acceptance_criteria: str | None = Form(None),
    frequency: str | None = Form(None),
    responsible_party: str | None = Form(None),
    notes: str | None = Form(None),
    db: Session = Depends(get_db)
):
    updated = {
        "inspection_items": [s.strip() for s in inspection_items.split(",")] if inspection_items else None,
        "inspection_methods": [s.strip() for s in inspection_methods.split(",")] if inspection_methods else None,
        "acceptance_criteria": [s.strip() for s in acceptance_criteria.split(",")] if acceptance_criteria else None,
        "frequency": frequency,
        "responsible_party": responsible_party,
        "notes": notes
    }
    return form_generation.update_temp_standard_item(db, temp_item_id, updated)

@router.post("/generate")
def generate_form(
    temp_file_id: int = Form(...),
    template_id: int = Form(...),
    form_name: str = Form(...),
    db: Session = Depends(get_db)
):
    return form_generation.generate_final_form(db, temp_file_id, template_id, form_name)
