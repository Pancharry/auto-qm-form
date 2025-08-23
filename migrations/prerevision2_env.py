# migrations/env.py  （方案 A：Base 留在 src/db.py，models 集中於 src/models.py）
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# --------------------------------------------------
# 1. 將專案根目錄加入 sys.path
#    假設此檔案位置：<project_root>/migrations/env.py
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# --------------------------------------------------
# 2. 匯入 Base
# --------------------------------------------------
from src.db import Base

# --------------------------------------------------
# 3. 匯入 models.py
#    必須：否則 Alembic 看不到具體 Table
# --------------------------------------------------
import src.models  # models.py 內的 class 定義會在 import 時註冊進 Base.metadata

# --------------------------------------------------
# 4. Alembic 基本設定
# --------------------------------------------------
config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# --------------------------------------------------
# 5. 取得資料庫 URL
# --------------------------------------------------
def resolve_db_url():
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    ini_url = config.get_main_option("sqlalchemy.url")
    if ini_url:
        return ini_url

    # 從設定載入（可選）
    try:
        from src.config import get_settings
        settings = get_settings()
        if getattr(settings, "DATABASE_URL", None):
            return settings.DATABASE_URL
    except Exception:
        pass

    return None

# --------------------------------------------------
# 6. 離線模式
# --------------------------------------------------
def run_migrations_offline():
    url = resolve_db_url()
    if not url:
        raise RuntimeError("未找到資料庫連線字串：請設定 DATABASE_URL 或 alembic.ini 的 sqlalchemy.url")

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
# 7. 在線模式
# --------------------------------------------------
def run_migrations_online():
    url = resolve_db_url()
    if not url:
        raise RuntimeError("未找到資料庫連線字串：請設定 DATABASE_URL 或 alembic.ini 的 sqlalchemy.url")

    config.set_main_option("sqlalchemy.url", url)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
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

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
    # debug 用，確認models 已正確載入 20250813
    print("Alembic models tables:", list(target_metadata.tables.keys()))
