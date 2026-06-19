"""Orders (admin) + checkout (public shopper flow) — PostgreSQL-backed."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import require_user
from ..db.models import Order, Product, Store
from ..db.session import get_session
from ..schemas import CheckoutRequest

router = APIRouter(prefix="/api", tags=["orders"])


def _row(obj) -> dict:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


@router.get("/orders")
async def get_orders(
    store: str | None = Query(None),
    db: AsyncSession = Depends(get_session),
    _user=Depends(require_user),
):
    stmt = select(Order).order_by(Order.created.desc())
    if store:
        s = await db.scalar(select(Store).where(or_(Store.key == store, Store.slug == store)))
        stmt = stmt.where(Order.store == (s.key if s else store))
    rows = (await db.scalars(stmt)).all()
    return {"orders": [_row(o) for o in rows]}


@router.post("/checkout", status_code=201)
async def checkout(req: CheckoutRequest, db: AsyncSession = Depends(get_session)):
    if not req.items:
        raise HTTPException(400, "cart is empty")
    s = await db.scalar(select(Store).where(or_(Store.key == req.store, Store.slug == req.store)))
    store_key = s.key if s else req.store

    line_items = []
    for it in req.items:
        p = await db.get(Product, it.id)
        if not p:
            raise HTTPException(404, f"product {it.id} not found")
        line_items.append({"id": p.id, "name": p.name, "qty": it.qty, "price": p.price})

    total = sum(i["price"] * i["qty"] for i in line_items)
    count = await db.scalar(select(func.count()).select_from(Order))
    order = Order(
        id=f"#{40000 + (count or 0)}",
        store=store_key,
        customer=req.customer or "Guest",
        items=line_items,
        total=total,
        status="已付款",
        country=req.country,
        created="2026-06-19",
    )
    db.add(order)
    await db.commit()
    return {"order": _row(order), "message": "下单成功（演示）", "confirmation": order.id}
