"""Database connection pool for orders-api (SYNTHETIC / fictional).

Uses asyncpg against the ``orders`` Postgres cluster. The pool is sized to stay
well under the cluster's connection limit; see runbooks/database-failover.md and
incidents/INC-2025-002-db-connection-exhaustion.md for the operational history.
"""

import os

import asyncpg

_pool: asyncpg.Pool | None = None


async def init_pool() -> None:
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=os.environ["ORDERS_DB_DSN"],
        min_size=2,
        max_size=10,  # per-replica; 10 replicas * 10 = 100 < cluster limit of 200
        command_timeout=5.0,
    )


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("pool not initialized; call init_pool() on startup")
    return _pool
