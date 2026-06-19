"""Create tables and seed initial data (idempotent).

Runs on startup. Retries the DB connection so the API can boot alongside
Postgres in docker-compose even if Postgres takes a moment to accept connections.
"""
from __future__ import annotations

import asyncio

from sqlalchemy import func, select

from .. import config, data
from ..auth import hash_password
from .models import Base, Customer, Order, Product, Store, User
from .session import SessionLocal, engine


async def _wait_for_db(attempts: int = 30, delay: float = 1.0) -> None:
    for i in range(attempts):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            return
        except Exception as exc:  # Postgres not ready yet
            if i == attempts - 1:
                raise
            print(f"[db] waiting for Postgres ({i + 1}/{attempts}): {exc}")
            await asyncio.sleep(delay)


async def init_db() -> None:
    await _wait_for_db()
    async with SessionLocal() as s:
        if await s.scalar(select(func.count()).select_from(Store)):
            return  # already seeded
        for st in data.STORES:
            s.add(Store(**st))
        for p in data.PRODUCTS:
            s.add(Product(**p))
        for c in data.CUSTOMERS:
            s.add(Customer(**c))
        for o in data.ORDERS:
            s.add(Order(**o))
        s.add(
            User(
                username=config.ADMIN_USER,
                password_hash=hash_password(config.ADMIN_PASSWORD),
                role="admin",
            )
        )
        await s.commit()
        print(f"[db] seeded stores/products/customers/orders + admin user '{config.ADMIN_USER}'")
