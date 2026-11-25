# Foundation Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, the walk, check_proofs, the Verifier and the screens sub-agent).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Design**: none - Medium scope; stack and layout are fixed by `PRD.md` §5 and the spec's Assumptions table
**Status**: Approved
**Approved**: 2026-11-25 - user: "Approve, use sub-agents"
**Build**: `pnpm build; pnpm typecheck; pnpm lint`
**Run api**: `docker compose up -d --wait db && cd api && .venv/bin/pytest -v`
**Run web**: `pnpm --filter @toth/web exec vitest run --reporter=verbose`
**Run shared**: `pnpm --filter @toth/shared exec vitest run --reporter=verbose`
**Run smoke**: `bash scripts/smoke.sh`
**Run testcmd**: `bash scripts/check-test-command.sh`

Greenfield note: the `Build` line cannot be green before T1–T10 create the packages it runs. `validate_tasks.py --execute` will report it red before T1; that is expected on an empty repo, and the Build gate first applies from T10 onward.

Root scripts (created in T1, filled as packages appear):
- `pnpm build` → `pnpm -r build` (shared, web)
- `pnpm typecheck` → `pnpm -r typecheck && cd api && .venv/bin/mypy app`
- `pnpm lint` → `pnpm -r lint && cd api && .venv/bin/ruff check app tests`
- `pnpm test` → `pnpm -r test && docker compose up -d --wait db && cd api && .venv/bin/pytest`

---

## Test Coverage Matrix

> Generated from the spec - the repo has no tests yet. Guidelines found: none - strong defaults applied. Test types and runners follow the spec (FND-19): pytest for the API, Vitest for web and shared, shell smoke scripts for compose and the root test command.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| API core (config, errors, db guard) | unit | All branches; 1:1 to spec ACs; every listed edge case | `api/tests/test_*.py` | `cd api && .venv/bin/pytest -v` |
| API routes (health) | integration (real Postgres test DB) | happy + DB-unavailable path | `api/tests/test_health.py` | `docker compose up -d --wait db && cd api && .venv/bin/pytest -v` |
| Migrations | integration | upgrade head + downgrade base on the test DB | `api/tests/test_migrations.py` | same as above |
| Repo / compose config | unit (file assertions) | every structural AC (layout, compose dependency, env example) | `api/tests/test_repo_*.py`, `api/tests/test_compose.py` | same as above |
| Web pages and routing | unit (Vitest + Testing Library) | every route and control in scope | `apps/web/src/**/*.test.tsx` | `pnpm --filter @toth/web exec vitest run` |
| Shared package | unit | exported values exactly as specified | `packages/shared/src/*.test.ts` | `pnpm --filter @toth/shared exec vitest run` |
| Running stack | smoke (shell, real compose) | each stack AC prints one `ok -` line | `scripts/smoke.sh` | `bash scripts/smoke.sh` |
| Root test command | smoke (shell) | all suites run; non-zero on a failing test | `scripts/check-test-command.sh` | `bash scripts/check-test-command.sh` |
| Dockerfiles, workspace manifests | none | - (build gate + smoke) | - | build gate |

## Gate Check Commands

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | Tasks with API unit tests, or web/shared unit tests | `cd api && .venv/bin/pytest -q` / `pnpm --filter <pkg> test` |
| Full | Tasks touching the DB, compose or the stack | `pnpm test` (and `bash scripts/smoke.sh` from T12 on) |
| Build | After each phase and from T10 on | `pnpm build; pnpm typecheck; pnpm lint` |

---

## Execution Plan

Phases run sequentially; tasks within a phase run in order.

### Phase 1: Workspace and API core

```
T1 → T2 → T3 → T4 → T5 → T6 → T7
```

### Phase 2: Web and shared

```
T8 → T9 → T10
```

### Phase 3: Stack and tooling

```
T11 → T12 → T13 → T14
```

---

## Task Breakdown

### T1: Create the pnpm workspace root

**What**: `.gitignore` (node_modules, `.venv`, `.env`, `__pycache__`, dist), `pnpm-workspace.yaml` (`apps/*`, `packages/*`), root `package.json` with the build/typecheck/lint/test scripts above, `.nvmrc` (22).
**Where**: repository root
**Depends on**: None
**Reuses**: PRD §5.1 layout
**Requirement**: FND-05, FND-19

