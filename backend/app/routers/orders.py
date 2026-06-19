"""Orders + checkout flow."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .. import data
from ..schemas import CheckoutRequest

router = APIRouter(prefix="/api", tags=["orders"])


@router.get("/orders")
def get_orders(store: str | None = Query(None)):
    return {"orders": data.list_orders(store)}


@router.post("/checkout", status_code=201)
def checkout(req: CheckoutRequest):
    if not req.items:
        raise HTTPException(400, "cart is empty")
    line_items = []
    for it in req.items:
        p = data.product_by_id(it.id)
        if not p:
            raise HTTPException(404, f"product {it.id} not found")
        line_items.append({"id": p["id"], "name": p["name"], "qty": it.qty, "price": p["price"]})
    order = data.create_order(req.store, req.customer or "Guest", line_items, req.country)
    return {"order": order, "message": "下单成功（演示）", "confirmation": order["id"]}
