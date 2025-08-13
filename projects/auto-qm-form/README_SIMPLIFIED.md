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
