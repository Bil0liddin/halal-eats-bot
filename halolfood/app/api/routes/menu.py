"""Rejalar (Plan) va haftalik menyu uchun API'lar."""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import current_user, get_session
from app.db.models import MenuSlot, Plan, User
from app.i18n import weekday_name

router = APIRouter()


def _next_monday() -> date:
    """Bugundan keyingi eng yaqin dushanba sanasini qaytaradi."""
    today = date.today()
    days_ahead = (7 - today.weekday()) % 7 or 7
    return today + timedelta(days=days_ahead)


@router.get("/plans")
async def list_plans(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
):
    """Foydalanuvchi tilida faol obuna rejalari ro'yxatini qaytaradi."""
    lang = user.lang.value if user.lang else "uz"
    result = await session.execute(select(Plan).where(Plan.is_active.is_(True)).order_by(Plan.sort_order))
    plans = result.scalars().all()
    return [
        {
            "id": p.id,
            "code": p.code,
            "name": p.name(lang),
            "period": p.period.value,
            "meals_count": p.meals_count,
            "duration_days": p.duration_days,
            "price_krw": p.price_krw,
            "price_per_meal": p.price_per_meal,
        }
        for p in plans
    ]


@router.get("/menu")
async def get_menu(
    week_start: date | None = Query(None),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
):
    """Berilgan haftaning e'lon qilingan menyusini kun bo'yicha guruhlab qaytaradi.

    `week_start` berilmasa, eng yaqin KEYINGI dushanba olinadi.
    """
    lang = user.lang.value if user.lang else "uz"
    if week_start is None:
        week_start = _next_monday()

    result = await session.execute(
        select(MenuSlot)
        .where(MenuSlot.week_start == week_start, MenuSlot.is_published.is_(True))
        .order_by(MenuSlot.weekday)
    )
    slots = result.scalars().unique().all()

    days: dict[int, list[dict]] = {i: [] for i in range(7)}
    for slot in slots:
        item = slot.menu_item
        days[slot.weekday].append(
            {
                "menu_item_id": item.id,
                "code": item.code,
                "name": item.name(lang),
                "description": item.description(lang),
                "category": item.category.value,
                "photo_url": item.photo_url,
                "is_halal_certified": item.is_halal_certified,
                "contains_beef": item.contains_beef,
                "contains_chicken": item.contains_chicken,
                "contains_lamb": item.contains_lamb,
                "is_vegetarian": item.is_vegetarian,
                "spicy_level": item.spicy_level,
                "calories": item.calories,
            }
        )

    return {
        "week_start": week_start.isoformat(),
        "days": [
            {
                "weekday": i,
                "date": (week_start + timedelta(days=i)).isoformat(),
                "label": weekday_name(i, lang),
                "items": days[i],
            }
            for i in range(7)
        ],
    }
