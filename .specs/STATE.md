# STATE

## Decisions

### AD-001
- **Decision**: yfinance is the primary data provider for both markets (company profile, financial statements, prices, company news; B3 tickers via the `.SA` suffix) and GDELT supplies geopolitical events; both sit behind provider interfaces in `api/app/services/`.
- **Reason**: Free, one library covers US and B3 for every financial category; GDELT is the free global event feed. User chose it over brapi.dev + FMP + a paid news API ("yfinance + GDELT (Recommended)").
- **Trade-off**: yfinance is unofficial and rate-limited, with no licensing guarantee; acceptable for an invite-only MVP, and the provider abstraction lets a paid provider replace it without touching agents.
- **Scope**: company-lookup, data collection, every agent's input
- **Date**: 2026-11-25
- **Status**: active

### AD-002
- **Decision**: Analyses run in-process as asyncio background tasks inside the FastAPI process; every status change is persisted to Postgres before its SSE event is published; on API startup, analyses and agent executions left `running` are marked `failed` with reason `interrupted`.
- **Reason**: Meets "never block HTTP" and "reconnect to ongoing executions" with no extra infrastructure. User chose it over a Redis + arq worker ("In-process asyncio (Recommended)").
- **Trade-off**: An API restart kills running analyses, and the API cannot scale to several processes without moving to a queue.
- **Scope**: orchestration, SSE, dashboard monitoring
- **Date**: 2026-11-25
- **Status**: active

### AD-003
- **Decision**: When one of the four parallel analysts fails after its retries, the run continues: Risk, Compliance and Portfolio Manager run with that gap, the report lists it as a data limitation, and the analysis ends `completed_with_errors`. Only a Portfolio Manager failure (or a failed data collection) ends the analysis `failed`.
- **Reason**: One flaky provider should not waste a whole run. User chose it over failing the whole analysis ("Continue, flag gap (Recommended)").
- **Trade-off**: Reports can be produced with a missing perspective; the status set gains a fifth value.
- **Scope**: orchestration, agents, report, dashboard status display
- **Date**: 2026-11-25
- **Status**: active

### AD-004
- **Decision**: All UI, agent prompts, agent findings and reports are English only, for both markets.
- **Reason**: One language for prompts, schemas and tests. User chose it over pt-BR or per-market language ("English always (Recommended)").
- **Trade-off**: Brazilian users read B3 reports in English.
- **Scope**: every feature
- **Date**: 2026-11-25
- **Status**: active

### AD-005
- **Decision**: The MVP runs only locally through `docker compose`; no cloud deployment is planned.
- **Reason**: User chose it ("Local docker-compose only (Recommended)").
- **Trade-off**: No hosted environment for invited users until a later deployment feature.
- **Scope**: foundation, every feature's infrastructure
- **Date**: 2026-11-25
- **Status**: active

## Handoff
