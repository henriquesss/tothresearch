# Toth Research — Roadmap

Source: `PRD.md` v0.2. Each feature gets its own `features/<name>/spec.md` when work reaches it, written against the code that exists by then. Build order follows dependencies.

| # | Feature | Delivers (PRD refs) | Depends on | Status |
|---|---------|---------------------|------------|--------|
| 1 | `foundation` | pnpm monorepo, docker-compose (Postgres, API, web), FastAPI app + config + health + safe error responses, Alembic, Vite/React/Tailwind/shadcn/Router/Query shell, `packages/shared`, one `pnpm test` (§5.1–5.5, §12 phase 1) | — | Spec drafted |
| 2 | `auth-invitations` | User/Invitation tables, admin-key invitation endpoint, redeem-invitation registration, login/logout/me, session cookie, protected routes, login + register screens (§3.2, §7 auth, §9) | 1 | Not started |
| 3 | `company-lookup` | Provider interfaces, yfinance + GDELT adapters, ticker validation/market detection, `GET /api/companies/search`, Company table, data collection + normalization service (§3.4 steps 1–3, §5.6) | 1, 2 | Not started |
| 4 | `agents` | OpenRouter LLM service (per-agent model config, token tracking, timeouts), seven agents with system prompts and typed Pydantic outputs, structured-output validation (§4.1, §4.4, §5.4) | 3 | Not started |
| 5 | `orchestration` | LangGraph workflow (collect → 4 parallel → risk → compliance → PM), Analysis/AgentExecution/AnalysisReport/Source tables, retries, partial-failure rule (AD-003), limits, restart recovery (AD-002), analyses REST + SSE (§4.2–4.3, §7, §8, §10) | 4 | Not started |
| 6 | `dashboard` | Header/nav/logout, new-analysis flow (search → confirm → start), live agent panel with reconnect, expandable findings, analysis history (§3.3–3.5) | 5 | Not started |
| 7 | `report-view` | Final report page: 11 sections, sources with timestamps, data limitations, fact/interpretation/scenario labelling, disclaimer (§3.5, §14) | 6 | Not started |
| 8 | `landing-page` | Public marketing page inspired by decade.com: hero, how it works, agent team, example analysis, footer + disclaimer (§3.1) | 1 | Not started |
| 9 | `hardening` | Observability summary per run (§10), security pass (§9), end-to-end test of MVP acceptance criteria 1–17 (§11) | 1–8 | Not started |

## Settled for later features

Recorded now so they are not asked again; each lands in its feature's spec.

- Rate limit: at most 10 analyses started per user per rolling 24 h; starting a ticker already running for that user returns the running analysis (user: "10/day + one per ticker (Recommended)") → `orchestration`.
- Default model for all seven agents: `anthropic/claude-sonnet-5.5` on OpenRouter, overridable per agent by env var (user: "anthropic/claude-sonnet-5.5 (Recommended)") → `agents`.
- decade.com is inspiration, not a binding design: the PRD says "Use Decade's visual language as inspiration" → `landing-page`.
- Providers, runner, partial failure, language, deployment: AD-001…AD-005 in `STATE.md`.
