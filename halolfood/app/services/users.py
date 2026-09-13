"""Foydalanuvchi va fabrika bilan bog'liq oddiy amallar."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Factory, Lang, User


async def get_or_create_user(session: AsyncSession, *, telegram_id: int, username: str | None) -> User:
    """Telegram ID bo'yicha foydalanuvchini topadi, topilmasa yangisini yaratadi."""
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        await session.flush()
    elif user.username != username:
        user.username = username
    return user


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    """Ichki (bazadagi) ID bo'yicha foydalanuvchini qaytaradi."""
    return await session.get(User, user_id)


async def set_language(session: AsyncSession, user: User, lang: str) -> None:
    """Foydalanuvchi tilini o'zgartiradi."""
    user.lang = Lang(lang)


async def list_active_factories(session: AsyncSession) -> list[Factory]:
    """Faol fabrikalar ro'yxatini qaytaradi."""
    result = await session.execute(select(Factory).where(Factory.is_active.is_(True)).order_by(Factory.name))
    return list(result.scalars().all())


async def get_factory(session: AsyncSession, factory_id: int) -> Factory | None:
    """ID bo'yicha fabrikani qaytaradi."""
    return await session.get(Factory, factory_id)


async def complete_registration(
    session: AsyncSession,
    user: User,
    *,
    full_name: str,
    phone: str,
    factory_id: int,
    delivery_note: str | None,
) -> None:
    """Ro'yxatdan o'tish anketasini yakunlaydi."""
    from datetime import datetime, timezone

    user.full_name = full_name
    user.phone = phone
    user.factory_id = factory_id
    user.delivery_note = delivery_note
    user.registered_at = datetime.now(timezone.utc)


def normalize_phone(raw: str) -> str | None:
    """Turli formatdagi telefon raqamini "010-1234-5678" ko'rinishiga keltiradi.

    Masalan: "+82 10 1234 5678", "01012345678", "010.1234.5678" — hammasi bir
    xil natijaga keladi. Noto'g'ri uzunlikda bo'lsa None qaytaradi.
    """
    digits = "".join(ch for ch in raw if ch.isdigit())

    # +82 bilan boshlangan xalqaro formatni mahalliy formatga o'tkazamiz
    if digits.startswith("82"):
        digits = "0" + digits[2:]

    if not digits.startswith("0"):
        digits = "0" + digits

    if len(digits) == 11:  # 010-1234-5678
        return f"{digits[0:3]}-{digits[3:7]}-{digits[7:11]}"
    if len(digits) == 10:  # 02-1234-5678 kabi qisqaroq shahar kodlari
        return f"{digits[0:2]}-{digits[2:6]}-{digits[6:10]}"
    return None
