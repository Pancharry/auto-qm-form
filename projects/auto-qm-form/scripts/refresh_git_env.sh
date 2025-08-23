# scripts/refresh_git_env.sh
#!/usr/bin/env bash
set -euo pipefail

# 確保在 repo 根目錄執行或自動尋找
if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "[ERR] Not inside a git repository." >&2
  exit 1
fi

AUTHOR_NAME="${GIT_AUTHOR_NAME:-$(git config user.name || echo 'Pancharry')}"
AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL:-$(git config user.email || echo 'cahrry.lin@hotmail.com')}"
FULL_SHA=$(git rev-parse HEAD)
SHORT12=$(git rev-parse --short=12 HEAD)
BRANCH=$(git rev-parse --abbrev-ref HEAD)
BUILD_TIME_UTC=$(TZ=UTC date -u +'%Y-%m-%dT%H:%M:%SZ')

cat > .env.git <<EOF
GIT_AUTHOR_NAME=${AUTHOR_NAME}
GIT_AUTHOR_EMAIL=${AUTHOR_EMAIL}
GIT_COMMIT=${FULL_SHA}
GIT_COMMIT_SHORT=${SHORT12}
GIT_BRANCH=${BRANCH}
BUILD_TIME_UTC=${BUILD_TIME_UTC}
EOF

echo "[OK] .env.git generated."