**Done when**:

- [x] `pnpm install` exits 0

**Tests**: none
**Gate**: `pnpm install` exits 0 (no code layer yet)
**Commit**: `chore: create pnpm workspace root`

---

### T2: Create the FastAPI project skeleton

**What**: `api/requirements.txt` (fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic, pydantic-settings, python-dotenv), `api/requirements-dev.txt` (pytest, pytest-asyncio, httpx, ruff, mypy, pyyaml), `api/pyproject.toml` (ruff, mypy, pytest config), package dirs `api/app/{agents,orchestration,services,repositories,models,schemas,api,core}/__init__.py`, and `api/app/main.py` with `create_app()`.
**Where**: `api/app/main.py`
**Depends on**: T1
**Reuses**: -
**Requirement**: FND-05

**Done when**:

- [x] `api/.venv` installs both requirement files
- [x] `tests/test_app.py::test_create_app_returns_fastapi_app` passes
- [x] `ruff check` and `mypy app` exit 0

**Tests**: unit
**Gate**: quick
**Commit**: `feat(api): add FastAPI project skeleton`

---

### T3: Load settings from the environment

**What**: `Settings` (pydantic-settings) declaring `DATABASE_URL` (required), `TEST_DATABASE_URL`, `OPENROUTER_API_KEY`, `ADMIN_API_KEY`, `SESSION_SECRET`, `LOG_LEVEL`; startup exits non-zero naming any missing required variable; `.env.example` with every declared variable, a placeholder and a comment.
**Where**: `api/app/core/config.py`
**Depends on**: T2
**Reuses**: -
**Requirement**: FND-11, FND-12

**Done when**:

- [x] `test_config.py`: starting the app in a subprocess with `DATABASE_URL` unset exits non-zero and stderr contains `DATABASE_URL`
- [x] `test_config.py`: the set of `Settings` fields equals the set of variables in `.env.example`, and each has a comment line
- [x] Gate passes; test count: 3

**Tests**: unit
**Gate**: quick
**Commit**: `feat(api): load settings from environment`

---

### T4: Return a fixed error envelope

**What**: Exception handlers registered in `create_app()`: unhandled → 500 `{"error":"internal_error","message":"An unexpected error occurred."}` with the traceback logged at ERROR; unmatched `/api` path → 404 `{"error":"not_found","message":"Resource not found."}`.
**Where**: `api/app/core/errors.py`
**Depends on**: T3
**Reuses**: `create_app()` from T2
**Requirement**: FND-08, FND-09, FND-10

**Done when**:

- [x] `test_errors.py` mounts a test-only route that raises `RuntimeError("secret /path detail")`: response is 500 with the exact body, and the body contains neither `RuntimeError`, `secret`, `/path` nor `Traceback`
- [x] `test_errors.py`: the same request logs an ERROR record whose text contains `Traceback` (caplog)
- [x] `test_errors.py`: `GET /api/does-not-exist` returns 404 with the exact body
- [x] Gate passes; test count: 6

**Tests**: unit
**Gate**: quick
**Commit**: `feat(api): add safe error envelope`

---

### T5: Add the database engine, test database and its guard

**What**: Async engine/session factory; `docker-compose.yml` with the `db` service (postgres:16, healthcheck `pg_isready`, init script creating `toth_test`); `api/tests/conftest.py` that loads the root `.env`, aborts the session when `TEST_DATABASE_URL` is unset or equals `DATABASE_URL` (message names both), and gives tests an engine on `TEST_DATABASE_URL`.
**Where**: `api/app/core/db.py`
**Depends on**: T4
**Reuses**: `Settings` from T3
**Requirement**: FND-21, FND-23

**Done when**:

- [ ] `test_db_guard.py`: the guard raises with a message containing `TEST_DATABASE_URL` and `DATABASE_URL` when the URLs are equal
- [ ] `test_db_guard.py`: the fixture engine's database name is the one in `TEST_DATABASE_URL` and differs from `DATABASE_URL`'s
- [ ] Gate passes; test count: 8

**Tests**: unit
**Gate**: full
**Commit**: `feat(api): add database engine and guarded test database`

---

### T6: Add the health endpoint

