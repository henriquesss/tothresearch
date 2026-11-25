# LESSONS - auto-maintained by scripts/lessons.py

> Machine-owned. Do NOT hand-edit. Changes are overwritten on the next `lessons.py` write.
> Canonical state lives in `.specs/lessons.json`. Edit lessons only via the script.
> promote_threshold=2 distinct features · window_days=45 · quarantine_threshold=2

## Confirmed (load these at Plan/Checks)

Corroborated across multiple features. Safe to apply as guidance.

_none_

## Candidates (under observation - do NOT load as guidance yet)

Seen once or not yet corroborated. Tracked, not trusted.

### L-001 - A timeout criterion needs a test against a peer that never replies, not a refused connection.
- signal: `weak_test` · recurrence: 1 feature(s) · scope: `api-tests` · harmful: 0
- features: foundation
- evidence: C7 / verification F1 (api-tests)
- last seen: 2026-11-25T20:28:08Z

### L-002 - A no-echo error criterion must cover custom validator messages and submitted key names, not only the input field.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `api-errors` · harmful: 0
- features: foundation
- evidence: FND-25 / verification F12 (api-errors)
- last seen: 2026-11-25T20:28:08Z

### L-003 - When a criterion says the suite aborts, test the session hook in a subprocess, not the helper it calls.
- signal: `weak_test` · recurrence: 1 feature(s) · scope: `api-tests` · harmful: 0
- features: foundation
- evidence: C23 / verification F3 (api-tests)
- last seen: 2026-11-25T20:28:08Z

### L-004 - Compare database identity after parsing host, port and name, never raw URL strings.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `api-tests` · harmful: 0
- features: foundation
- evidence: FND-21 / verification F2 (api-tests)
- last seen: 2026-11-25T20:28:09Z

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
