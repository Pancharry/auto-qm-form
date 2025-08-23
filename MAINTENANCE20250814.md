# 專案維護與環境記錄手冊
（最後更新：<請填寫日期>）

## 1. 專案概覽
- 類型：FastAPI + SQLAlchemy + Alembic + Pytest
- 主要用途：<簡述系統用途>
- Python 版本：3.12.3
- 虛擬環境：.venv（標準 venv）
- 測試涵蓋率工具：pytest-cov
- 資料庫：
  - 開發 / 執行：PostgreSQL（透過 docker-compose 啟動）
  - 測試：同一 PostgreSQL 服務中的獨立資料庫（建議 auto_qm_test），或 SQLite（備援）
- 目前尚未啟用 Git 版本控制（文件內提供導入步驟）

## 2. 目錄結構（精簡示意）
```
auto-qm-form/
├─ alembic.ini
├─ migrations/
│  ├─ env.py
│  ├─ script.py.mako
│  └─ versions/           # 資料庫版本檔 *.py
├─ src/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ db.py
│  ├─ crud.py
│  ├─ main.py             # FastAPI 入口
│  ├─ models.py
│  ├─ schemas.py
│  └─ prerevision2_db.py  # (舊稿/待整理)
├─ tests/
│  ├─ conftest.py
│  ├─ test_api.py
│  ├─ test_crud.py
│  ├─ test_db.py          # 資料庫檢查腳本
│  └─ test_simple.py
├─ docker-compose.yml
├─ requirements.txt 或 pyproject.toml
├─ pytest.ini
└─ docs/
   └─ MAINTENANCE.md
```

## 3. 重要環境變數
| 名稱 | 用途 | 範例 |
|------|------|------|
| DATABASE_URL | 開發 / 正式資料庫連線 | postgresql+psycopg2://appuser:apppass@localhost:5432/auto_qm |
| TEST_DATABASE_URL | 測試資料庫（覆蓋 DATABASE_URL） | postgresql+psycopg2://appuser:apppass@localhost:5432/auto_qm_test |
| PYTHONPATH | （可選）確保 src 可匯入 | export PYTHONPATH=./ |

建議建立 .env（不提交 Git）：
```
DATABASE_URL=postgresql+psycopg2://appuser:apppass@localhost:5432/auto_qm
TEST_DATABASE_URL=postgresql+psycopg2://appuser:apppass@localhost:5432/auto_qm_test
```

若應用程式也容器化，容器內用服務名稱 postgres：
```
DATABASE_URL=postgresql+psycopg2://appuser:apppass@postgres:5432/auto_qm
```

## 4. 虛擬環境建立與啟動
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # 或：pip install -e . (若使用 pyproject)
```
檢查：
```
which python
python --version
```

## 5. Docker / docker-compose 資料庫服務

### 5.1 docker-compose.yml 內容（摘要）
```
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
      test: ["CMD-SHELL", "pg_isready -U appuser -d auto_qm || exit 1"]
      interval: 5s
      timeout: 5s
      retries: 10
volumes:
  pgdata:
```

說明：
- 指定初始 DB：auto_qm
- 使用命名卷 pgdata 儲存資料（刪除容器不會丟資料）
- healthcheck 確保容器內 Postgres ready 後再進行後續操作

### 5.2 啟動 / 停止 / 查看狀態
```
docker compose up -d postgres
docker compose ps
docker logs -f autoqm-postgres
docker compose stop postgres
docker compose down            # 停止並移除容器（保留卷）
docker compose down -v         # 停止並刪除卷（清空資料！）
```

### 5.3 建立測試資料庫
啟動後建立第二個 DB（僅第一次需要）：
```
docker exec -it autoqm-postgres psql -U appuser -d postgres -c "CREATE DATABASE auto_qm_test OWNER appuser;"
```
驗證：
```
docker exec -it autoqm-postgres psql -U appuser -l | grep auto_qm
```

### 5.4 連線測試
Host（本機）：
```
psql postgresql://appuser:apppass@localhost:5432/auto_qm
```
容器內：
```
docker exec -it autoqm-postgres psql -U appuser -d auto_qm
```

### 5.5 DATABASE_URL / TEST_DATABASE_URL 對應
- 本機直接運行 FastAPI：
  - DATABASE_URL=postgresql+psycopg2://appuser:apppass@localhost:5432/auto_qm
- 若 FastAPI 也進容器（同 docker network）：
  - DATABASE_URL=postgresql+psycopg2://appuser:apppass@postgres:5432/auto_qm

### 5.6 資料備份 / 還原
建立 backup 目錄：
```
mkdir -p backup
```
備份（本機 shell）：
```
TS=$(date +%Y%m%d_%H%M)
docker exec autoqm-postgres pg_dump -U appuser -d auto_qm > backup/auto_qm_$TS.sql
```
還原：
```
cat backup/auto_qm_YYYYmmdd_HHMM.sql | docker exec -i autoqm-postgres psql -U appuser -d auto_qm
```
備份全部（含角色/多 DB 可改用 pg_dumpall）：
```
docker exec autoqm-postgres pg_dumpall -U appuser > backup/all_$TS.sql
```

### 5.7 快速重置（危險）
```
docker compose down -v
docker compose up -d postgres
# 重新建立 test DB
docker exec -it autoqm-postgres psql -U appuser -d postgres -c "CREATE DATABASE auto_qm_test OWNER appuser;"
alembic upgrade head
```

### 5.8 健康檢查觀察
```
docker inspect --format='{{json .State.Health}}' autoqm-postgres | jq
```
沒安裝 jq：
```
docker inspect autoqm-postgres | grep -i health -A5
```

### 5.9 常見容器問題
| 問題 | 現象 | 解法 |
|------|------|------|
| 5432 被占用 | docker compose up 失敗 | 停掉本機原生 postgres 或改 ports |
| 密碼改後登入失敗 | 原容器仍用舊環境變數 | docker compose down -v 後再 up |
| 無法連線 ECONNREFUSED | 應用太快啟動 | 等待 healthcheck 或在 app 啟動加重試 |
| 權限錯誤 | FATAL: password authentication failed | 確認 URL 帳密拼寫 |

### 5.10 在容器啟動後執行遷移
（本機執行）
```
alembic upgrade head
```
或若將 app 容器化，Dockerfile entrypoint 可加入：
```
alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 5.11 容器內執行 Alembic（若未在本機裝套件）
需建立應用容器；暫無 Dockerfile 時，可用一次性映像（建議後續補 Dockerfile）。

