echo "=== alembic.ini (關鍵段落) ==="
grep -nE '^(script_location|version_locations|prepend_sys_path)' alembic.ini || true

echo
echo "=== migrations 目錄結構 ==="
find migrations -maxdepth 3 -type f -name '*.py' -print

echo
echo "=== versions 內層詳細 (含隱藏) ==="
ls -al migrations/versions

echo
echo "=== 尋找所有 revision 定義 ==="
grep -R "revision =" -n .

echo
echo "=== Alembic history (若有) ==="
alembic history --verbose || true

echo
echo "=== env.py 前 120 行 ==="
head -n 120 migrations/env.py

