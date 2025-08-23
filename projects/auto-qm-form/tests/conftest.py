import os
from pathlib import Path
import pytest
from alembic import command
from alembic.config import Config

from src.db import reset_engine_for_test, SessionLocal  # 你原本就有的

# 專案根 = tests 上一層
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALEMBIC_INI = PROJECT_ROOT / "alembic.ini"
MIGRATIONS_DIR = PROJECT_ROOT / "migrations"

def build_alembic_config(db_url: str) -> Config:
    """
    取得 Alembic Config：
    1) 若 alembic.ini 存在，讀檔後覆蓋 sqlalchemy.url
    2) 若不存在，動態建立一個 Config
    """
    if ALEMBIC_INI.exists():
        cfg = Config(str(ALEMBIC_INI))
        # 有些情況 alembic.ini 裡沒有設定 script_location，保險起見補上
        if not cfg.get_main_option("script_location") and MIGRATIONS_DIR.exists():
            cfg.set_main_option("script_location", str(MIGRATIONS_DIR))
    else:
        cfg = Config()
        if MIGRATIONS_DIR.exists():
            cfg.set_main_option("script_location", str(MIGRATIONS_DIR))
        else:
            raise RuntimeError(f"找不到 alembic.ini 且 {MIGRATIONS_DIR} 也不存在，請先 alembic init migrations")
    cfg.set_main_option("sqlalchemy.url", db_url)
    return cfg

def _determine_test_db_url() -> str:
    # 優先 TEST_DATABASE_URL，其次 DATABASE_URL，最後 fallback 到記憶型 sqlite
    return (
        os.getenv("TEST_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or "sqlite:///./test.sqlite"
    )

@pytest.fixture(scope="session", autouse=True)
def migrate():
    db_url = _determine_test_db_url()
    # 重建 engine（你原本自訂的功能）
    reset_engine_for_test(db_url)
    cfg = build_alembic_config(db_url)
    command.upgrade(cfg, "head")
    yield
    # (可選) 測試後若是 sqlite file，可清除
    if db_url.startswith("sqlite:///./test.sqlite"):
        try:
            Path("test.sqlite").unlink()
        except OSError:
            pass

@pytest.fixture
def db_session():
    """
    每個測試獨立 session；測試後 rollback & close。
    """
    session = SessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()
