# src/main.py 20250825 改良版

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.api.routes import budget_complex     # 新增 budget_paser.py 後引入 20250825


from src.db import get_db, test_connection, dispose_engine_on_shutdown
# 若已建立這些 router 模組再引入
from src.api.routes import budget, specs, reference, form, ui #增加 ui 20250825


app = FastAPI(title="AutoQM MVP", version="0.1.0")

# 掛載 budget_complex 路由 20250825
app.include_router(budget_complex.router)

@app.on_event("startup")
def on_startup():
    # 啟動即測試 DB，提早發現錯誤
    try:
        test_connection()
    except Exception as e:
        # 這裡用 RuntimeError 讓部署（例如 Docker healthcheck）快速失敗
        raise RuntimeError(f"Database connection failed: {e}")

@app.on_event("shutdown")
def on_shutdown():
    dispose_engine_on_shutdown()

@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}

@app.get("/debug/db_ping", tags=["system"])
def db_ping(db: Session = Depends(get_db)):
    value = db.execute(text("SELECT 1")).scalar()
    return {"db_select_1": value}

# Router 掛載（尚未到對應步驟可註解）己先注解
app.include_router(budget.router, prefix="/budget", tags=["budget"])
app.include_router(specs.router, prefix="/specs", tags=["specs"])
app.include_router(reference.router, prefix="/reference", tags=["reference"])
app.include_router(form.router, prefix="/form", tags=["form"])
app.include_router(budget_complex.router, prefix="/budget_complex", tags=["budget_complex"])  # 增加 budget_ccomplex 20250825
app.include_router(ui.router, prefix="/ui", tags=["ui"])  # 增加 ui 20250825

# 可選：根路徑
@app.get("/")
def root():
    return {"app": "AutoQM", "status": "running"}

# 若使用 uvicorn src.main:app --reload 即可啟動
