"""Authentication: password hashing + Redis-backed sessions.

Sessions live in Redis (key `sess:<token>` -> JSON, with TTL). The browser
holds an opaque httponly cookie carrying the token. Passwords are hashed with
PBKDF2-HMAC-SHA256 (stdlib — no native build deps).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import secrets

import redis.asyncio as aioredis
from fastapi import Cookie, HTTPException

from . import config

_redis: aioredis.Redis | None = None

_PBKDF2_ROUNDS = 200_000


# ----------------------------------------------------------- passwords -----
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), _PBKDF2_ROUNDS)
    return f"pbkdf2_sha256${_PBKDF2_ROUNDS}${salt}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, rounds, salt, expected = stored.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(rounds))
        return hmac.compare_digest(dk.hex(), expected)
    except Exception:
        return False


# ------------------------------------------------------------- redis -------
def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(config.REDIS_URL, decode_responses=True)
    return _redis


async def create_session(user: dict) -> str:
    token = secrets.token_urlsafe(32)
    await get_redis().set(f"sess:{token}", json.dumps(user), ex=config.SESSION_TTL)
    return token


async def read_session(token: str | None) -> dict | None:
    if not token:
        return None
    raw = await get_redis().get(f"sess:{token}")
    return json.loads(raw) if raw else None


async def destroy_session(token: str | None) -> None:
    if token:
        await get_redis().delete(f"sess:{token}")


# --------------------------------------------------------- dependencies ----
async def current_user(sa_session: str | None = Cookie(default=None)):
    """Optional: returns the logged-in user dict, or None."""
    return await read_session(sa_session)


async def require_user(sa_session: str | None = Cookie(default=None)):
    """Required: 401 if not logged in."""
    user = await read_session(sa_session)
    if not user:
        raise HTTPException(status_code=401, detail="未登录 / not authenticated")
    return user
