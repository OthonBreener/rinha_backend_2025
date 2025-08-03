from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, Index, Integer, Boolean, Float
from sqlalchemy.ext.asyncio import (
    AsyncEngine, async_sessionmaker, create_async_engine, AsyncSession
)

DATABASE_URL_ASYNC = "postgresql+asyncpg://postgres:postgres@postgres:5432/payments"


class Base(DeclarativeBase):
    ...


class Pagamento(Base):
    __tablename__ = "pagamentos"
    id = Column(Integer, primary_key=True, index=True)
    correlation_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    requested_at = Column(DateTime(timezone=True), nullable=False)
    processor_used = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False, default=0.0)

    __table_args__ = (
        Index(
            'ix_payments_summary',
            'requested_at',
            'processor_used'
        ),
    )


engine: AsyncEngine = create_async_engine(
    DATABASE_URL_ASYNC,
    pool_recycle=60,
    pool_size=10,
    max_overflow=20,
    pool_use_lifo=True,
    pool_pre_ping=True,
    echo=False,
)


SessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def create_tables_async() -> None:
    """Create DB tables and ensure indices exist (async)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


async def salvar_pagamento(pagamento: dict[str, str | datetime]) -> None:
    async with SessionLocal() as session:
        async with session.begin():
            objeto_pagamento = Pagamento(**pagamento)
            session.add(objeto_pagamento)
