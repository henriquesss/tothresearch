#!/usr/bin/env bash
# Brings the whole stack up on a separate compose project with a fresh volume,
# checks it, and always tears it down. The developer's default stack and its
# data volume are never touched: the smoke project uses its own host ports.
set -euo pipefail

cd "$(dirname "$0")/.."

export COMPOSE_PROJECT_NAME=toth-smoke
export DB_PORT="${SMOKE_DB_PORT:-55432}"
export API_PORT="${SMOKE_API_PORT:-58000}"
export WEB_PORT="${SMOKE_WEB_PORT:-55173}"
# Equivalent of `cp .env.example .env` on a fresh clone.
export TOTH_ENV_FILE=.env.example

HEALTH_BODY='{"status":"ok","database":"ok"}'

compose() { docker compose -p "$COMPOSE_PROJECT_NAME" "$@"; }
teardown() { compose down -v --remove-orphans >/dev/null 2>&1 || true; }
fail() {
  echo "not ok - $1"
  compose logs --tail 50 >&2 || true
  exit 1
}
trap teardown EXIT

teardown
compose build -q >/dev/null

start=$(date +%s)
compose up -d >/dev/null 2>&1 || fail "compose up"
status=""
while (($(date +%s) - start < 90)); do
  status=$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:${API_PORT}/api/health" || true)
  [[ "$status" == "200" ]] && break
  sleep 1
done
[[ "$status" == "200" ]] || fail "api health 200 within 90s (last status: ${status:-none})"
echo "ok - api health 200 within 90s"

current=$(compose exec -T api alembic current 2>/dev/null || true)
[[ "$current" == *"0001_baseline (head)"* ]] || fail "migrations at head after start (got: $current)"
echo "ok - migrations at head after start"

body=""
for _ in $(seq 1 60); do
  body=$(curl -s "http://localhost:${WEB_PORT}/api/health" || true)
  [[ "$body" == "$HEALTH_BODY" ]] && break
  sleep 1
done
[[ "$body" == "$HEALTH_BODY" ]] || fail "web proxies /api/health (got: ${body:-nothing})"
echo "ok - web proxies /api/health"
