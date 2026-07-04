# INC-2025-001 — orders-api latency spike during flash sale (SYNTHETIC)

**Severity:** SEV2 · **Duration:** 41m · **Service:** orders-api · **Author:** Fulfillment on-call

## Summary
During a flash sale, orders-api p95 latency rose from 180ms to 1.4s. No elevated error rate. Customers
saw slow checkouts; no orders were lost.

## Timeline
- 14:02 — Flash sale begins; request rate 6×.
- 14:09 — p95 latency alert fires.
- 14:15 — On-call rules out a recent deploy (last deploy 3 days prior).
- 14:28 — `reserve_inventory` stored-proc timing identified as the bottleneck under contention.
- 14:43 — Traffic normalizes post-sale; latency recovers without intervention.

## Root cause
`reserve_inventory` takes a row lock per SKU; under 6× concurrency on hot SKUs, lock waits serialized
reservations. The service was healthy — the DB proc was the constraint.

## Follow-ups
- Add per-SKU reservation latency to the dashboard (done).
- Evaluate optimistic reservation for hot SKUs (backlog).
- Pre-scale reads before announced sales (added to `deploy-rollback.md` pre-sale checklist).

## Lessons
Not every latency spike is a deploy regression. Correlate with traffic and downstream (DB) timing
before rolling back — see `runbooks/orders-api-oncall.md`.