**What**: `GET /api/health` runs `SELECT 1` with a 2-second timeout: 200 `{"status":"ok","database":"ok"}` or 503 `{"status":"degraded","database":"unavailable"}`.
**Where**: `api/app/api/health.py`
**Depends on**: T5
**Reuses**: session factory from T5, error envelope from T4
**Requirement**: FND-06, FND-07

**Done when**:

- [ ] `test_health.py`: with the test DB, the response is 200 with the exact body
- [ ] `test_health.py`: with the engine pointed at an unreachable port, the response is 503 with the exact body within 3 seconds
- [ ] Gate passes; test count: 10

**Tests**: integration
**Gate**: full
**Commit**: `feat(api): add health endpoint`

---

### T7: Configure Alembic with a baseline revision

**What**: Async `alembic.ini` + `env.py` reading `DATABASE_URL` from `Settings`, and an empty baseline revision `0001_baseline` that later features build on.
**Where**: `api/alembic/env.py`
**Depends on**: T6
**Reuses**: `Settings` from T3
**Requirement**: FND-03

**Done when**:

- [ ] `test_migrations.py`: `alembic upgrade head` then `alembic downgrade base` against `TEST_DATABASE_URL` both exit 0, and `alembic current` reports `0001_baseline` between them
- [ ] Gate passes; test count: 11; Build gate on the API half (`mypy`, `ruff`) green

**Tests**: integration
**Gate**: full
**Commit**: `feat(api): configure alembic with baseline revision`

---

### T8: Create the shared package with agent ids

**What**: `@toth/shared` exporting `AGENT_TYPES` as a readonly tuple of the seven ids in workflow order, its `AgentType` union, and build/typecheck/lint/test scripts.
**Where**: `packages/shared/src/index.ts`
**Depends on**: None within phase (Phase 1 complete)
**Reuses**: -
**Requirement**: FND-18

**Done when**:

- [ ] `index.test.ts`: `AGENT_TYPES` equals exactly `fundamental_analyst, market_analyst, news_sentiment_analyst, geopolitical_analyst, risk_analyst, compliance_analyst, portfolio_manager` in that order
- [ ] Gate passes; test count: 1

**Tests**: unit
**Gate**: quick
**Commit**: `feat(shared): export agent type ids`

---

### T9: Scaffold the web app with Vite, Tailwind and shadcn/ui

**What**: `@toth/web` with React + TypeScript + Vite, Tailwind CSS, shadcn/ui initialised with the `Button` component, Vitest + Testing Library, ESLint; `vite.config.ts` with `envPrefix: 'VITE_'` and a `/api` proxy to `http://localhost:8000` (overridable by `API_PROXY_TARGET` for compose).
**Where**: `apps/web/vite.config.ts`
**Depends on**: T8
**Reuses**: -
**Requirement**: FND-13, FND-04

**Done when**:

- [ ] `env.test.ts`: the Vite config's `envPrefix` is `VITE_`, and no `VITE_` variable in the root `.env.example` contains `KEY`, `SECRET` or `TOKEN`
- [ ] `env.test.ts`: the Vite config proxies `/api` to the configured target
- [ ] Gate passes; test count: 2

**Tests**: unit
**Gate**: quick
**Commit**: `feat(web): scaffold vite app with tailwind and shadcn`

---

### T10: Add routing, the home page and the not-found page

**What**: `App` with `QueryClientProvider` and React Router: `/` renders the "Toth Research" heading, a shadcn `Button` and the agent count from `@toth/shared`; `*` renders "Page not found" with a link to `/`.
**Where**: `apps/web/src/App.tsx`
**Depends on**: T9
**Reuses**: `Button` from T9, `AGENT_TYPES` from T8
**Requirement**: FND-14, FND-15, FND-16, FND-17, FND-18

**Done when**:

- [ ] `App.test.tsx`: `/` shows a heading "Toth Research"
- [ ] `App.test.tsx`: `/nope` shows "Page not found"
- [ ] `App.test.tsx`: clicking the not-found link shows the "Toth Research" heading
- [ ] `App.test.tsx`: `/` renders an element produced by the shadcn `Button` and the text "7 specialized agents" derived from `AGENT_TYPES.length`
- [ ] `stack.test.ts`: `apps/web/package.json` depends on react, react-router, @tanstack/react-query, tailwindcss and `@toth/shared` (`workspace:*`)
- [ ] Build gate green (`pnpm build; pnpm typecheck; pnpm lint`); test count: web 7

