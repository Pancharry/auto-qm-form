# 建立CI前的測試角本 20250814 取消
# from src.db import SessionLocal
# from src.models import MaterialEquipment

# def main():
#     with SessionLocal() as db:
#         obj = MaterialEquipment(name="測試A", type="material", category="CAT1")
#         db.add(obj)
#         db.commit()
#         db.refresh(obj)
#         print("Inserted ID:", obj.id)

# if __name__ == "__main__":
#    main()

# test_db.py 20250814
"""
用途：
  驗證測試資料庫連線、基本查詢、指定資料表存在、Alembic 版本一致性。
使用：
  python test_db.py --url postgresql+psycopg2://user:pass@localhost:5432/dbname --expect-table users --check-alembic
參數說明：
  --url / -u             : 指定資料庫 URL，未提供則讀環境 TEST_DATABASE_URL -> DATABASE_URL
  --expect-table / -t    : 可多次指定需存在的資料表
  --check-alembic        : 檢查 alembic_version 與 migrations 最新 head 是否一致
  --alembic-dir          : migrations 目錄（預設 migrations）
  --max-retries          : 連線最大重試次數（預設 8）
  --interval             : 每次重試間隔秒數（預設 1.5）
  --json                 : 以 JSON 輸出結果（適合機器解析）
  --verbose / -v         : 顯示更詳細過程
退出碼：
  0: 全部成功
  1: 連線或檢查失敗
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from typing import List, Optional

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, ProgrammingError

# Alembic 檢查需要讀取 migrations/versions 內的檔案名稱
def load_latest_alembic_head(alembic_dir: str) -> Optional[str]:
    versions_dir = os.path.join(alembic_dir, "versions")
    if not os.path.isdir(versions_dir):
        return None
    revs = []
    for fname in os.listdir(versions_dir):
        if fname.endswith(".py") and "_" in fname:
            rev = fname.split("_")[0]
            if len(rev) >= 6:
                revs.append((os.path.getmtime(os.path.join(versions_dir, fname)), rev))
    if not revs:
        return None
    # 以修改時間排序取最後一個
    revs.sort(key=lambda x: x[0])
    return revs[-1][1]


@dataclass
class CheckResult:
    url: str
    connected: bool
    tables_checked: List[str]
    tables_missing: List[str]
    alembic_db_rev: Optional[str]
    alembic_fs_head: Optional[str]
    alembic_match: Optional[bool]
    elapsed_seconds: float
    retries: int
    error: Optional[str] = None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Test DB connectivity & schema sanity.")
    p.add_argument("--url", "-u", help="Database URL (override env)")
    p.add_argument("--expect-table", "-t", action="append", default=[], help="Expected table name (repeatable)")
    p.add_argument("--check-alembic", action="store_true", help="Check alembic head match")
    p.add_argument("--alembic-dir", default="migrations", help="Alembic migrations directory")
    p.add_argument("--max-retries", type=int, default=8, help="Max connection retries")
    p.add_argument("--interval", type=float, default=1.5, help="Seconds between retries")
    p.add_argument("--json", action="store_true", help="Output JSON only")
    p.add_argument("--verbose", "-v", action="store_true")
    return p.parse_args()


def resolve_url(cli_url: Optional[str]) -> str:
    if cli_url:
        return cli_url
    env_url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not env_url:
        raise SystemExit("No --url provided and TEST_DATABASE_URL / DATABASE_URL not set.")
    return env_url


def connect_with_retry(url: str, max_retries: int, interval: float, verbose: bool) -> tuple[Optional[Engine], int, Optional[str]]:
    last_err = None
    engine = None
    for attempt in range(1, max_retries + 1):
        if verbose:
            print(f"[connect] Attempt {attempt}/{max_retries} ...")
        try:
            engine = create_engine(url, pool_pre_ping=True)
            # 實際開連線
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine, attempt, None
        except OperationalError as e:
            last_err = str(e)
            if verbose:
                print(f"[connect] OperationalError: {e}")
            time.sleep(interval)
        except Exception as e:  # noqa: BLE001
            last_err = str(e)
            if verbose:
                print(f"[connect] Generic error: {e}")
            time.sleep(interval)
    return None, max_retries, last_err


def check_tables(engine: Engine, expected: List[str], verbose: bool) -> List[str]:
    if not expected:
        return []
    inspector = inspect(engine)
    existing = set(inspector.get_table_names())
    missing = [t for t in expected if t not in existing]
    if verbose:
        print(f"[tables] existing={sorted(existing)}; missing={missing}")
    return missing


def read_alembic_db_revision(engine: Engine, verbose: bool) -> Optional[str]:
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT version_num FROM alembic_version"))
            row = res.fetchone()
            if row:
                if verbose:
                    print(f"[alembic] DB revision={row[0]}")
                return row[0]
            return None
    except ProgrammingError:
        if verbose:
            print("[alembic] alembic_version table not found")
        return None
    except Exception as e:  # noqa: BLE001
        if verbose:
            print(f"[alembic] error reading version: {e}")
        return None


def main():
    args = parse_args()
    start = time.time()
    url = resolve_url(args.url)

    engine, retries, err = connect_with_retry(url, args.max_retries, args.interval, args.verbose)
    if engine is None:
        result = CheckResult(
            url=url,
            connected=False,
            tables_checked=args.expect_table,
            tables_missing=args.expect_table,
            alembic_db_rev=None,
            alembic_fs_head=None,
            alembic_match=None,
            elapsed_seconds=time.time() - start,
            retries=retries,
            error=err,
        )
        emit(result, args.json)
        sys.exit(1)

    missing = check_tables(engine, args.expect_table, args.verbose)

    alembic_db_rev = None
    alembic_fs_head = None
    alembic_match = None

    if args.check_alembic:
        alembic_db_rev = read_alembic_db_revision(engine, args.verbose)
        alembic_fs_head = load_latest_alembic_head(args.alembic_dir)
        if alembic_db_rev and alembic_fs_head:
            alembic_match = (alembic_db_rev.startswith(alembic_fs_head)
                             or alembic_fs_head.startswith(alembic_db_rev)
                             or alembic_db_rev == alembic_fs_head)

    result = CheckResult(
        url=url,
        connected=True,
        tables_checked=args.expect_table,
        tables_missing=missing,
        alembic_db_rev=alembic_db_rev,
        alembic_fs_head=alembic_fs_head,
        alembic_match=alembic_match,
        elapsed_seconds=time.time() - start,
        retries=retries,
        error=None if not missing else ("Missing tables: " + ",".join(missing)),
    )

    # 決定是否失敗
    exit_fail = False
    if missing:
        exit_fail = True
    if args.check_alembic and alembic_db_rev and alembic_fs_head and not alembic_match:
        result.error = (result.error + " | " if result.error else "") + "Alembic head mismatch"
        exit_fail = True

    emit(result, args.json)
    sys.exit(1 if exit_fail else 0)


def emit(result: CheckResult, as_json: bool):
    if as_json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
        return
    print("=== DB CHECK RESULT ===")
    print(f"URL               : {result.url}")
    print(f"Connected         : {result.connected}")
    print(f"Retries Used      : {result.retries}")
    print(f"Elapsed (s)       : {result.elapsed_seconds:.2f}")
    print(f"Tables Checked    : {result.tables_checked}")
    print(f"Tables Missing    : {result.tables_missing}")
    print(f"Alembic DB Rev    : {result.alembic_db_rev}")
    print(f"Alembic FS Head   : {result.alembic_fs_head}")
    print(f"Alembic Match     : {result.alembic_match}")
    print(f"Error             : {result.error}")


if __name__ == "__main__":
    main()