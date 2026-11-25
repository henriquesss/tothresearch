# Foundation Specification

**Approved**: 2026-11-25 - user: "approved, go ahead with the tasks"

## Problem Statement

Toth Research has a PRD and no code. Every later feature (auth, data, agents, orchestration, UI) needs the same base: a pnpm monorepo with a FastAPI API, a React web app, PostgreSQL with migrations, configuration from the environment, and one test command. Building that base once, with the PRD's security rules for errors and secrets in place from the first commit, keeps every later feature small.

## Goals

- [ ] `docker compose up` brings up Postgres, the API and the web app from a fresh clone plus a copied `.env`, with no manual step.
- [ ] One root command, `pnpm test`, runs the API and web test suites and exits non-zero when either fails.
- [ ] The API reports its own and the database's health, and never leaks internals in an error.

## Out of Scope

| Feature | Reason |
| ------- | ------ |
| Domain tables (User, Invitation, Company, Analysis, …) | Each feature migrates its own tables (`auth-invitations`, `company-lookup`, `orchestration`) |
| Authentication, landing page content, dashboard screens | Features 2, 6, 8 in `ROADMAP.md` |
| OpenRouter, yfinance, GDELT integration | Features 3 and 4 |
| Cloud deployment, CI pipeline | AD-005: local docker-compose only |
| Production web build served by nginx | Local MVP runs the Vite dev server in compose |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Runtime versions | Python 3.12, Node 22 LTS, pnpm 9, PostgreSQL 16 | Current stable releases supported by FastAPI, LangGraph and Vite | n |
| Python dependency management | `api/requirements.txt` (runtime) + `api/requirements-dev.txt` (tests, lint), installed into `api/.venv` | The PRD's tree names `requirements.txt` | n |
| Database driver | SQLAlchemy 2.x async with `asyncpg`; Alembic configured for async | FastAPI and SSE handlers are async; one driver for app and migrations | n |
| Where migrations run | The API container runs `alembic upgrade head` before starting uvicorn | Satisfies "no manual step" on a fresh database | n |
| Health endpoint path and body | `GET /api/health` → `200 {"status":"ok","database":"ok"}`; DB unreachable → `503 {"status":"degraded","database":"unavailable"}` | One endpoint compose and the web shell can both call | n |
| Generic error body | Unhandled exception → `500 {"error":"internal_error","message":"An unexpected error occurred."}`; the traceback goes to the server log only | PRD §9: sensitive errors must not expose internals | n |
| Unknown API route | `404 {"error":"not_found","message":"Resource not found."}` | Same envelope as other errors | n |
| Required configuration | `DATABASE_URL` is required at startup; `OPENROUTER_API_KEY`, `ADMIN_API_KEY`, `SESSION_SECRET` are declared in settings and `.env.example` but only required by the features that use them | The API must boot in the foundation before those features exist | n |
| Web shell content | `/` shows a "Toth Research" placeholder page; any unknown path shows a "Page not found" page with a link to `/` | Real pages come in features 6–8 | n |
| `packages/shared` content | Exports `AGENT_TYPES`: the seven agent ids in workflow order (`fundamental_analyst`, `market_analyst`, `news_sentiment_analyst`, `geopolitical_analyst`, `risk_analyst`, `compliance_analyst`, `portfolio_manager`), consumed by `apps/web` | Gives the shared package a real purpose and fixes the agent ids the SSE events use (PRD §8 uses `geopolitical_analyst`) | n |
| Ports | Postgres 5432, API 8000, web 5173; Vite proxies `/api` to the API | Defaults of each tool; same-origin `/api` avoids CORS for cookie auth later | n |
| Lint and type checks in the build | `ruff check` + `mypy` on `api/app`; `tsc --noEmit` + `eslint` on web and shared | The gate's build line catches type errors before tests | n |
| Version control | No task creates the repository; T1 only adds `.gitignore`. The user owns repository creation | user: "in the phase 1, remove the github repo creation" | y |

**Open questions:** none - all resolved or logged above. Product decisions for later features are recorded in `.specs/STATE.md` (AD-001…AD-005) and `.specs/ROADMAP.md`.

---

## User Stories

### P1: Run the whole stack locally ⭐ MVP

**User Story**: As the developer, I want one command to start the database, API and web app so that every feature is built and tested against the same environment.

