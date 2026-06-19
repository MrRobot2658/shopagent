"""Runtime configuration, read from environment variables.

Kept dependency-free (plain os.getenv) so the mock stack needs nothing beyond
FastAPI + uvicorn. Real-provider keys are read here too, ready for later.
"""
import os

# Which AI provider powers chat / content / images.
#   "mock"   -> deterministic, context-aware fake responses (no key needed)
#   "claude" -> Anthropic / Vercel AI Gateway (requires ANTHROPIC_API_KEY)
AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").lower()

# Reserved for the real provider (not required in mock mode).
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-8")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "")  # e.g. Vercel AI Gateway

# PostgreSQL (async, asyncpg driver) — the source of truth for store data.
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://shopagent:shopagent@db:5432/shopagent"
)

# Redis — backs login sessions (token -> session JSON, with TTL).
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
SESSION_TTL = int(os.getenv("SESSION_TTL", "86400"))      # seconds (24h)
SESSION_COOKIE = os.getenv("SESSION_COOKIE", "sa_session")

# Seed admin credentials (created on first boot if the users table is empty).
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Absolute path to the static site root (the repo root). When set, the API also
# serves the marketing/demo HTML so the whole thing runs in one container.
STATIC_ROOT = os.getenv("STATIC_ROOT", "")

# Per-streamed-chunk delay (seconds) to simulate a live model typing.
STREAM_DELAY = float(os.getenv("STREAM_DELAY", "0.03"))

# CORS allow-list ("*" for the demo).
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
