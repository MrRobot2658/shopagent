"""Stores / products / customers / dashboard data APIs."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .. import data

router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/stores")
def get_stores():
    return {"stores": data.list_stores()}


@router.get("/stores/{store}")
def get_store(store: str):
    s = data.store_by_key(store)
    if not s:
        raise HTTPException(404, "store not found")
    s["products"] = data.list_products(s["key"])
    return s


@router.get("/products")
def get_products(store: str | None = Query(None)):
    return {"products": data.list_products(store)}


@router.get("/customers")
def get_customers(store: str | None = Query(None), tier: str | None = Query(None)):
    return {"customers": data.list_customers(store, tier)}


@router.get("/dashboard")
def get_dashboard(store: str = Query("fur")):
    s = data.store_by_key(store)
    if not s:
        raise HTTPException(404, "store not found")
    orders = data.list_orders(s["key"])
    return {
        "store": {"key": s["key"], "slug": s["slug"], "name": s["name"]},
        "kpis": s["kpis"],
        "revenue_series": s["revenue_series"],
        "weeks": data.WEEKS,
        "recent_orders": orders[:5],
        "customers": data.list_customers(s["key"]),
    }
