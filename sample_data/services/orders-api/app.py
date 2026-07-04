"""orders-api — Meridian Logistics order intake service (SYNTHETIC / fictional).

Accepts orders from the storefront, validates them, reserves inventory, and
enqueues fulfillment. This is illustrative sample data for RAG/MCP indexing.
"""

from fastapi import FastAPI, HTTPException

from .db import get_pool
from .models import Order, OrderStatus

app = FastAPI(title="orders-api", version="3.2.1")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/orders", status_code=201)
async def create_order(order: Order) -> dict[str, str]:
    if not order.line_items:
        raise HTTPException(status_code=422, detail="order must have at least one line item")

    pool = get_pool()
    async with pool.acquire() as conn:
        # Reserve inventory inside a transaction so partial reservations can't leak.
        async with conn.transaction():
            for item in order.line_items:
                reserved = await conn.fetchval(
                    "SELECT reserve_inventory($1, $2)", item.sku, item.quantity
                )
                if not reserved:
                    raise HTTPException(status_code=409, detail=f"insufficient stock for {item.sku}")
            order_id = await conn.fetchval(
                "INSERT INTO orders(customer_id, status) VALUES($1, $2) RETURNING id",
                order.customer_id,
                OrderStatus.RESERVED,
            )
    return {"order_id": str(order_id), "status": OrderStatus.RESERVED}


@app.get("/orders/{order_id}")
async def get_order(order_id: str) -> dict[str, str]:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id, status FROM orders WHERE id = $1", order_id)
    if row is None:
        raise HTTPException(status_code=404, detail="order not found")
    return {"order_id": str(row["id"]), "status": row["status"]}
