import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# --- 1. 動態路徑與設定 ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
# 專案根 => 加入 src
SRC_PATH = os.path.join(PROJECT_ROOT, 'src')
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from src.config import get_settings  # noqa
from src.db import Base  # noqa
# 確保 models 被 Import（若集中在一檔即可；若拆檔需在此 import 以便 autogenerate）
import src.models  # noqa

settings = get_settings()

# --- 2. Alembic config 物件 ---
config = context.config

# 覆寫 sqlalchemy.url
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 設定 log
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 目標 metadata
target_metadata = Base.metadata


def run_migrations_offline():
    """離線模式（輸出 SQL）"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,        # 若型別改變也偵測
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """在線模式（直接對 DB 執行）"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="",
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
