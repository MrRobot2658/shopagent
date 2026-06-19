"""Stores / products / customers / dashboard — PostgreSQL-backed."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import require_user
from ..db.models import Customer, Order, Product, Store
from ..db.session import get_session

router = APIRouter(prefix="/api", tags=["catalog"])


def _row(obj) -> dict:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


async def _resolve_store(db: AsyncSession, store: str) -> Store | None:
    return await db.scalar(select(Store).where(or_(Store.key == store, Store.slug == store)))


@router.get("/stores")
async def get_stores(db: AsyncSession = Depends(get_session)):
    rows = (await db.scalars(select(Store))).all()
    return {"stores": [_row(s) for s in rows]}


@router.get("/stores/{store}")
async def get_store(store: str, db: AsyncSession = Depends(get_session)):
    s = await _resolve_store(db, store)
    if not s:
        raise HTTPException(404, "store not found")
    products = (await db.scalars(select(Product).where(Product.store == s.key))).all()
    out = _row(s)
    out["products"] = [_row(p) for p in products]
    return out


@router.get("/products")
async def get_products(store: str | None = Query(None), db: AsyncSession = Depends(get_session)):
    stmt = select(Product)
    if store:
        s = await _resolve_store(db, store)
        stmt = stmt.where(Product.store == (s.key if s else store))
    rows = (await db.scalars(stmt)).all()
    return {"products": [_row(p) for p in rows]}


@router.get("/customers")
async def get_customers(
    store: str | None = Query(None),
    tier: str | None = Query(None),
    db: AsyncSession = Depends(get_session),
    _user=Depends(require_user),
):
    stmt = select(Customer)
    if store:
        s = await _resolve_store(db, store)
        stmt = stmt.where(Customer.store == (s.key if s else store))
    if tier:
        stmt = stmt.where(Customer.tier == tier)
    rows = (await db.scalars(stmt)).all()
    return {"customers": [_row(c) for c in rows]}


@router.get("/dashboard")
async def get_dashboard(
    store: str = Query("fur"),
    db: AsyncSession = Depends(get_session),
    _user=Depends(require_user),
):
    s = await _resolve_store(db, store)
    if not s:
        raise HTTPException(404, "store not found")
    orders = (
        await db.scalars(
            select(Order).where(Order.store == s.key).order_by(Order.created.desc())
        )
    ).all()
    customers = (await db.scalars(select(Customer).where(Customer.store == s.key))).all()
    return {
        "store": {"key": s.key, "slug": s.slug, "name": s.name},
        "kpis": s.kpis,
        "revenue_series": s.revenue_series,
        "weeks": ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10"],
        "recent_orders": [_row(o) for o in orders[:5]],
        "customers": [_row(c) for c in customers],
    }
