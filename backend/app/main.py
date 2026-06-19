"""Shops Agent backend — FastAPI app.

Exposes the data + AI APIs and (optionally) serves the static marketing/demo
site so the whole product runs in a single container. API routes are registered
first; a catch-all then serves static files with Vercel-style cleanUrls.
"""
from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

from . import config
from .routers import ai_gen, catalog, chat, orders

app = FastAPI(title="Shops Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in config.CORS_ORIGINS.split(",")] if config.CORS_ORIGINS != "*" else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(catalog.router)
app.include_router(orders.router)
app.include_router(ai_gen.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "ai_provider": config.AI_PROVIDER}


# ----------------------------------------------------- static site serving ---
_STATIC = config.STATIC_ROOT and os.path.isdir(config.STATIC_ROOT)
_REDIRECTS = {"": "/home", "/": "/home", "fur-expo": "/home"}


def _resolve_static(path: str) -> str | None:
    """Map a clean URL to a file on disk (mirrors vercel.json cleanUrls)."""
    root = os.path.abspath(config.STATIC_ROOT)
    candidates = [path, f"{path}.html", os.path.join(path, "index.html")]
    for cand in candidates:
        full = os.path.abspath(os.path.join(root, cand))
        if not full.startswith(root):  # path-traversal guard
            continue
        if os.path.isfile(full):
            return full
    return None


if _STATIC:

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_static(full_path: str):
        key = full_path.strip("/")
        if key in _REDIRECTS:
            return RedirectResponse(_REDIRECTS[key])
        found = _resolve_static(key)
        if found:
            return FileResponse(found)
        raise HTTPException(404, "not found")
