# Runbook: orders-api on-call (SYNTHETIC)

**Service:** orders-api · **Team:** Fulfillment · **Tier:** 1 (customer-facing)

## Dashboards & alerts
- Grafana: `Fulfillment / orders-api`. Golden signals: request rate, p95 latency, 5xx rate, inventory
  reservation failures.
- Pager triggers: p95 latency > 800ms for 5m; 5xx rate > 2% for 5m; `reserve_inventory` failure rate
  > 5%.

## First response
1. Check the `orders-api` dashboard and recent deploys (`deploy-rollback.md`). A latency or error
   spike within ~15m of a deploy is a rollback candidate.
2. Check Postgres connection saturation. If `pg_stat_activity` is near the cluster limit, see
   `database-failover.md` and INC-2025-002 — do **not** raise `max_size` blindly.
3. If inventory reservations are failing broadly, confirm the `inventory` service is healthy before
   assuming an orders-api bug.

## Common symptoms
- **Elevated p95, low error rate** → usually DB contention or a slow downstream. Check the
  `reserve_inventory` stored-proc timing.
- **409 spike (insufficient stock)** → expected during flash sales; not an orders-api fault.
- **Connection errors on startup** → `ORDERS_DB_DSN` misconfig or the pool never initialized.
