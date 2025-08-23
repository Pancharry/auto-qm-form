#!/usr/bin/env bash
set -euo pipefail

# === 基本設定 ===
DB_NAME="${POSTGRES_DB:-auto_qm}"
DB_USER="${POSTGRES_USER:-appuser}"
DB_PASS="${POSTGRES_PASSWORD:-apppass}"
DB_CONTAINER="${DB_CONTAINER:-autoqm-postgres}"
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
FORCE_INITIAL_PATCH="${FORCE_INITIAL_PATCH:-0}"

COLOR_RED="\033[31m"; COLOR_GRN="\033[32m"; COLOR_YEL="\033[33m"; COLOR_CYAN="\033[36m"; COLOR_DIM="\033[2m"; COLOR_RST="\033[0m"
die(){ echo -e "${COLOR_RED}[X] $*${COLOR_RST}" >&2; exit 1; }
info(){ echo -e "${COLOR_CYAN}[i]${COLOR_RST} $*"; }
ok(){ echo -e "${COLOR_GRN}[✓]${COLOR_RST} $*"; }
warn(){ echo -e "${COLOR_YEL}[!]${COLOR_RST} $*"; }

[ -f alembic.ini ] || die "請在專案根目錄執行（找不到 alembic.ini）"
[ -d migrations ] || die "找不到 migrations/ 目錄"

# 檢查容器
if ! docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}\$"; then
  warn "資料庫容器 ${DB_CONTAINER} 不在執行。"
  docker ps
  die "請確認 DB_CONTAINER。"
fi

# 驅動自動偵測
if [ -n "${DB_DRIVER:-}" ]; then
  DETECTED_DRIVER="${DB_DRIVER}"
else
  if python - <<'PY' >/dev/null 2>&1
import importlib; importlib.import_module("psycopg")
PY
  then
    DETECTED_DRIVER="postgresql+psycopg"
  elif python - <<'PY' >/dev/null 2>&1
import importlib; importlib.import_module("psycopg2")
PY
  then
    DETECTED_DRIVER="postgresql+psycopg2"
  else
    die "未安裝 psycopg 或 psycopg2： pip install 'psycopg[binary]' 或 pip install psycopg2-binary"
  fi
fi

EXPORT_DATABASE_URL="${DETECTED_DRIVER}://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

info "使用設定："
echo -e "  DB_CONTAINER = ${COLOR_DIM}${DB_CONTAINER}${COLOR_RST}"
echo -e "  DB_NAME      = ${COLOR_DIM}${DB_NAME}${COLOR_RST}"
echo -e "  DB_USER      = ${COLOR_DIM}${DB_USER}${COLOR_RST}"
echo -e "  DB_HOST      = ${COLOR_DIM}${DB_HOST}${COLOR_RST}"
echo -e "  DB_PORT      = ${COLOR_DIM}${DB_PORT}${COLOR_RST}"
echo -e "  DB_DRIVER    = ${COLOR_DIM}${DETECTED_DRIVER}${COLOR_RST}"
echo -e "  DATABASE_URL = ${COLOR_DIM}${EXPORT_DATABASE_URL}${COLOR_RST}"

if [ "${FORCE_YES:-}" != "1" ]; then
  echo
  read -r -p "⚠ 此動作會刪除並重建 '${DB_NAME}'，繼續？(yes/NO) " ans
  [[ "$ans" =~ ^([Yy]([Ee][Ss])?)$ ]] || die "使用者取消"
fi

# 備份
BACKUP_FILE="backup_before_reinit_$(date +%Y%m%d_%H%M%S).sql"
if [ "${SKIP_BACKUP:-}" != "1" ]; then
  info "備份到 ${BACKUP_FILE}"
  if docker exec -e PGPASSWORD="${DB_PASS}" -i "${DB_CONTAINER}" \
      pg_dump -U "${DB_USER}" -d "${DB_NAME}" -F p > "${BACKUP_FILE}" 2>/dev/null; then
    ok "備份完成"
  else
    warn "備份失敗或資料庫不存在，忽略。"
    rm -f "${BACKUP_FILE}" || true
  fi
else
  warn "跳過備份"
fi

# 重建 DB
info "終止連線並重建 DB"
docker exec -e PGPASSWORD="${DB_PASS}" -it "${DB_CONTAINER}" \
  psql -U "${DB_USER}" -d postgres -v ON_ERROR_STOP=1 -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='${DB_NAME}';" || true

docker exec -e PGPASSWORD="${DB_PASS}" -it "${DB_CONTAINER}" \
  psql -U "${DB_USER}" -d postgres -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS ${DB_NAME};"
