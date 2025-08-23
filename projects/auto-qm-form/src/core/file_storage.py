# src/core/file_storage.py
import os, uuid
from pathlib import Path
from ..config import settings

def save_file(file_bytes: bytes, filename: str, file_type: str, metadata: dict | None = None, db=None):
    root = Path(settings.FILE_STORAGE_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    file_id = uuid.uuid4().hex[:16]
    ext = os.path.splitext(filename)[1]
    stored_name = f"{file_id}{ext}"
    path = root / stored_name
    with open(path, "wb") as f:
        f.write(file_bytes)
    from .. import models
    sf = models.StoredFile(
        file_id=file_id,
        file_name=filename,
        file_type=file_type,
        path=str(path),
        size=len(file_bytes),
        metadata_json=metadata or {}
    )
    db.add(sf)
    db.commit()
    return {"status": True, "file_id": file_id, "path": str(path)}

def read_file(file_id: str, db):
    from ..models import StoredFile
    sf = db.query(StoredFile).filter_by(file_id=file_id).first()
    if not sf:
        return None
    with open(sf.path, "rb") as f:
        data = f.read()
    return sf, data
