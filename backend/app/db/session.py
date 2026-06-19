"""Async engine + session factory."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .. import config

engine = create_async_engine(config.DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncSession:
    """FastAPI dependency yielding a scoped async session."""
    async with SessionLocal() as session:
        yield session