**Why P1**: Nothing else can be built or demonstrated without it.

**Acceptance Criteria**:

1. WHEN the developer runs `docker compose up` from a fresh clone with `.env` copied from `.env.example` THEN the system SHALL start the `db`, `api` and `web` services and `GET http://localhost:8000/api/health` SHALL return `200` within 90 seconds.
2. WHEN the `api` service starts against an empty database THEN the system SHALL apply every Alembic migration up to `head` before accepting requests.
3. WHEN the developer runs `alembic upgrade head` followed by `alembic downgrade base` THEN both commands SHALL exit 0.
4. WHEN a browser opens `http://localhost:5173/api/health` THEN the web dev server SHALL proxy the request to the API and return the API's health body.
5. The repository SHALL follow the PRD §5.1 layout: `apps/web`, `api/app/{agents,orchestration,services,repositories,models,schemas,api,core}`, `api/tests`, `packages/shared`, `docker-compose.yml`, `pnpm-workspace.yaml`, root `package.json`, `.env.example`, `README.md`.

**Independent Test**: From a clean checkout, copy `.env.example` to `.env`, run `docker compose up`, then `curl localhost:8000/api/health` returns `{"status":"ok","database":"ok"}`.

---

### P1: Health and safe errors ⭐ MVP

**User Story**: As the developer, I want the API to report its health and to answer every error with a fixed envelope so that later features inherit safe error handling.

**Why P1**: PRD §9 requires that sensitive errors never expose internals; establishing it once prevents every endpoint from re-deciding it.

**Acceptance Criteria**:

1. WHEN a client calls `GET /api/health` and the database answers `SELECT 1` THEN the API SHALL return `200` with body `{"status":"ok","database":"ok"}`.
2. IF the database does not answer `SELECT 1` within 2 seconds THEN the API SHALL return `503` with body `{"status":"degraded","database":"unavailable"}`.
3. IF a request handler raises an unhandled exception THEN the API SHALL return `500` with body `{"error":"internal_error","message":"An unexpected error occurred."}` and the body SHALL contain no exception type, message, file path or traceback.
4. WHEN a request handler raises an unhandled exception THEN the API SHALL write the traceback to the server log at ERROR level.
5. IF a client requests a path under `/api` that matches no route THEN the API SHALL return `404` with body `{"error":"not_found","message":"Resource not found."}`.

**Independent Test**: Run the API tests: health with a live DB, health with an unreachable DB URL, a test-only route that raises, and an unknown path.

---

### P1: Configuration from the environment ⭐ MVP

**User Story**: As the developer, I want all settings read from environment variables with a documented example file so that secrets never live in code.

**Why P1**: PRD §5.4 and §9 require API keys in environment variables and never in the frontend.

**Acceptance Criteria**:

1. IF `DATABASE_URL` is unset when the API starts THEN the API SHALL exit with a non-zero code and an error message that names `DATABASE_URL`.
2. The `.env.example` file SHALL list every variable the API settings declare, with a placeholder value and a one-line comment each.
3. The web app's Vite configuration SHALL expose to the browser only variables prefixed `VITE_`, and `.env.example` SHALL define no `VITE_` variable containing `KEY`, `SECRET` or `TOKEN`.

**Independent Test**: Start the API with `DATABASE_URL` unset and read the error; run the settings test that compares declared settings with `.env.example`.

---

### P1: Web application shell ⭐ MVP

**User Story**: As the developer, I want a React app with routing, data fetching and the design-system toolkit wired up so that screens in later features only add pages.

**Why P1**: Features 2, 6, 7 and 8 all add pages to this shell.

**Acceptance Criteria**:

1. WHEN a visitor opens `/` THEN the web app SHALL render a page whose heading reads "Toth Research".
2. WHEN a visitor opens a path that matches no route THEN the web app SHALL render a page reading "Page not found" with a link to `/`.
3. WHEN a visitor uses the "Page not found" page's link THEN the web app SHALL navigate to `/` and render the "Toth Research" heading.
4. The web app SHALL use React, TypeScript, Vite, Tailwind CSS, shadcn/ui, React Router and TanStack Query, with one shadcn/ui component installed and rendered on the `/` page.
5. The `packages/shared` package SHALL export `AGENT_TYPES` as exactly the seven ids `fundamental_analyst`, `market_analyst`, `news_sentiment_analyst`, `geopolitical_analyst`, `risk_analyst`, `compliance_analyst`, `portfolio_manager`, in that order, and `apps/web` SHALL import it from the workspace package.

