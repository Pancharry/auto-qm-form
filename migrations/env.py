# migrations/env.py
from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, pool

# --------------------------------------------------
# 1. 將專案根目錄加入 sys.path
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 1.1 20250818 在 migrations/env.py 頂部 sys.path 完成後加入：
try:
    from src.config import get_settings  # Pydantic v2 settings
except Exception:
    get_settings = None  # 若失敗則 fallback 原邏輯

def get_db_url() -> str:
    # 1. -x db_url=...
    x_args = context.get_x_argument(as_dictionary=True)
    if "db_url" in x_args and x_args["db_url"]:
        return x_args["db_url"]

    # 2. TEST_DATABASE_URL (若存在且 APP_ENV=test)
    if os.getenv("TEST_DATABASE_URL"):
        return os.getenv("TEST_DATABASE_URL")

    # 3. DATABASE_URL
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")

    # 4. config settings（若有）
    if get_settings:
        try:
            s = get_settings()
            return s.effective_database_url
        except Exception:
            pass

    # 5. alembic.ini sqlalchemy.url
    ini_url = config.get_main_option("sqlalchemy.url")
    if ini_url:
        return ini_url

    raise RuntimeError("無法解析資料庫 URL，請設定 -x db_url= 或環境變數 DATABASE_URL")


# --------------------------------------------------
# 2. 匯入 Base 以及所有 models
# --------------------------------------------------
from src.db import Base  # Base 含 naming_convention
from src import models  # noqa: F401  需確保此路徑下的模型定義已被 import

# --------------------------------------------------
# 3. Alembic 基本 config 與 logging
# --------------------------------------------------
config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# --------------------------------------------------
# 4. 解析 DB URL（優先順序）
#    -x db_url > TEST_DATABASE_URL > DATABASE_URL > alembic.ini sqlalchemy.url
# --------------------------------------------------
def get_db_url() -> str:
    # 來自 alembic -x 參數
    x_args = context.get_x_argument(as_dictionary=True)
    if "db_url" in x_args and x_args["db_url"]:
        return x_args["db_url"]

    test_url = os.getenv("TEST_DATABASE_URL")
    if test_url:
        return test_url

    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    ini_url = config.get_main_option("sqlalchemy.url")
    if ini_url:
        return ini_url

    raise RuntimeError("無法解析資料庫 URL，請使用 -x db_url= 或設定環境變數。")


# --------------------------------------------------
# 5. 離線模式（產出 SQL 而不實際連線）
# --------------------------------------------------
def run_migrations_offline():
    url = get_db_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# --------------------------------------------------
# 6. 線上模式（實際執行 migration）
# --------------------------------------------------
def run_migrations_online():
    url = get_db_url()
    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# --------------------------------------------------
# 7. 入口
# --------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
