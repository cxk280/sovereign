# Meridian Logistics — system overview (SYNTHETIC)

Fictional architecture used as sample context. Meridian runs a set of small services behind an API
gateway; **orders-api** is the intake point for the order lifecycle.

## Core services
- **storefront** — customer web/app; calls orders-api to place orders.
- **orders-api** — validates orders, reserves inventory, records the order (system of record: Postgres
  `orders-pg`). See `services/orders-api/`.
- **inventory** — authoritative stock levels; exposes `reserve_inventory`.
- **fulfillment** — picks/packs/ships reserved orders; consumes an order-events queue.

## Data & messaging
- **orders-pg** — Postgres cluster (primary + 2 replicas), connection limit 200. System of record for
  orders (see ADR-0002).
- **order-events** — durable queue; orders-api publishes `OrderReserved`, fulfillment subscribes.

## Cross-cutting
- All services expose `/healthz`, emit Prometheus metrics, and deploy via GitLab CI/CD with canary +
  expand/contract migrations (`runbooks/deploy-rollback.md`).
