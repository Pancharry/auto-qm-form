# scripts/init_test_db.py
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from urllib.parse import urlparse

TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://appuser:apppass@localhost:5432/auto_qm_test"
)

def ensure_db(url):
    u = urlparse(url)
    dbname = u.path.lstrip("/")
    admin_conn = psycopg2.connect(
        dbname="postgres",
        user=u.username,
        password=u.password,
        host=u.hostname,
        port=u.port or 5432,
    )
    admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = admin_conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (dbname,))
    if not cur.fetchone():
        cur.execute(f'CREATE DATABASE "{dbname}" OWNER {u.username}')
        print(f"Created test database {dbname}")
    else:
        print(f"Test database {dbname} already exists")
    cur.close()
    admin_conn.close()

if __name__ == "__main__":
    ensure_db(TEST_DB_URL)
