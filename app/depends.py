from typing import AsyncGenerator

from httpx import AsyncClient, Limits, Timeout

from sqlalchemy.ext.asyncio import AsyncSession

from app.orm import SessionLocal


# Shared limits: 100 max connections, 20 per host, 5 s total timeout
HTTP_LIMITS = Limits(max_connections=100, max_keepalive_connections=20)
HTTP_TIMEOUT = Timeout(5.0, connect=1.0)


async def cliente_assincrono() -> AsyncGenerator[AsyncClient, None]:
    """Dependency que provê um httpx.AsyncClient com pool e timeouts otimizados."""
    async with AsyncClient(
        limits=HTTP_LIMITS,
        timeout=HTTP_TIMEOUT,
    ) as client:
        yield client


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an AsyncSession."""
    async with SessionLocal() as session:
        async with session.begin():
            yield session