docker exec -e PGPASSWORD="${DB_PASS}" -it "${DB_CONTAINER}" \
  psql -U "${DB_USER}" -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"
ok "資料庫已重建"

# 清空 versions 與 __pycache__
info "清空 migrations/versions 與 __pycache__"
rm -rf migrations/versions
mkdir -p migrations/versions
find migrations -type d -name '__pycache__' -exec rm -rf {} +
ok "versions 目錄重建完成"

export DATABASE_URL="${EXPORT_DATABASE_URL}"

# 產生前檢查是否仍有 revision
info "檢查是否仍有遺留 revision（應為 0）"
python - <<'PY'
from alembic.config import Config
from alembic.script import ScriptDirectory
cfg = Config("alembic.ini")
script = ScriptDirectory.from_config(cfg)
revs = list(script.walk_revisions())
if revs:
  print("⚠ 偵測到仍有 revision：")
  for r in revs:
      print(" -", r.revision, r.doc)
  raise SystemExit(3)
print("（OK）未偵測到舊 revision")
PY
CODE=$?
if [ $CODE -eq 3 ]; then
  die "仍存在 revision（可能多版本路徑 version_locations），請檢查。"
fi

# 驗證 models
info "驗證 models import"
python - <<'PY'
from src.db import Base
from src import models
tables = list(Base.metadata.tables.keys())
print(f"發現 {len(tables)} 個表：")
for t in tables: print(" -", t)
if not tables:
  raise SystemExit("❌ 沒有任何表被載入，請檢查 target_metadata。")
PY
ok "models 載入成功"

# 產生 initial
info "產生 initial"
alembic revision --autogenerate -m "initial"
REV_FILE=$(ls -1 migrations/versions/*_initial.py | tail -n 1 || true)
[ -n "${REV_FILE}" ] || die "未產生 initial 檔案"

info "解析 down_revision（容錯 regex）"
python - "$REV_FILE" "$FORCE_INITIAL_PATCH" <<'PY'
import sys, re, pathlib
rev_path = pathlib.Path(sys.argv[1])
force = sys.argv[2] == "1"
text = rev_path.read_text(encoding="utf-8")
m = re.search(r'^\s*down_revision\s*(:[^=]+)?=\s*(.+)$', text, re.MULTILINE)
if not m:
  print(f"[X] 未找到 down_revision 行：{rev_path}")
  sys.exit(2)
rhs = m.group(2).strip()
# 去掉行尾註解
rhs_clean = rhs.split("#", 1)[0].strip()
print(f"  原始右側：{rhs}")
print(f"  清理後：{rhs_clean}")
is_none = rhs_clean == "None"
if is_none:
  print("[✓] 判定為 None (base)")
  sys.exit(0)
if force:
  print("[!] 強制改寫為 None (FORCE_INITIAL_PATCH=1)")
  new_text = re.sub(r'^(\s*down_revision\s*(:[^=]+)?=\s*)(.+)$',
                    r'\1None', text, flags=re.MULTILINE)
  rev_path.write_text(new_text, encoding="utf-8")
  sys.exit(0)
print(f"[X] down_revision 不是 None：{rhs_clean}")
sys.exit(3)
PY
CODE=$?
if [ $CODE -eq 2 ]; then
  die "initial 檔案內未找到 down_revision 行"
elif [ $CODE -eq 3 ]; then
  die "initial 檔案的 down_revision 不是 None，若確定重置請 export FORCE_INITIAL_PATCH=1 再跑"
fi
ok "down_revision 已確認為 None"

# 確認有 create_table
if grep -q "op.create_table" "${REV_FILE}"; then
  ok "包含 create_table"
else
  warn "未偵測 create_table，可能沒有 ORM Table。"
fi

info "升級 head"
alembic upgrade head
ok "schema 已套用"

info "列出表"
docker exec -e PGPASSWORD="${DB_PASS}" -it "${DB_CONTAINER}" \
  psql -U "${DB_USER}" -d "${DB_NAME}" -c "\dt" || warn "列出表失敗"

info "漂移檢查"
set +e
DRIFT=$(alembic revision --autogenerate -m "post-initial-drift-check" 2>&1)
CODE=$?
set -e
if echo "${DRIFT}" | grep -qi "No changes"; then
  ok "無 drift"
elif [ $CODE -eq 0 ]; then
  warn "有 drift 檔案（檢查差異），輸出："
  echo "${DRIFT}"
else
  warn "drift 檢查異常："
  echo "${DRIFT}"
fi

echo
ok "流程完成"
echo "migrations/versions 內請確認只有 initial (+ 可能 drift-check)"
echo "若使用 FORCE_INITIAL_PATCH=1，請務必確認沒有其他舊 revisions 來源。"