**Independent Test**: Run the web tests: render `/`, render `/nope`, click the link back; run the shared package test on `AGENT_TYPES`.

---

### P1: One test command ⭐ MVP

**User Story**: As the developer, I want `pnpm test` at the root to run every suite so that each task's gate is one command.

**Why P1**: The workflow's gate needs one command that the test runner, not judgement, decides.

**Acceptance Criteria**:

1. WHEN the developer runs `pnpm test` at the repository root THEN the system SHALL run the API pytest suite, the web Vitest suite and the shared package tests.
2. IF any of those suites has a failing test THEN `pnpm test` SHALL exit with a non-zero code.
3. WHEN the API test suite runs THEN it SHALL use a separate test database named by `TEST_DATABASE_URL`, never the database named by `DATABASE_URL`.

**Independent Test**: Run `pnpm test` green; add a deliberately failing test in one suite and confirm the exit code is non-zero.

---

## Edge Cases

- IF the database is still starting when the API container starts THEN the `api` service SHALL wait for the `db` health check to pass before running migrations (compose `depends_on: condition: service_healthy`).
- IF `TEST_DATABASE_URL` equals `DATABASE_URL` THEN the API test suite SHALL abort before running any test with a message naming both variables.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| FND-01 | P1: Run the whole stack locally — AC1 compose up + health | Tasks | Pending |
| FND-02 | P1: Run the whole stack locally — AC2 migrations on start | Tasks | Pending |
| FND-03 | P1: Run the whole stack locally — AC3 upgrade/downgrade | Tasks | Implementing |
| FND-04 | P1: Run the whole stack locally — AC4 Vite proxy | Tasks | Pending |
| FND-05 | P1: Run the whole stack locally — AC5 repo layout | Tasks | Implementing |
| FND-06 | P1: Health and safe errors — AC1 healthy | Tasks | Implementing |
| FND-07 | P1: Health and safe errors — AC2 DB unavailable 503 | Tasks | Implementing |
| FND-08 | P1: Health and safe errors — AC3 generic 500 body | Tasks | Implementing |
| FND-09 | P1: Health and safe errors — AC4 traceback logged | Tasks | Implementing |
| FND-10 | P1: Health and safe errors — AC5 404 envelope | Tasks | Implementing |
| FND-11 | P1: Configuration — AC1 missing DATABASE_URL | Tasks | Implementing |
| FND-12 | P1: Configuration — AC2 .env.example complete | Tasks | Implementing |
| FND-13 | P1: Configuration — AC3 no secrets exposed to browser | Tasks | Pending |
| FND-14 | P1: Web shell — AC1 home heading | Tasks | Pending |
| FND-15 | P1: Web shell — AC2 not found page | Tasks | Pending |
| FND-16 | P1: Web shell — AC3 link back home | Tasks | Pending |
| FND-17 | P1: Web shell — AC4 frontend stack | Tasks | Pending |
| FND-18 | P1: Web shell — AC5 AGENT_TYPES | Tasks | Pending |
| FND-19 | P1: One test command — AC1 runs all suites | Tasks | Implementing |
| FND-20 | P1: One test command — AC2 non-zero on failure | Tasks | Pending |
| FND-21 | P1: One test command — AC3 separate test DB | Tasks | Implementing |
| FND-22 | Edge: api waits for db health | Tasks | Pending |
| FND-23 | Edge: test DB guard | Tasks | Implementing |

**Coverage:** 23 total, 0 mapped to tasks, 23 unmapped ⚠️ (mapped in `tasks.md` after approval)

---

## Sources

- `PRD.md` v0.2 §5.1–5.5 (layout, stack, database), §9 (errors, secrets), §12 phase 1 - what the foundation must contain
- `.specs/STATE.md` AD-001…AD-005, `.specs/ROADMAP.md` - decisions taken while planning on 2026-11-25

---

## Success Criteria

- [ ] Fresh clone to healthy stack with `cp .env.example .env && docker compose up` and nothing else.
- [ ] `pnpm test` green at the end of the feature, and red when any single test fails.
