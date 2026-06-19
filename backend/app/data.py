"""In-memory seed data + a tiny mutable store.

Mirrors the hardcoded mock content already used by the static front-end
(admin.js STORES, the LUXEFUR product grid, etc.) so the API is a drop-in
source of truth. No database — everything lives in process memory and resets
on restart. Orders placed through /api/orders are appended here at runtime.
"""
from __future__ import annotations

import itertools
from copy import deepcopy
from typing import Optional

# ---------------------------------------------------------------- stores ----
# `key` matches admin.js (fur/pet/sport); `slug` matches the public page path.
STORES = [
    {
        "key": "fur",
        "slug": "luxefur",
        "name": "LUXEFUR",
        "tagline": "海宁皮革城 · 一件代发 · 高端皮草",
        "industry": "皮草 / Fur",
        "currency": "USD",
        "knowledge_base": "皮草保养知识库",
        "scene": "雪天",
        "platforms": ["Shopify"],
        "kpis": {"visitors": "84,291", "orders": "2,487", "revenue": "$1.62M", "cvr": "2.95%"},
        "revenue_series": [42, 55, 48, 63, 70, 66, 78, 84, 80, 92],
    },
    {
        "key": "pet",
        "slug": "pawmaison",
        "name": "PAWMAISON",
        "tagline": "义乌宠物产业带 · OEM · 高端宠物用品",
        "industry": "宠物 / Pet",
        "currency": "USD",
        "knowledge_base": "宠物品种适配知识库",
        "scene": "家居",
        "platforms": ["Shopify", "BigCommerce"],
        "kpis": {"visitors": "51,038", "orders": "3,142", "revenue": "$486K", "cvr": "3.42%"},
        "revenue_series": [30, 38, 44, 41, 52, 58, 55, 63, 69, 74],
    },
    {
        "key": "sport",
        "slug": "cupid-sport",
        "name": "CUPID SPORT",
        "tagline": "柯桥面料产业带 · OEM · 运动服饰",
        "industry": "运动 / Sportswear",
        "currency": "USD",
        "knowledge_base": "运动场景推荐知识库",
        "scene": "健身房",
        "platforms": ["Shopify", "Amazon", "Temu"],
        "kpis": {"visitors": "127,654", "orders": "8,930", "revenue": "$392K", "cvr": "4.10%"},
        "revenue_series": [48, 52, 60, 58, 67, 72, 70, 81, 88, 95],
    },
]

WEEKS = ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10"]

# -------------------------------------------------------------- products ----
PRODUCTS = [
    # LUXEFUR (mirrors the static product grid)
    {"id": "lux-001", "store": "fur", "name": "Midnight Mink Coat", "desc": "Saga Furs Certified · 3 Colors", "price": 2400, "emoji": "🧥", "stock": 12},
    {"id": "lux-002", "store": "fur", "name": "Silver Fox Coat", "desc": "Natural Color · One of a Kind", "price": 1680, "emoji": "🦊", "stock": 5},
    {"id": "lux-003", "store": "fur", "name": "Shearling Jacket", "desc": "Italian Sheepskin · Cream", "price": 890, "emoji": "🧣", "stock": 28},
    {"id": "lux-004", "store": "fur", "name": "Faux Fur Coat", "desc": "Premium Faux · 6 Colors", "price": 220, "emoji": "🧶", "stock": 140},
    # PAWMAISON
    {"id": "paw-001", "store": "pet", "name": "Orthopedic Dog Bed", "desc": "Memory Foam · 3 Sizes", "price": 128, "emoji": "🛏", "stock": 220},
    {"id": "paw-002", "store": "pet", "name": "Adventure Harness", "desc": "No-Pull · Reflective", "price": 64, "emoji": "🦮", "stock": 310},
    {"id": "paw-003", "store": "pet", "name": "Ceramic Slow Feeder", "desc": "Anti-Gulp · Dishwasher Safe", "price": 45, "emoji": "🍽", "stock": 180},
    {"id": "paw-004", "store": "pet", "name": "Cat Tower Deluxe", "desc": "Sisal + Plush · 1.8m", "price": 320, "emoji": "🐈", "stock": 36},
    # CUPID SPORT
    {"id": "cup-001", "store": "sport", "name": "Seamless Leggings", "desc": "Squat-Proof · 7 Colors", "price": 52, "emoji": "🩳", "stock": 540},
    {"id": "cup-002", "store": "sport", "name": "Cloud Sports Bra", "desc": "Medium Impact · Buttery", "price": 42, "emoji": "👚", "stock": 480},
    {"id": "cup-003", "store": "sport", "name": "Featherweight Tee", "desc": "Quick-Dry · Anti-Odor", "price": 38, "emoji": "👕", "stock": 620},
    {"id": "cup-004", "store": "sport", "name": "Train Shorts 2-in-1", "desc": "Liner + Pocket", "price": 48, "emoji": "🩳", "stock": 410},
]

