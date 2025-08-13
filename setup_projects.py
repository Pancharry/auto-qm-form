import os
from textwrap import dedent

PROJECT_ROOT = "projects/auto-qm-form"

FILES = {
    "requirements.txt": dedent("""
    fastapi==0.111.0
    uvicorn[standard]==0.30.0
    sqlalchemy==2.0.30
    psycopg2-binary==2.9.9
    pydantic==2.7.1
    pydantic-settings==2.2.1
    python-dotenv==1.0.1
    """).strip() + "\n",

    ".env.example": dedent("""
    # 環境設定範例，複製為 .env 後可調整
    APP_NAME=AutoQM
    APP_ENV=dev
    APP_HOST=127.0.0.1
    APP_PORT=8000

    # 資料庫連線（PostgreSQL - 宿主機 Python → Docker Postgres）
    DATABASE_URL=postgresql+psycopg2://appuser:apppass@localhost:5432/auto_qm

    # 若暫時不用 Docker，可改為：
    # DATABASE_URL=sqlite:///./local.db
    """).strip() + "\n",

    "docker-compose.db.yml": dedent("""
    version: "3.9"
    services:
      postgres:
        image: postgres:16-alpine
        container_name: autoqm-postgres
        environment:
          POSTGRES_USER: appuser
          POSTGRES_PASSWORD: apppass
          POSTGRES_DB: auto_qm
        ports:
          - "5432:5432"
        volumes:
          - pgdata:/var/lib/postgresql/data
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U appuser -d auto_qm"]
          interval: 5s
          timeout: 5s
          retries: 10
    volumes:
      pgdata:
    """).strip() + "\n",

    "README_SIMPLIFIED.md": dedent("""
    # Auto QM Form (Simplified Init)

    本專案為簡化版初始化：後端在宿主機執行，PostgreSQL 透過 Docker。
    可使用 create_all 直接建立資料表，後續再導入 Alembic。

    ## 快速開始

    1. python -m venv .venv && source .venv/bin/activate
    2. pip install -r requirements.txt
    3. cp .env.example .env
    4. docker compose -f docker-compose.db.yml up -d
    5. uvicorn src.main:app --reload --port 8000
    6. http://127.0.0.1:8000/docs

    ## 變更資料庫
    - 使用 SQLite：修改 .env 的 DATABASE_URL=sqlite:///./local.db
    - 改回 Postgres：DATABASE_URL=postgresql+psycopg2://appuser:apppass@localhost:5432/auto_qm

    ## 下一步建議
    - 加入 Alembic
    - 改 async engine
    - 容器化 backend
    """).strip() + "\n",

    "src/__init__.py": "",
    "src/config.py": dedent("""
    from pydantic_settings import BaseSettings
    from functools import lru_cache

    class Settings(BaseSettings):
        APP_NAME: str = "AutoQM"
        APP_ENV: str = "dev"
        APP_HOST: str = "127.0.0.1"
        APP_PORT: int = 8000
        DATABASE_URL: str = "sqlite:///./local.db"

        class Config:
            env_file = ".env"
            extra = "ignore"

    @lru_cache
    def get_settings() -> Settings:
        return Settings()
    """).strip() + "\n",

    "src/db.py": dedent("""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, DeclarativeBase
    from src.config import get_settings

    settings = get_settings()

    # 同步 Engine（初期簡化；未來可換 async）
    engine = create_engine(
        settings.DATABASE_URL,
        echo=(settings.APP_ENV == "dev"),
        future=True
    )

    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    class Base(DeclarativeBase):
        pass

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    """).strip() + "\n",

    "src/models.py": dedent("""
    from sqlalchemy import String, Integer
    from sqlalchemy.orm import Mapped, mapped_column
    from src.db import Base

    class MaterialEquipment(Base):
        __tablename__ = "material_equipment"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(100), index=True)
        type: Mapped[str] = mapped_column(String(50))          # material / equipment
        category: Mapped[str] = mapped_column(String(100))     # 自由分類
        system_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    class Budget(Base):
        __tablename__ = "budget"
        id: Mapped[int] = mapped_column(primary_key=True)
        budget_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
        name: Mapped[str] = mapped_column(String(100))

    class TechnicalSpec(Base):
        __tablename__ = "technical_spec"
        id: Mapped[int] = mapped_column(primary_key=True)
        spec_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
        name: Mapped[str] = mapped_column(String(100))
    """).strip() + "\n",

    "src/schemas.py": dedent("""
    from pydantic import BaseModel

    # Material / Equipment
    class MaterialEquipmentBase(BaseModel):
        name: str
        type: str
        category: str
        system_type: str | None = None

    class MaterialEquipmentCreate(MaterialEquipmentBase):
        pass

    class MaterialEquipmentRead(MaterialEquipmentBase):
        id: int
        class Config:
            from_attributes = True

    # Budget
    class BudgetBase(BaseModel):
        budget_code: str
        name: str

    class BudgetCreate(BudgetBase):
        pass

    class BudgetRead(BudgetBase):
        id: int
        class Config:
            from_attributes = True

    # Technical Spec
    class TechnicalSpecBase(BaseModel):
        spec_code: str
        name: str

    class TechnicalSpecCreate(TechnicalSpecBase):
        pass

    class TechnicalSpecRead(TechnicalSpecBase):
        id: int
        class Config:
            from_attributes = True
    """).strip() + "\n",

    "src/crud.py": dedent("""
    from sqlalchemy.orm import Session
    from sqlalchemy import select
    from src import models
    from src import schemas

    # Generic helpers (可後續泛型化)

    # MaterialEquipment
    def create_material_equipment(db: Session, data: schemas.MaterialEquipmentCreate):
        obj = models.MaterialEquipment(**data.model_fields_set, **data.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_material_equipment(db: Session, limit: int = 50):
        return db.execute(select(models.MaterialEquipment).limit(limit)).scalars().all()

    def get_material_equipment(db: Session, item_id: int):
        return db.get(models.MaterialEquipment, item_id)

    # Budget
    def create_budget(db: Session, data: schemas.BudgetCreate):
        obj = models.Budget(**data.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_budgets(db: Session, limit: int = 50):
        return db.execute(select(models.Budget).limit(limit)).scalars().all()

    def get_budget(db: Session, item_id: int):
        return db.get(models.Budget, item_id)

    # TechnicalSpec
    def create_technical_spec(db: Session, data: schemas.TechnicalSpecCreate):
        obj = models.TechnicalSpec(**data.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_technical_specs(db: Session, limit: int = 50):
        return db.execute(select(models.TechnicalSpec).limit(limit)).scalars().all()

    def get_technical_spec(db: Session, item_id: int):
        return db.get(models.TechnicalSpec, item_id)
    """).strip() + "\n",

    "src/main.py": dedent("""
    from fastapi import FastAPI, Depends, HTTPException
    from sqlalchemy.orm import Session
    from src.db import Base, engine, get_db
    from src import schemas, crud, models
    from src.config import get_settings

    settings = get_settings()

    # 啟動時建立資料表（初期簡化，未來換 Alembic）
    def init_models():
        Base.metadata.create_all(bind=engine)

    init_models()

    app = FastAPI(title=settings.APP_NAME, version="0.1.0")

    @app.get("/health")
    def health():
        return {"status": "ok", "env": settings.APP_ENV}

    # MaterialEquipment Endpoints
    @app.post("/material-equipment", response_model=schemas.MaterialEquipmentRead)
    def create_material_equipment(payload: schemas.MaterialEquipmentCreate, db: Session = Depends(get_db)):
        return crud.create_material_equipment(db, payload)

    @app.get("/material-equipment", response_model=list[schemas.MaterialEquipmentRead])
    def list_material_equipment(limit: int = 50, db: Session = Depends(get_db)):
        return crud.list_material_equipment(db, limit)

    @app.get("/material-equipment/{item_id}", response_model=schemas.MaterialEquipmentRead)
    def get_material_equipment(item_id: int, db: Session = Depends(get_db)):
        obj = crud.get_material_equipment(db, item_id)
        if not obj:
            raise HTTPException(404, "Not found")
        return obj

    # Budget
    @app.post("/budgets", response_model=schemas.BudgetRead)
    def create_budget(payload: schemas.BudgetCreate, db: Session = Depends(get_db)):
        return crud.create_budget(db, payload)

    @app.get("/budgets", response_model=list[schemas.BudgetRead])
    def list_budgets(limit: int = 50, db: Session = Depends(get_db)):
        return crud.list_budgets(db, limit)

    @app.get("/budgets/{item_id}", response_model=schemas.BudgetRead)
    def get_budget(item_id: int, db: Session = Depends(get_db)):
        obj = crud.get_budget(db, item_id)
        if not obj:
            raise HTTPException(404, "Not found")
        return obj

    # Technical Spec
    @app.post("/technical-specs", response_model=schemas.TechnicalSpecRead)
    def create_technical_spec(payload: schemas.TechnicalSpecCreate, db: Session = Depends(get_db)):
        return crud.create_technical_spec(db, payload)

    @app.get("/technical-specs", response_model=list[schemas.TechnicalSpecRead])
    def list_technical_specs(limit: int = 50, db: Session = Depends(get_db)):
        return crud.list_technical_specs(db, limit)

    @app.get("/technical-specs/{item_id}", response_model=schemas.TechnicalSpecRead)
    def get_technical_spec(item_id: int, db: Session = Depends(get_db)):
        obj = crud.get_technical_spec(db, item_id)
        if not obj:
            raise HTTPException(404, "Not found")
        return obj
    """).strip() + "\n",
}


def create_file(path, content):
    if os.path.exists(path):
        print(f"[skip] {path} already exists")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[ok]   {path}")

def main():
    print("== Generating simplified project structure ==")
    # 建立根目錄
    os.makedirs(PROJECT_ROOT, exist_ok=True)
    # 子目錄
    os.makedirs(os.path.join(PROJECT_ROOT, "src"), exist_ok=True)

    for rel_path, content in FILES.items():
        abs_path = os.path.join(PROJECT_ROOT, rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        create_file(abs_path, content)

    print("\n完成。下一步：")
    print(f"  1. cd {PROJECT_ROOT}")
    print("  2. python -m venv .venv && source .venv/bin/activate")
    print("  3. pip install -r requirements.txt")
    print("  4. cp .env.example .env (如需)")
    print("  5. docker compose -f docker-compose.db.yml up -d")
    print("  6. uvicorn src.main:app --reload --port 8000")
    print("  7. 瀏覽 http://127.0.0.1:8000/docs")

if __name__ == "__main__":
    main()