# ADR-0001 — Decompose the monolith by order lifecycle stage (SYNTHETIC)

**Status:** Accepted · **Date:** 2024-11 · **Deciders:** Fulfillment, Platform

## Context
The original monolith coupled intake, inventory, and fulfillment. A single slow query in fulfillment
could stall order intake, and teams could not deploy independently.

## Decision
Split along order-lifecycle boundaries: **orders-api** (intake + reservation), **inventory** (stock),
**fulfillment** (post-reservation). Communicate via a durable **order-events** queue for the
asynchronous handoff; keep synchronous calls only where an immediate answer is required (inventory
reservation at order time).

## Consequences
- (+) Independent deploys; intake stays up if fulfillment is degraded.
- (+) Clear ownership boundaries and blast radius.
- (−) Distributed-systems complexity: eventual consistency between reservation and fulfillment,
  addressed with the event queue and idempotent consumers.
- Reservation stays **synchronous** at intake to avoid overselling — the one place we accept coupling.