### 5.12 （可選）Mac / ARM 相容性
若在 Apple Silicon 遇到映像問題，可明確：
```
services:
  postgres:
    platform: linux/amd64
```

## 6. Alembic 遷移操作
1. 建立新版本：
   ```
   alembic revision -m "describe change"
   ```
2. 自動產生（需在 env.py 設定 target_metadata）：
   ```
   alembic revision --autogenerate -m "add table X"
   ```
3. 升級到最新：
   ```
   alembic upgrade head
   ```
4. 降級一版：
   ```
   alembic downgrade -1
   ```
5. 查看目前版本：
   ```
   alembic current
   ```
6. 歷史：
   ```
   alembic history --verbose
   ```

若測試環境以程式內覆蓋 sqlalchemy.url，請確保 conftest.py 已 set_main_option("sqlalchemy.url", TEST_DATABASE_URL)。

## 7. 測試流程
- 單次執行（於專案根）：
  ```
  pytest -q
  ```
- 含覆蓋率：
  ```
  pytest --cov=src --cov-report=term-missing
  ```
- 指定單檔 / 單測試：
  ```
  pytest tests/test_crud.py::test_create_budget -vv
  ```

### 7.1 常用 pytest 參數
| 參數 | 說明 |
|------|------|
| -q | 安靜模式 |
| -vv | 詳細輸出 |
| -k expr | 只跑符合名稱的測試 |
| -x | 首個失敗即停止 |
| --maxfail=2 | 最多失敗 2 個停止 |
| --lf | 只跑上次失敗 |
| --ff | 先跑上次失敗再其餘 |
| --durations=10 | 顯示最慢 10 個測試 |

### 7.2 測試使用 Docker DB 的注意事項
- 確保 test DB 已建立（auto_qm_test）
- 設 TEST_DATABASE_URL 指向該 DB
- conftest.py 在 session 開始時執行 alembic upgrade head
- 若需 isolation，可在每個測試使用 transaction + rollback

## 8. （範例）test_with_migrate.sh（可選）
```
#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

echo "[info] Python: $(python --version)"
echo "[info] DB URL: ${TEST_DATABASE_URL:-${DATABASE_URL:-'(not set)'}}"

alembic upgrade head
pytest --cov=src --cov-report=term-missing
```

## 9. 常用指令快速表
| 任務 | 指令 |
|------|------|
| 啟動 DB 容器 | docker compose up -d postgres |
| 查看 DB logs | docker logs -f autoqm-postgres |
| 建立測試 DB | docker exec -it autoqm-postgres psql -U appuser -d postgres -c "CREATE DATABASE auto_qm_test OWNER appuser;" |
| 備份 | docker exec autoqm-postgres pg_dump -U appuser -d auto_qm > backup/auto_qm.sql |
| 還原 | cat backup/auto_qm.sql \| docker exec -i autoqm-postgres psql -U appuser -d auto_qm |
| 清空資料（慎用） | docker compose down -v |
| 安裝套件 | pip install -r requirements.txt |
| 遷移升級 | alembic upgrade head |
| 自動產生遷移 | alembic revision --autogenerate -m "..." |
| 測試 | pytest -q |
| 覆蓋率 | pytest --cov=src --cov-report=term-missing |
| 單一測試 | pytest tests/test_api.py::test_health -vv |
| 清除 .pyc | find . -name "__pycache__" -prune -exec rm -rf {} \; |
| 啟動開發伺服器 | uvicorn src.main:app --reload |
| 互動 DB（容器內） | docker exec -it autoqm-postgres psql -U appuser -d auto_qm |