**Tests**: unit
**Gate**: build
**Commit**: `feat(web): add routes, home and not-found pages`

---

### T11: Containerise the API and web app

**What**: `api/Dockerfile` (entrypoint `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0`), `apps/web/Dockerfile` (Vite dev server on 0.0.0.0:5173), and `api` + `web` services in `docker-compose.yml`; `api` `depends_on: db: condition: service_healthy`; `web` gets `API_PROXY_TARGET=http://api:8000`.
**Where**: `docker-compose.yml`
**Depends on**: None within phase (Phase 2 complete)
**Reuses**: `db` service from T5
**Requirement**: FND-02, FND-22

**Done when**:

- [ ] `test_compose.py`: `api.depends_on.db.condition` is `service_healthy` and `db` defines a healthcheck
- [ ] `test_compose.py`: the `api` entrypoint runs `alembic upgrade head` before `uvicorn`
- [ ] `docker compose build` exits 0; full gate passes

**Tests**: unit
**Gate**: full
**Commit**: `feat: containerise api and web in docker compose`

---

### T12: Add the stack smoke script

**What**: `scripts/smoke.sh` brings the stack up on a fresh project name and volume, then prints one `ok -` line per check and exits non-zero on the first failure; always tears down.
**Where**: `scripts/smoke.sh`
**Depends on**: T11
**Reuses**: -
**Requirement**: FND-01, FND-02, FND-04

**Done when**:

- [ ] Prints `ok - api health 200 within 90s` (fresh volume, `cp .env.example .env` equivalent)
- [ ] Prints `ok - migrations at head after start` (`alembic current` in the api container shows `0001_baseline`)
- [ ] Prints `ok - web proxies /api/health` (`curl localhost:5173/api/health` returns the API body)
- [ ] Exits 0

**Tests**: smoke
**Gate**: full
**Commit**: `test: add docker compose smoke script`

---

### T13: Verify the root test command

**What**: `scripts/check-test-command.sh` runs `pnpm test`, asserts the output shows the pytest, web Vitest and shared Vitest summaries, then for each suite adds a temporary failing test, asserts `pnpm test` exits non-zero, and removes it (trap on exit).
**Where**: `scripts/check-test-command.sh`
**Depends on**: T12
**Reuses**: root `test` script from T1
**Requirement**: FND-19, FND-20

**Done when**:

- [ ] Prints `ok - pnpm test runs api, web and shared suites`
- [ ] Prints `ok - pnpm test exits non-zero when an api test fails`, `... a web test fails`, `... a shared test fails`
- [ ] Leaves `git status` clean

**Tests**: smoke
**Gate**: full
**Commit**: `test: verify root test command`

---

### T14: Assert the repository layout and document setup

**What**: `test_repo_layout.py` asserting every PRD §5.1 path in FND-05; `README.md` with prerequisites, `cp .env.example .env`, `docker compose up`, `pnpm test`.
**Where**: `api/tests/test_repo_layout.py`
**Depends on**: T13
**Reuses**: -
**Requirement**: FND-05

**Done when**:

- [ ] `test_repo_layout.py::test_prd_layout_exists` passes
- [ ] Build gate, `pnpm test`, `bash scripts/smoke.sh` and `bash scripts/check-test-command.sh` all green

**Tests**: unit
**Gate**: build
**Commit**: `docs: assert repo layout and document setup`

---

## Checks

**C1** - `docker compose up` from a fresh volume serves `GET :8000/api/health` 200 within 90 s (FND-01, AC 1)
Proof: run smoke | ok - api health 200 within 90s

**C2** - The api container applies migrations to `head` on start against an empty database (FND-02, AC 2)
Proof: run smoke | ok - migrations at head after start

**C3** - `alembic upgrade head` then `alembic downgrade base` both exit 0 (FND-03, AC 3)
Proof: run api | test_migrations.py::test_upgrade_head_then_downgrade_base PASSED

**C4** - `GET :5173/api/health` returns the API's health body through the Vite proxy (FND-04, AC 4)
Proof: run smoke | ok - web proxies /api/health

**C5** - Every PRD §5.1 path exists (FND-05, AC 5)
Proof: run api | test_repo_layout.py::test_prd_layout_exists PASSED

