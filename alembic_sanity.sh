#!/usr/bin/env bash
set -euo pipefail

COLOR_RED="\033[31m"
COLOR_GREEN="\033[32m"
COLOR_YELLOW="\033[33m"
COLOR_RESET="\033[0m"

echo -e "${COLOR_YELLOW}[Alembic Sanity] 檢查開始...${COLOR_RESET}"

# 1. 驗證基本指令存在
if ! command -v alembic >/dev/null 2>&1; then
  echo -e "${COLOR_RED}未找到 alembic 指令，請啟動虛擬環境或安裝依賴。${COLOR_RESET}"
  exit 1
fi

# 2. 取得 heads
HEADS_OUTPUT=$(alembic heads 2>&1 || true)
HEAD_COUNT=$(echo "$HEADS_OUTPUT" | grep -Eo '^[0-9a-f]+' | wc -l | tr -d ' ')

if [ "$HEAD_COUNT" -gt 1 ]; then
  echo -e "${COLOR_RED}偵測到多個 heads (${HEAD_COUNT})，需人工合併：${COLOR_RESET}"
  echo "$HEADS_OUTPUT"
  echo "建議：alembic merge -m 'merge heads' <head1> <head2> ..."
  exit 2
fi

HEAD_REV=$(echo "$HEADS_OUTPUT" | grep -Eo '^[0-9a-f]+' || true)
if [ -z "$HEAD_REV" ]; then
  echo -e "${COLOR_RED}無法解析 head revision，請檢查 migrations/versions。${COLOR_RESET}"
  exit 3
fi

# 3. 取得 current
CURRENT_OUTPUT=$(alembic current 2>&1 || true)
CURRENT_REV=$(echo "$CURRENT_OUTPUT" | grep -Eo '^[0-9a-f]+' || true)

if echo "$CURRENT_OUTPUT" | grep -qi "FAILED"; then
  echo -e "${COLOR_RED}alembic current 執行失敗：${COLOR_RESET}"
  echo "$CURRENT_OUTPUT"
  exit 4
fi

if [ -z "$CURRENT_REV" ]; then
  echo -e "${COLOR_YELLOW}目前 DB 沒有版本（可能是全新或未 stamp）。${COLOR_RESET}"
  echo "可選：alembic upgrade head 或若表已存在且一致 → alembic stamp head"
  exit 0
fi

# 4. 比較
if [ "$CURRENT_REV" != "$HEAD_REV" ]; then
  echo -e "${COLOR_YELLOW}DB 落後：current=$CURRENT_REV head=$HEAD_REV${COLOR_RESET}"
  if [ "${AUTO_UPGRADE:-0}" = "1" ]; then
    echo "AUTO_UPGRADE=1 → 自動升級中..."
    alembic upgrade head
    echo -e "${COLOR_GREEN}升級完成。${COLOR_RESET}"
  else
    echo "請執行：alembic upgrade head"
  fi
  exit 0
fi

echo -e "${COLOR_GREEN}[Alembic Sanity] OK：current == head ($HEAD_REV)。${COLOR_RESET}"