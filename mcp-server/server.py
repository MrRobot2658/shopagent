"""Shops Agent MCP server.

A thin MCP (Model Context Protocol) server that exposes the Shops Agent platform
as a set of agent-callable tools. It is a *client* of the FastAPI backend — every
tool is an HTTP call to `/api/...`. Nothing here touches Postgres / Redis directly,
so this server runs anywhere it can reach the backend.

Connection:
    SHOPAGENT_API  origin of the backend (default http://localhost:8091).
                   Point it at the nginx front (http://localhost:8090) or a remote
                   deployment; the server always appends the `/api/...` paths.

Auth: a single persistent cookie jar is shared across tool calls, so once the
`login` tool succeeds the `sa_session` cookie unlocks the login-required tools
(dashboard / customers / orders / copilot chat / AI generation) for the lifetime
of the process.

Run (stdio transport, the default for editor/CLI integrations):
    python server.py
"""
from __future__ import annotations

import os
from typing import Any, Optional

import httpx
from mcp.server.fastmcp import FastMCP

API_BASE = os.getenv("SHOPAGENT_API", "http://localhost:8091").rstrip("/")
TIMEOUT = float(os.getenv("SHOPAGENT_TIMEOUT", "60"))

mcp = FastMCP("shops-agent")

# One client for the whole process → the login cookie persists across tool calls.
# trust_env=False: ignore ambient HTTP(S)/SOCKS proxy env vars — we always talk to
# an explicit backend origin and don't want a proxy intercepting localhost calls.
_client = httpx.AsyncClient(
    base_url=API_BASE, timeout=TIMEOUT, follow_redirects=True, trust_env=False
)


async def _request(method: str, path: str, **kw) -> Any:
    """Call the backend and return parsed JSON, raising readable errors."""
    try:
        resp = await _client.request(method, path, **kw)
    except httpx.RequestError as exc:  # connection refused, DNS, timeout, ...
        raise RuntimeError(
            f"无法连接后端 {API_BASE}{path}: {exc}. 后端是否在运行？(docker compose up)"
        ) from exc
    if resp.status_code == 401:
        raise RuntimeError("需要登录：先调用 login 工具（默认 admin / admin123）")
    if resp.status_code >= 400:
        detail = resp.text
        try:
            detail = resp.json().get("detail", detail)
        except Exception:
            pass
        raise RuntimeError(f"后端返回 {resp.status_code}: {detail}")
    if not resp.content:
        return {}
    return resp.json()


# --------------------------------------------------------------------------- #
# Commerce actions: login + checkout
# --------------------------------------------------------------------------- #
@mcp.tool()
async def login(username: str = "admin", password: str = "admin123") -> dict:
    """登录后台，获取会话 cookie 以解锁需要鉴权的工具。

    成功后 dashboard / customers / orders / chat_copilot / generate_content /
    generate_image 才可用。默认种子账号为 admin / admin123。
    """
    return await _request("POST", "/api/auth/login", json={"username": username, "password": password})


@mcp.tool()
async def whoami() -> dict:
    """返回当前登录用户（未登录返回 401 提示）。"""
    return await _request("GET", "/api/auth/me")


@mcp.tool()
async def place_order(
    store: str,
    items: list[dict],
    customer: str = "Guest",
    country: str = "US",
) -> dict:
    """下单（演示用 checkout，公开无需登录）。

    store: 店铺 key 或 slug（fur/pet/sport 或 luxefur/pawmaison/cupid-sport）。
    items: 形如 [{"id": "<product_id>", "qty": 2}] 的商品列表。
    """
    payload = {
        "store": store,
        "customer": customer,
        "country": country,
        "items": [{"id": str(i["id"]), "qty": int(i.get("qty", 1))} for i in items],
    }
    return await _request("POST", "/api/checkout", json=payload)


# --------------------------------------------------------------------------- #
# Catalog & analytics
# --------------------------------------------------------------------------- #
@mcp.tool()
async def list_stores() -> dict:
    """列出全部 demo 店铺及元数据（公开）。"""
    return await _request("GET", "/api/stores")


@mcp.tool()
async def get_products(store: Optional[str] = None) -> dict:
    """查询商品目录（公开）。可选 store 过滤（key 或 slug）。"""
    params = {"store": store} if store else None
    return await _request("GET", "/api/products", params=params)


@mcp.tool()
async def get_dashboard(store: str = "fur") -> dict:
    """店铺仪表盘：KPI、收入曲线、近期订单、客户（需要登录）。"""
    return await _request("GET", "/api/dashboard", params={"store": store})


@mcp.tool()
async def get_customers(store: Optional[str] = None, tier: Optional[str] = None) -> dict:
    """客户列表，支持按 store 和 RFM tier 过滤（需要登录）。"""
    params: dict[str, str] = {}
    if store:
        params["store"] = store
    if tier:
        params["tier"] = tier
    return await _request("GET", "/api/customers", params=params or None)


@mcp.tool()
async def get_orders(store: Optional[str] = None) -> dict:
    """订单列表，可选 store 过滤（需要登录）。"""
    params = {"store": store} if store else None
    return await _request("GET", "/api/orders", params=params)


# --------------------------------------------------------------------------- #
# AI chat
# --------------------------------------------------------------------------- #
async def _chat(surface: str, message: str, store: Optional[str], history: Optional[list[dict]]) -> dict:
    messages: list[dict] = list(history or [])
    messages.append({"role": "user", "content": message})
    payload = {"surface": surface, "store": store, "messages": messages, "stream": False}
    return await _request("POST", "/api/chat", json=payload)


@mcp.tool()
async def chat_concierge(
    message: str,
    store: Optional[str] = None,
    history: Optional[list[dict]] = None,
) -> dict:
    """面向买家的店铺导购助手（公开）。

    store 提供店铺上下文；history 是可选的历史消息列表
    （[{"role":"user"|"assistant","content":"..."}]）。返回 {"reply": "..."}。
    """
    return await _chat("store", message, store, history)


@mcp.tool()
async def chat_copilot(
    message: str,
    store: Optional[str] = None,
    history: Optional[list[dict]] = None,
) -> dict:
    """面向运营者的后台 Copilot 助手（需要登录）。参数同 chat_concierge。"""
    return await _chat("copilot", message, store, history)


# --------------------------------------------------------------------------- #
# AI generation
# --------------------------------------------------------------------------- #
@mcp.tool()
async def generate_content(
    kind: str = "product_desc",
    store: Optional[str] = None,
    language: str = "English",
    params: Optional[dict] = None,
) -> dict:
    """生成营销文案（需要登录）。

    kind: product_desc | seo_blog | social | edm。
    params: 自由字段（category / material / keywords / channel ...）。
    """
    payload = {"kind": kind, "store": store, "language": language, "params": params or {}}
    return await _request("POST", "/api/ai/content", json=payload)


@mcp.tool()
async def generate_image(
    operation: str = "scene_swap",
    store: Optional[str] = None,
    scene: str = "雪天",
    source: Optional[str] = None,
) -> dict:
    """图片处理/生成（需要登录）。

    operation: bg_remove | scene_swap | upscale | video。
    """
    payload = {"store": store, "operation": operation, "scene": scene, "source": source}
    return await _request("POST", "/api/ai/image", json=payload)


@mcp.tool()
async def health() -> dict:
    """后端健康检查 + 当前 AI provider。"""
    return await _request("GET", "/api/health")


if __name__ == "__main__":
    mcp.run()
