# foundation proofs

**HEAD**: 25c45ed
**Tree**: clean
**Shell**: /bin/sh
**Result**: 26 pass, 0 fail

| Check | Proof | Result |
| --- | --- | --- |
| C1 | `run smoke / ok - api health 200 within 90s` | pass |
| C2 | `run smoke / ok - migrations at head after start` | pass |
| C3 | `run api / test_migrations.py::test_upgrade_head_then_downgrade_base PASSED` | pass |
| C4 | `run smoke / ok - web proxies /api/health` | pass |
| C5 | `run api / test_repo_layout.py::test_prd_layout_exists PASSED` | pass |
| C6 | `run api / test_health.py::test_health_ok_when_database_answers PASSED` | pass |
| C7 | `run api / test_health.py::test_health_503_when_database_unreachable PASSED` | pass |
| C8 | `run api / test_errors.py::test_unhandled_exception_returns_generic_500 PASSED` | pass |
| C9 | `run api / test_errors.py::test_unhandled_exception_logs_traceback PASSED` | pass |
| C10 | `run api / test_errors.py::test_unknown_api_path_returns_404_envelope PASSED` | pass |
| C11 | `run api / test_config.py::test_missing_database_url_exits_naming_it PASSED` | pass |
| C12 | `run api / test_config.py::test_env_example_matches_settings PASSED` | pass |
| C13 | `run web / ✓ src/env.test.ts > exposes only VITE_ variables and no secrets` | pass |
| C14 | `run web / ✓ src/App.test.tsx > renders the Toth Research heading on /` | pass |
| C15 | `run web / ✓ src/App.test.tsx > renders Page not found on an unknown path` | pass |
| C16 | `run web / ✓ src/App.test.tsx > not-found link navigates home` | pass |
| C17 | `run web / ✓ src/App.test.tsx > renders a shadcn button on /` | pass |
| C18 | `run shared / ✓ src/index.test.ts > AGENT_TYPES lists the seven agents in workflow order` | pass |
| C19 | `run testcmd / ok - pnpm test runs api, web and shared suites` | pass |
| C20 | `run testcmd / ok - pnpm test exits non-zero when an api test fails` | pass |
| C21 | `run api / test_db_guard.py::test_fixture_engine_uses_test_database PASSED` | pass |
| C22 | `run api / test_compose.py::test_api_waits_for_healthy_db PASSED` | pass |
| C23 | `run api / test_db_guard.py::test_guard_rejects_equal_urls PASSED` | pass |
| Build | `pnpm build` | pass |
| Build | `pnpm typecheck` | pass |
| Build | `pnpm lint` | pass |

## Output

`Run smoke` - exit 0

```
ok - api health 200 within 90s
ok - migrations at head after start
ok - web proxies /api/health
```

`Run api` - exit 0

```
tests/test_health.py::test_health_ok_when_database_answers PASSED        [ 78%]
tests/test_health.py::test_health_503_when_database_unreachable PASSED   [ 85%]
tests/test_migrations.py::test_upgrade_head_then_downgrade_base PASSED   [ 92%]
tests/test_repo_layout.py::test_prd_layout_exists PASSED                 [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /Users/lucashenriques/Projects/fun/toth_research/api/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 14 passed, 1 warning in 2.09s =========================
 Container toth_research-db-1  Running
 Container toth_research-db-1  Waiting
 Container toth_research-db-1  Healthy
```

`Run web` - exit 0

```
RUN  v5.1.2 /Users/lucashenriques/Projects/fun/toth_research/apps/web

 ✓ src/stack.test.ts > depends on the PRD frontend stack and the shared workspace package 1ms
 ✓ src/env.test.ts > exposes only VITE_ variables and no secrets 2ms
 ✓ src/env.test.ts > proxies /api to the configured target 0ms
 ✓ src/App.test.tsx > renders the Toth Research heading on / 41ms
 ✓ src/App.test.tsx > renders Page not found on an unknown path 4ms
 ✓ src/App.test.tsx > not-found link navigates home 18ms
 ✓ src/App.test.tsx > renders a shadcn button on / 2ms

 Test Files  3 passed (3)
      Tests  7 passed (7)
   Start at  17:07:45
   Duration  837ms (environment 39%, setup 37%, import 15%, tests 5%, transform 3%, worker 1%)
```

`Run shared` - exit 0

```
RUN  v5.1.2 /Users/lucashenriques/Projects/fun/toth_research/packages/shared

 ✓ src/index.test.ts > AGENT_TYPES lists the seven agents in workflow order 1ms

 Test Files  1 passed (1)
      Tests  1 passed (1)
   Start at  17:07:46
   Duration  90ms (import 45%, transform 27%, worker 16%, tests 12%, environment 1%)
```

`Run testcmd` - exit 0

```
ok - pnpm test runs api, web and shared suites
ok - pnpm test exits non-zero when an api test fails
ok - pnpm test exits non-zero when a web test fails
ok - pnpm test exits non-zero when a shared test fails
```
