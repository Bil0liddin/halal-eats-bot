"""Ma'lumotlar bazasiga ulanish: async engine va sessiya boshqaruvi."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)

SessionMaker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    """Bitta tranzaksiya doirasida sessiya ochadi: muvaffaqiyatli bo'lsa commit, xato bo'lsa rollback qiladi."""
    async with SessionMaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_models() -> None:
    """Jadvallarni yaratadi.

    Ishlab chiqarishda (production) to'liq migratsiya vositasi (masalan Alembic)
    ishlatish tavsiya etiladi — bu funksiya faqat dastlabki sozlash/test uchun.
    """
    from app.db.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
