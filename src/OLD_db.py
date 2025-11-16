# src/db.py
from __future__ import annotations

import os
from typing import Generator, Optional, Callable

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
    Session,
)

# 你自己的設定模組（若無可移除）
try:
    from src.config import get_settings  # 假設存在
except Exception:  # noqa
    get_settings = None  # type: ignore


# -----------------------------------------
# 命名慣例：讓 Alembic 在 rename / diff 時更穩定
# -----------------------------------------
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# -----------------------------------------
# 取得資料庫 URL（統一邏輯）
# -----------------------------------------
def _resolve_database_url(
    explicit: Optional[str] = None,
    prefer_test: bool = True,
) -> str:
    """
    解析資料庫連線字串優先順序：
    1. explicit (呼叫者直接傳入)
    2. TEST_DATABASE_URL（若 prefer_test=True）
    3. DATABASE_URL
    4. 設定物件 (get_settings) 的 DATABASE_URL
    5. 失敗則拋例外
    """
    if explicit:
        return explicit

    if prefer_test:
        env_test = os.getenv("TEST_DATABASE_URL")
        if env_test:
            return env_test

    env_main = os.getenv("DATABASE_URL")
    if env_main:
        return env_main

    if get_settings:
        try:
            settings = get_settings()
            if getattr(settings, "TEST_DATABASE_URL", None) and prefer_test:
                return settings.TEST_DATABASE_URL  # type: ignore
            if getattr(settings, "DATABASE_URL", None):
                return settings.DATABASE_URL  # type: ignore
        except Exception:
            pass

    raise RuntimeError("無法解析資料庫 URL，請設定 TEST_DATABASE_URL 或 DATABASE_URL")


# -----------------------------------------
# Engine / Session 管理（惰性建立 + 可重置）
# -----------------------------------------
_ENGINE = None
_SessionFactory: Optional[sessionmaker] = None

# 20250823 增加 pool_size, max_overflow 參數
def get_engine(
    url: Optional[str] = None,
    *,
    echo: bool = False,
    future: bool = True,
    pool_pre_ping: bool = True,
    pool_size: int | None = None,
    max_overflow: int | None = None,
):
    global _ENGINE
    if _ENGINE is not None and url is not None:
        # 若傳入的 url 與現有 engine 不同 → 重新建立
        current_url = str(_ENGINE.url)
        if current_url != url:
            _ENGINE.dispose()
            _ENGINE = None

#    if _ENGINE is None:
        resolved = _resolve_database_url(url)
        _ENGINE = create_engine(
            resolved,
            echo=echo,
            future=future,
            pool_pre_ping=pool_pre_ping,
        )
#    return _ENGINE
#    20250823 增加下列邏輯
        if _ENGINE is None:
            resolved = _resolve_database_url(url)
            connect_args = {}
            if resolved.startswith("sqlite"):
                # FastAPI 多執行緒 + SQLite 需關閉同執行緒限制
                connect_args["check_same_thread"] = False
            create_kwargs = {
                "echo": echo,
                "future": future,
                "pool_pre_ping": pool_pre_ping,
            }
            # SQLite 不支援 pool_size / max_overflow
            if not resolved.startswith("sqlite"):
                if pool_size is not None:
                    create_kwargs["pool_size"] = pool_size
                if max_overflow is not None:
                    create_kwargs["max_overflow"] = max_overflow
            _ENGINE = create_engine(resolved, connect_args=connect_args, **create_kwargs)
         return _ENGINE

def get_sessionmaker(
    url: Optional[str] = None,
    *,
    expire_on_commit: bool = False,
    autoflush: bool = True,
) -> sessionmaker:
    global _SessionFactory
    if _SessionFactory is not None and url is not None:
        # 若需要強制重建
        engine = get_engine(url)
        if _SessionFactory.kw.get("bind") is not engine:  # type: ignore
            _SessionFactory = None

    if _SessionFactory is None:
        engine = get_engine(url)
        _SessionFactory = sessionmaker(
            bind=engine,
            class_=Session,
            expire_on_commit=expire_on_commit,
            autoflush=autoflush,
            future=True,
        )
    return _SessionFactory


# 預設的 SessionLocal（供現有程式碼沿用）
SessionLocal = get_sessionmaker()


# -----------------------------------------
# FastAPI 或一般 dependency 用法
# -----------------------------------------
def get_db() -> Generator[Session, None, None]:
    """
    with 用法：
    with SessionLocal() as db:
        ...
    或 FastAPI:
    def endpoint(db: Session = Depends(get_db)):
        ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------------------
# 測試專用：重置 engine / session（例如在 pytest fixture 裡）
# -----------------------------------------
def reset_engine_for_test(url: str):
    """
    在測試初始化時呼叫：
        reset_engine_for_test(TEST_DATABASE_URL)
    之後 import 的 SessionLocal 會指向新的 sessionmaker。
    """
    global _ENGINE, _SessionFactory, SessionLocal
    if _ENGINE is not None:
        try:
            _ENGINE.dispose()
        except Exception:
            pass
    _ENGINE = None
    _SessionFactory = None
    SessionLocal = get_sessionmaker(url)  # type: ignore


# -----------------------------------------
# （可選）快速建立全部表（不建議在正式或與 Alembic 併用）
# -----------------------------------------
"""
def create_all(url: Optional[str] = None):
    engine = get_engine(url)
    Base.metadata.create_all(engine)


def drop_all(url: Optional[str] = None):
    engine = get_engine(url)
    Base.metadata.drop_all(engine)
"""

# -----------------------------------------
# 入口測試（手動執行）
# -----------------------------------------
if __name__ == "__main__":
    # 單次連線測試
#    engine = get_engine()
#    with engine.connect() as conn:
#        print("資料庫連線成功：", conn.execute("SELECT 1").scalar())

# 20250823 修改為 text() 方式
       engine = get_engine()
        with engine.connect() as conn:
            print("資料庫連線成功：", conn.execute(text("SELECT 1")).scalar())

# -----------------------------------------
# 啟動檢查 / 關閉釋放（供 main.py 使用）
# -----------------------------------------
def test_connection() -> None:
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

def dispose_engine_on_shutdown():
    global _ENGINE
    if _ENGINE is not None:
        try:
            _ENGINE.dispose()
       finally:
            _ENGINE = None