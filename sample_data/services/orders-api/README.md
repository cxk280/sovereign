# orders-api (synthetic)

Fictional order-intake microservice for **Meridian Logistics**. Python / FastAPI / asyncpg on Postgres.

- `app.py` — HTTP routes: create order (reserves inventory transactionally), fetch order, health.
- `models.py` — Pydantic models and the `OrderStatus` state enum.
- `db.py` — asyncpg pool, deliberately sized under the cluster connection limit.

Owned by the (fictional) **Fulfillment** team. On-call: `runbooks/orders-api-oncall.md`.
