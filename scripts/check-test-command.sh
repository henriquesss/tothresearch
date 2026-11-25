#!/usr/bin/env bash
# Proves that the root `pnpm test` runs the api, web and shared suites and
# exits non-zero when any one of them has a failing test.
set -uo pipefail

cd "$(dirname "$0")/.."

API_FAIL=api/tests/test_zz_check_test_command.py
WEB_FAIL=apps/web/src/zz-check-test-command.test.ts
SHARED_FAIL=packages/shared/src/zz-check-test-command.test.ts
OUT=$(mktemp)

cleanup() { rm -f "$API_FAIL" "$WEB_FAIL" "$SHARED_FAIL" "$OUT"; }
trap cleanup EXIT

fail() {
  echo "not ok - $1"
  tail -40 "$OUT" >&2
  exit 1
}

pnpm test >"$OUT" 2>&1 || fail "pnpm test runs api, web and shared suites (exit non-zero)"
grep -Eq '^packages/shared test: +Tests +[0-9]+ passed' "$OUT" || fail "shared Vitest summary missing"
grep -Eq '^apps/web test: +Tests +[0-9]+ passed' "$OUT" || fail "web Vitest summary missing"
grep -Eq '^=+ [0-9]+ passed.* in [0-9.]+s' "$OUT" || fail "api pytest summary missing"
echo "ok - pnpm test runs api, web and shared suites"

# $1 suite label, $2 article, $3 file to create, $4 contents
expect_failure() {
  printf '%s\n' "$4" >"$3"
  if pnpm test >"$OUT" 2>&1; then
    rm -f "$3"
    fail "pnpm test exits non-zero when $2 $1 test fails (exit 0)"
  fi
  rm -f "$3"
  grep -q "$(basename "$3")" "$OUT" || fail "the failing $1 test did not run"
  echo "ok - pnpm test exits non-zero when $2 $1 test fails"
}

expect_failure api an "$API_FAIL" 'def test_deliberate_failure() -> None:
    assert False'
expect_failure web a "$WEB_FAIL" 'import { expect, it } from "vitest";
it("deliberate failure", () => { expect(1).toBe(2); });'
expect_failure shared a "$SHARED_FAIL" 'import { expect, it } from "vitest";
it("deliberate failure", () => { expect(1).toBe(2); });'
