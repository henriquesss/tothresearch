# Toth Research

Multi-agent equity research: a FastAPI API (`api/`), a React web app (`apps/web`) and a shared TypeScript package (`packages/shared`) in one pnpm workspace, backed by PostgreSQL.

## Prerequisites

- Docker with Docker Compose v2
- Node.js 22+ and pnpm 9 (`corepack enable`)
- Python 3.12 (for running the API tests on the host)

## Run the stack

```bash
cp .env.example .env
docker compose up
```

This starts:

| Service | URL | Notes |
| ------- | --- | ----- |
| `db` | `localhost:5432` | PostgreSQL 16; creates `toth` and the test database `toth_test` |
| `api` | `http://localhost:8000/api/health` | Runs `alembic upgrade head`, then uvicorn |
| `web` | `http://localhost:5173` | Vite dev server; proxies `/api` to the API |

## Run the tests

One-time setup:

```bash
pnpm install
python3.12 -m venv api/.venv
api/.venv/bin/pip install -r api/requirements.txt -r api/requirements-dev.txt
```

Then, from the repository root:

```bash
pnpm test
```

`pnpm test` runs the shared and web Vitest suites, starts the `db` service, and runs the API pytest suite against `TEST_DATABASE_URL` (never `DATABASE_URL`).

Other root commands: `pnpm build`, `pnpm typecheck`, `pnpm lint`.

## Checks

- `bash scripts/smoke.sh` brings the whole stack up on a separate compose project (`toth-smoke`, its own volume and host ports) and checks health, migrations and the web proxy.
- `bash scripts/check-test-command.sh` proves `pnpm test` runs every suite and fails when any one of them fails.
