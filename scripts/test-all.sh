#!/usr/bin/env bash
# Runs the shared, web and api suites even when one fails; exits non-zero if any failed.
set -uo pipefail

cd "$(dirname "$0")/.."

status=0
pnpm -r --if-present --no-bail test || status=1
if docker compose up -d --wait db; then
  (cd api && .venv/bin/pytest) || status=1
else
  status=1
fi
exit "$status"
