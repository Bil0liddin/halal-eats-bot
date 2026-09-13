"""Savat bilan ishlash uchun API'lar."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import current_user, get_session
from app.db.models import CartItem, User
from app.services.subscriptions import get_cart_items, remove_cart_item, set_cart_item

router = APIRouter()


class CartItemIn(BaseModel):
    """PUT /cart uchun kiruvchi ma'lumot: bitta kunga bitta taom tanlash."""

    plan_id: int
    delivery_date: date
    menu_item_id: int
    qty: int = 1


class CartItemDelete(BaseModel):
    """DELETE /cart uchun kiruvchi ma'lumot: bekor qilinadigan sana."""

    delivery_date: date


def _serialize(items: list[CartItem], lang: str) -> list[dict]:
    return [
        {
            "plan_id": ci.plan_id,
            "delivery_date": ci.delivery_date.isoformat(),
            "menu_item_id": ci.menu_item_id,
            "menu_item_name": ci.menu_item.name(lang),
            "qty": ci.qty,
        }
        for ci in items
    ]


@router.get("/cart")
async def get_cart(session: AsyncSession = Depends(get_session), user: User = Depends(current_user)):
    """Foydalanuvchi savatidagi barcha tanlovlarni qaytaradi."""
    lang = user.lang.value if user.lang else "uz"
    items = await get_cart_items(session, user)
    return {"items": _serialize(items, lang)}


@router.put("/cart")
async def put_cart_item(
    payload: CartItemIn,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
):
    """Bitta kunga taom tanlaydi. Shu kunga avval tanlov bo'lsa — ALMASHTIRILADI."""
    lang = user.lang.value if user.lang else "uz"
    await set_cart_item(
        session,
        user,
        plan_id=payload.plan_id,
        delivery_date=payload.delivery_date,
        menu_item_id=payload.menu_item_id,
        qty=payload.qty,
    )
    items = await get_cart_items(session, user, plan_id=payload.plan_id)
    return {"items": _serialize(items, lang)}


@router.delete("/cart")
async def delete_cart_item(
    payload: CartItemDelete,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
):
    """Berilgan kundagi tanlovni savatdan olib tashlaydi."""
    lang = user.lang.value if user.lang else "uz"
    await remove_cart_item(session, user, payload.delivery_date)
    items = await get_cart_items(session, user)
    return {"items": _serialize(items, lang)}
