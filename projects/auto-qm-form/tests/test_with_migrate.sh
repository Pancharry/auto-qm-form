#!/usr/bin/env bash
# scripts/test_with_migrate.sh
set -euo pipefail

: "${TEST_DATABASE_URL:=postgresql+psycopg2://appuser:apppass@localhost:5432/auto_qm_test}"

python scripts/init_test_db.py

echo "[Alembic upgrade]"
alembic -x db_url="$TEST_DATABASE_URL" upgrade head

echo "[Run pytest]"
pytest -q
