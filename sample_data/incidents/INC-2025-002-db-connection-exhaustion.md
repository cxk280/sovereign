# INC-2025-002 — orders Postgres connection exhaustion (SYNTHETIC)

**Severity:** SEV1 · **Duration:** 26m · **Service:** orders-api / orders-pg · **Author:** DB on-call

## Summary
orders-api began throwing connection errors; ~30% of order creations failed with 500s. Root cause was
Postgres connection exhaustion after a well-intentioned pool change.

## Timeline
- 09:12 — A change raised orders-api `max_size` from 10 to 25 to "reduce pool wait."
- 09:20 — Deploy completes across 10 replicas → 250 requested connections vs. the 200 cluster limit.
- 09:24 — New connections rejected; 500s climb; SEV1 declared.
- 09:38 — Reverted `max_size` to 10 (`deploy-rollback.md`); connections drain; errors clear.

## Root cause
Total connections = replicas × `max_size`. 10 × 25 = 250 > 200 limit. The per-replica change ignored
the cluster-wide budget documented in `runbooks/database-failover.md`.

## Follow-ups
- Add a CI check asserting `replicas × max_size < cluster_limit` (backlog).
- Document the connection budget inline in `db.py` (done — see the comment on `max_size`).

## Lessons
Pool sizing is a **cluster-wide** budget, not a per-replica knob. Always compute replicas × max_size
against the limit before changing it.
