import pytest
from src.db import reset_engine_for_test, SessionLocal
from alembic.config import Config
from alembic import command
import os

TEST_URL = os.getenv("TEST_DATABASE_URL", "postgresql+psycopg2://appuser:apppass@localhost:5432/auto_qm_test")

@pytest.fixture(scope="session", autouse=True)
def migrate():
    cfg = Config("alembic.ini")
    # 用 -x db_url 優先；也可直接 set_main_option
    command.upgrade(cfg, "head", sql=False, tag=None)
    reset_engine_for_test(TEST_URL)
    yield

@pytest.fixture
def db_session():
    with SessionLocal() as s:
        tx = s.begin()
        try:
            yield s
        finally:
            tx.rollback()
