# Runbook: orders Postgres failover (SYNTHETIC)

**Cluster:** `orders-pg` (primary + 2 replicas) · **Connection limit:** 200

## When to fail over
- Primary unreachable for > 60s, or disk/IO saturation with no recovery trend.
- Prefer an automated failover via the managed control plane; manual promotion is the fallback.

## Manual failover
1. Confirm the primary is truly down (not a network partition from your vantage point only).
2. Promote the most-caught-up replica (check replication lag first).
3. Update the DSN secret; roll `orders-api` so pools reconnect to the new primary.
4. Verify writes succeed and replication re-establishes to the remaining replica.

## Connection budget (read before touching pool sizes)
Total connections = replicas × `max_size`. Current: 10 app replicas × `max_size=10` = 100, half the
200 limit, leaving headroom for migrations and admin. Raising `max_size` without cutting replica count
risks exhaustion — this is exactly what caused INC-2025-002.
