from typing import AsyncGenerator

from httpx import Limits, Timeout

from sqlalchemy.ext.asyncio import AsyncSession

from app.orm import SessionLocal


# Shared limits: 100 max connections, 20 per host, 5 s total timeout
HTTP_LIMITS = Limits(max_connections=100, max_keepalive_connections=20)
HTTP_TIMEOUT = Timeout(5.0, connect=1.0)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an AsyncSession."""
    async with SessionLocal() as session:
        async with session.begin():
            yield session