## 10. 問題排查（Troubleshooting）

### 10.1 Alembic: No config file 'alembic.ini'
- 原因：從 tests/ 目錄或錯誤工作目錄執行
- 解法：回專案根；或 conftest.py 使用絕對路徑

### 10.2 DB 連線失敗 (OperationalError)
- 確認 docker compose ps 中 postgres Up
- 確認密碼 / host / port
- 用 psql 測試

### 10.3 Migration 與 Model 不一致
- 自動產生比對：
  ```
  alembic revision --autogenerate -m "sync models"
  alembic upgrade head
  ```
- 手動審查版本檔

### 10.4 覆蓋率低
- 使用 term-missing 找缺口
- 補測例：錯誤路徑 / 例外 / 邊界條件

### 10.5 容器啟動慢
- 檢查 logs
- 健康檢查未通過時延後應用啟動

## 11. 新人上手流程 (Onboarding)
1. （導入 Git 後）clone
2. 啟動 DB：
   ```
   docker compose up -d postgres
   ```
3. 建立 test DB（若尚未）：
   ```
   docker exec -it autoqm-postgres psql -U appuser -d postgres -c "CREATE DATABASE auto_qm_test OWNER appuser;"
   ```
4. 建立 .venv & 安裝：
   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
5. 遷移：
   ```
   alembic upgrade head
   ```
6. 測試：
   ```
   pytest -q
   ```
7. 啟動：
   ```
   uvicorn src.main:app --reload
   ```
8. 瀏覽 API docs：http://127.0.0.1:8000/docs

## 12. Git 導入建議步驟
1. 初始化：
   ```
   git init
   git config user.name "<Your Name>"
   git config user.email "<Your Email>"
   ```
2. 建立 .gitignore
3. 提交：
   ```
   git add .
   git commit -m "chore: initial project import"
   ```
4. 遠端：
   ```
   git branch -M main
   git remote add origin git@github.com:<org>/<repo>.git
   git push -u origin main
   ```

### 建議 .gitignore
```
__pycache__/
*.py[cod]
.venv/
.env
.env.*
.pytest_cache/
.coverage
htmlcov/
*.log
migrations/versions/__pycache__/
.idea/
.vscode/
test.sqlite
backup/
```

## 13. 版本策略（建議）
- 語意化版本：MAJOR.MINOR.PATCH
- Tag：
  ```
  git tag -a v0.1.0 -m "Initial"
  git push origin v0.1.0
  ```

## 14. 安全注意事項
- 密碼放 .env，勿提交
- 資料庫使用 least privilege
- 定期 rotate 密碼（更新 docker 環境變數需重建容器）

## 15. 後續可考慮改進（TODO）
| 項目 | 說明 | 優先度 |
|------|------|--------|
| CI/CD | GitHub Actions 跑測試 + 覆蓋率 | 中 |
| 型別檢查 | mypy / pyright | 中 |
| Lint | ruff / black | 中 |
| 日誌 | structlog / loguru | 低 |
| 設定管理 | Pydantic Settings | 中 |
| App 容器化 | Dockerfile + multi-stage build | 高 |
| 健康檢查強化 | /health 包含 DB ping | 中 |
| Data Seed | 初始資料載入腳本 | 中 |
| Monitoring | Prometheus metrics | 低 |

## 16. pytest 旗標速查
| 指令 | 功能 |
|------|------|
| pytest -k expr | 名稱過濾 |
| pytest -m mark | 依標記 |
| pytest -x | 失敗即停 |
| pytest --maxfail=2 | 指定最大失敗數 |
| pytest --lf | 只跑上次失敗 |
| pytest --ff | 先失敗後其餘 |
| pytest --durations=10 | 慢測試 |
| pytest -q | 簡潔輸出 |

## 17. 常見錯誤訊息備忘錄
| 訊息 | 意義 | 解決 |
|------|------|------|
| No config file 'alembic.ini' | Alembic 找不到設定 | 使用絕對路徑或回專案根 |
| password authentication failed | 帳密錯 / 未更新 | 重設環境變數 / 重建容器 |
| could not connect to server | DB 未啟動或 port 占用 | docker compose up / 更換 port |
| relation "xxx" does not exist | 未遷移 | alembic upgrade head |
| IncompleteRead / timeout | DB 初始化中 | 等待 health check 完成 |

## 18. Dockerfile（示例，後續可加入）
```
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# 可選：執行遷移再啟動
CMD ["bash", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
```

## 19. 聯絡與責任
| 角色 | 人員 | 聯絡方式 |
|------|------|----------|
| 維護負責 | <Name> | <Email> |
| DB Admin | <Name> | <Email> |

（請自行填寫）

---
若需：
- 增補實際 requirements.txt 解析
- 補 CI 範例（GitHub Actions）
- 增加資料初始化 / seed 方案
- 撰寫自動健康檢查端點

請提供對應檔案或需求，我將再擴充本文件。