**C6** - Health with a reachable DB returns 200 `{"status":"ok","database":"ok"}` (FND-06, AC 1)
Proof: run api | test_health.py::test_health_ok_when_database_answers PASSED

**C7** - Health with an unreachable DB returns 503 `{"status":"degraded","database":"unavailable"}` within 3 s (FND-07, AC 2)
Proof: run api | test_health.py::test_health_503_when_database_unreachable PASSED

**C8** - An unhandled exception returns 500 with the exact generic body and no exception type, message, path or traceback (FND-08, AC 3)
Proof: run api | test_errors.py::test_unhandled_exception_returns_generic_500 PASSED

**C9** - An unhandled exception's traceback is logged at ERROR (FND-09, AC 4)
Proof: run api | test_errors.py::test_unhandled_exception_logs_traceback PASSED

**C10** - An unmatched `/api` path returns 404 `{"error":"not_found","message":"Resource not found."}` (FND-10, AC 5)
Proof: run api | test_errors.py::test_unknown_api_path_returns_404_envelope PASSED

**C11** - Starting the API with `DATABASE_URL` unset exits non-zero naming `DATABASE_URL` (FND-11, AC 1)
Proof: run api | test_config.py::test_missing_database_url_exits_naming_it PASSED

**C12** - `.env.example` lists exactly the declared settings, each with a comment (FND-12, AC 2)
Proof: run api | test_config.py::test_env_example_matches_settings PASSED

**C13** - The browser sees only `VITE_` variables and none of them is a key, secret or token (FND-13, AC 3)
Proof: run web | ✓ src/env.test.ts > exposes only VITE_ variables and no secrets

**C14** - `/` renders the heading "Toth Research" (FND-14, AC 1)
Proof: run web | ✓ src/App.test.tsx > renders the Toth Research heading on /

**C15** - An unknown path renders "Page not found" with a link to `/` (FND-15, AC 2)
Proof: run web | ✓ src/App.test.tsx > renders Page not found on an unknown path

**C16** - Using the not-found link shows the "Toth Research" heading (FND-16, AC 3)
Proof: run web | ✓ src/App.test.tsx > not-found link navigates home

**C17** - The web app uses the PRD stack and renders a shadcn `Button` on `/` (FND-17, AC 4)
Proof: run web | ✓ src/App.test.tsx > renders a shadcn button on /

**C18** - `AGENT_TYPES` is exactly the seven ids in workflow order (FND-18, AC 5)
Proof: run shared | ✓ src/index.test.ts > AGENT_TYPES lists the seven agents in workflow order

**C19** - `pnpm test` runs the api, web and shared suites (FND-19, AC 1)
Proof: run testcmd | ok - pnpm test runs api, web and shared suites

**C20** - `pnpm test` exits non-zero when any one suite has a failing test (FND-20, AC 2)
Proof: run testcmd | ok - pnpm test exits non-zero when an api test fails

**C21** - API tests use the database named by `TEST_DATABASE_URL`, never `DATABASE_URL` (FND-21, AC 3)
Proof: run api | test_db_guard.py::test_fixture_engine_uses_test_database PASSED

**C22** - The api service waits for the db health check (FND-22, edge)
Proof: run api | test_compose.py::test_api_waits_for_healthy_db PASSED

**C23** - Equal `TEST_DATABASE_URL` and `DATABASE_URL` abort the suite with a message naming both (FND-23, edge)
Proof: run api | test_db_guard.py::test_guard_rejects_equal_urls PASSED

---

## Handoff

**Settled mid-build:** 2026-11-25 - repository creation removed from T1; this plan does not create the repository (user: "in the phase 1, remove the github repo creation"); 2026-11-25 - the user creates the repository and each task is committed locally, never pushed (user: "1")
**Dispatched:** batch 1 (Phase 1, T1–T7) worker - at HEAD: none (unborn branch `feature/foundation`) - 2026-11-25
**Walked:** none

---

## Phase Execution Map

```
Phase 1 → Phase 2 → Phase 3

Phase 1:  T1 → T2 → T3 → T4 → T5 → T6 → T7
Phase 2:  T8 → T9 → T10
Phase 3:  T11 → T12 → T13 → T14
```

14 tasks pack into two batches: Phase 1 (7 tasks), then Phases 2 + 3 (7 tasks).
