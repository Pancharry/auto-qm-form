# src/core/file_storage.py
import os, uuid
from pathlib import Path
from ..config import settings

def save_file(file_bytes: bytes, filename: str, file_type: str, metadata: dict | None = None, db=None):
    """
    保存檔案到檔案系統並記錄到 StoredFile 資料表。
    - file_type: 建議傳入 MIME 類型或邏輯類型（此版本映射到 mime_type 欄位）
    - 回傳：{"status": True, "file_id": <int>, "path": <str>}
    """
    root = Path(settings.FILE_STORAGE_ROOT)
    root.mkdir(parents=True, exist_ok=True)

    # 用 UUID 作為實際儲存檔名，避免衝突；保留原始擴展名
    ext = os.path.splitext(filename)[1]
    stored_name = f"{uuid.uuid4().hex[:16]}{ext}"
    path = root / stored_name

    with open(path, "wb") as f:
        f.write(file_bytes)

    from .. import models

    sf = models.StoredFile(
        original_name=filename,
        stored_path=str(path),
        mime_type=file_type,          # 對齊模型欄位
        size_bytes=len(file_bytes),
        metadata_json=metadata or {}
    )
    db.add(sf)
    db.commit()
    db.refresh(sf)  # 取得自增主鍵

    return {"status": True, "file_id": sf.file_id, "path": str(path)}

def read_file(file_id: int, db):
    """
    以資料庫主鍵 file_id 讀取檔案。
    回傳：(StoredFile, bytes) 或 None
    """
    from ..models import StoredFile
    sf = db.query(StoredFile).filter_by(file_id=file_id).first()
    if not sf:
        return None
    if not os.path.exists(sf.stored_path):
        # 檔案紀錄存在但實體檔案遺失
        return None
    with open(sf.stored_path, "rb") as f:
        data = f.read()
    return sf, data