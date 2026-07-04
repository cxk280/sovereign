# ADR-0002 — Postgres as the order system of record (SYNTHETIC)

**Status:** Accepted · **Date:** 2024-12 · **Deciders:** Fulfillment, Data

## Context
Orders require strong consistency (no overselling, no lost orders) and transactional inventory
reservation. We evaluated Postgres vs. a document store vs. an event-sourced log.

## Decision
Use **Postgres** (`orders-pg`) as the system of record. Reserve inventory and insert the order in a
single transaction so partial reservations cannot leak. Publish `OrderReserved` to the event queue
after commit.

## Consequences
- (+) ACID reservation + insert; simple mental model; mature operational tooling.
- (+) Read replicas absorb order-status lookups.
- (−) The connection limit is a shared, cluster-wide budget that must be respected by every service —
  violated once in INC-2025-002.
- (−) Hot-SKU row locks can serialize reservations under extreme concurrency — see INC-2025-001.
- Migrations follow **expand/contract** to keep deploys and rollbacks online-safe
  (`runbooks/deploy-rollback.md`).