# ------------------------------------------------------------- customers ----
CUSTOMERS = [
    {"id": "c-1001", "store": "fur", "name": "Isabella Romano", "email": "isabella@example.com", "country": "US", "orders": 4, "ltv": 7320, "tier": "VIP", "last_active": "2026-06-17"},
    {"id": "c-1002", "store": "fur", "name": "Hans Müller", "email": "hans@example.de", "country": "DE", "orders": 2, "ltv": 3360, "tier": "高价值", "last_active": "2026-06-02"},
    {"id": "c-1003", "store": "fur", "name": "Yuki Tanaka", "email": "yuki@example.jp", "country": "JP", "orders": 1, "ltv": 2400, "tier": "沉睡", "last_active": "2026-05-08"},
    {"id": "c-2001", "store": "pet", "name": "Sarah Johnson", "email": "sarah@example.com", "country": "US", "orders": 6, "ltv": 1180, "tier": "VIP", "last_active": "2026-06-18"},
    {"id": "c-2002", "store": "pet", "name": "Liam O'Brien", "email": "liam@example.ie", "country": "IE", "orders": 3, "ltv": 540, "tier": "活跃", "last_active": "2026-06-11"},
    {"id": "c-3001", "store": "sport", "name": "Mia Chen", "email": "mia@example.com", "country": "US", "orders": 9, "ltv": 720, "tier": "VIP", "last_active": "2026-06-19"},
    {"id": "c-3002", "store": "sport", "name": "Emma Wilson", "email": "emma@example.au", "country": "AU", "orders": 2, "ltv": 96, "tier": "新客", "last_active": "2026-06-15"},
]

# ---------------------------------------------------------------- orders ----
_STATUS = ["已付款", "已发货", "运输中", "已完成", "待处理"]
ORDERS = [
    {"id": "#10492", "store": "fur", "customer": "Isabella Romano", "items": [{"id": "lux-001", "name": "Midnight Mink Coat", "qty": 1, "price": 2400}], "total": 2400, "status": "已发货", "country": "US", "created": "2026-06-18"},
    {"id": "#10488", "store": "fur", "customer": "Hans Müller", "items": [{"id": "lux-003", "name": "Shearling Jacket", "qty": 1, "price": 890}], "total": 890, "status": "运输中", "country": "DE", "created": "2026-06-17"},
    {"id": "#10477", "store": "fur", "customer": "Yuki Tanaka", "items": [{"id": "lux-002", "name": "Silver Fox Coat", "qty": 1, "price": 1680}], "total": 1680, "status": "已完成", "country": "JP", "created": "2026-06-15"},
    {"id": "#20913", "store": "pet", "customer": "Sarah Johnson", "items": [{"id": "paw-004", "name": "Cat Tower Deluxe", "qty": 1, "price": 320}, {"id": "paw-003", "name": "Ceramic Slow Feeder", "qty": 2, "price": 45}], "total": 410, "status": "已付款", "country": "US", "created": "2026-06-18"},
    {"id": "#20888", "store": "pet", "customer": "Liam O'Brien", "items": [{"id": "paw-002", "name": "Adventure Harness", "qty": 1, "price": 64}], "total": 64, "status": "已完成", "country": "IE", "created": "2026-06-14"},
    {"id": "#30551", "store": "sport", "customer": "Mia Chen", "items": [{"id": "cup-001", "name": "Seamless Leggings", "qty": 2, "price": 52}], "total": 104, "status": "已发货", "country": "US", "created": "2026-06-19"},
    {"id": "#30540", "store": "sport", "customer": "Emma Wilson", "items": [{"id": "cup-002", "name": "Cloud Sports Bra", "qty": 1, "price": 42}], "total": 42, "status": "待处理", "country": "AU", "created": "2026-06-15"},
]

# Sequential id generator for runtime-created orders (continues past seed ids).
_order_seq = itertools.count(40000)


# ----------------------------------------------------------- accessors -----
def store_by_key(key: str) -> Optional[dict]:
    return next((deepcopy(s) for s in STORES if s["key"] == key or s["slug"] == key), None)


def list_stores() -> list[dict]:
    return deepcopy(STORES)


def list_products(store: Optional[str] = None) -> list[dict]:
    items = PRODUCTS if store is None else [p for p in PRODUCTS if p["store"] == _resolve(store)]
    return deepcopy(items)


def product_by_id(pid: str) -> Optional[dict]:
    return next((deepcopy(p) for p in PRODUCTS if p["id"] == pid), None)


def list_orders(store: Optional[str] = None) -> list[dict]:
    items = ORDERS if store is None else [o for o in ORDERS if o["store"] == _resolve(store)]
    return deepcopy(sorted(items, key=lambda o: o["created"], reverse=True))


def list_customers(store: Optional[str] = None, tier: Optional[str] = None) -> list[dict]:
    items = list(CUSTOMERS)
    if store:
        items = [c for c in items if c["store"] == _resolve(store)]
    if tier:
        items = [c for c in items if c["tier"] == tier]
    return deepcopy(items)


def create_order(store: str, customer: str, items: list[dict], country: str = "US") -> dict:
    skey = _resolve(store)
    total = sum(i["price"] * i["qty"] for i in items)
    order = {
        "id": f"#{next(_order_seq)}",
        "store": skey,
        "customer": customer or "Guest",
        "items": items,
        "total": total,
        "status": "已付款",
        "country": country,
        "created": "2026-06-19",
    }
    ORDERS.insert(0, order)
    return deepcopy(order)


def _resolve(store: str) -> str:
    """Accept either the admin key (fur) or the public slug (luxefur)."""
    s = store_by_key(store)
    return s["key"] if s else store
