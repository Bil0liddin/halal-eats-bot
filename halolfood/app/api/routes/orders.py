"""Buyurtma yaratish, to'lovni boshlash va uning holatini kuzatish uchun API'lar."""
from __future__ import annotations

from aiogram import Bot
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import current_user, get_session
from app.bot.keyboards import payment_action_keyboard, pay_url_keyboard
from app.bot.notify import safe_send
from app.config import settings
from app.db.models import User
from app.i18n import t
from app.services.payments import get_provider
from app.services.subscriptions import (
    BusinessError,
    create_order_from_cart,
    get_active_subscription,
    get_order_by_reference,
)

router = APIRouter()

# Botning o'zi (polling) ishlab-ishlamaganidan qat'i nazar, API alohida
# jarayon sifatida ishlaganda ham foydalanuvchiga xabar yubora olishi uchun
# bitta umumiy Bot obyekti.
_bot = Bot(token=settings.bot_token)


class CheckoutIn(BaseModel):
    """Checkout uchun kiruvchi ma'lumot."""

    plan_id: int


@router.post("/orders/checkout")
async def checkout(
    payload: CheckoutIn,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
):
    """Savatdan buyurtma yaratadi va tanlangan provayder orqali to'lovni boshlaydi."""
    lang = user.lang.value if user.lang else "uz"
    try:
        order = await create_order_from_cart(session, user, payload.plan_id, lang=lang)
    except BusinessError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc

    provider = get_provider()
    intent = await provider.create_payment(
        reference=order.reference,
        amount_krw=order.amount_krw,
        description=f"Halol Food - {order.reference}",
        lang=lang,
    )

    order.provider = intent.provider
    order.provider_payment_id = intent.provider_payment_id
    await session.flush()

    # Mini App yopilib qolsa ham davom ettira olishi uchun, botda ham
    # to'lov ma'lumotini alohida xabar qilib yuboramiz.
    if intent.instructions:
        await safe_send(
            _bot,
            user.telegram_id,
            intent.instructions,
            reply_markup=payment_action_keyboard(order.reference, lang),
        )
    elif intent.checkout_url:
        await safe_send(
            _bot,
            user.telegram_id,
            t("checkout_instructions_heading", lang),
            reply_markup=pay_url_keyboard(intent.checkout_url, lang),
        )

    return {
        "reference": order.reference,
        "amount_krw": order.amount_krw,
        "starts_on": order.starts_on.isoformat(),
        "ends_on": order.ends_on.isoformat(),
        "provider": intent.provider,
        "checkout_url": intent.checkout_url,
        "instructions": intent.instructions,
        "auto_confirm": provider.auto_confirm,
    }


@router.get("/orders/{reference}")
async def get_order_status(
    reference: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
):
    """Buyurtmaning joriy to'lov holatini qaytaradi — Mini App shu endpointni so'rab (polling) turadi."""
    order = await get_order_by_reference(session, reference)
    if order is None or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return {
        "reference": order.reference,
        "status": order.status.value,
        "amount_krw": order.amount_krw,
        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
    }


@router.get("/orders/me/subscription")
async def my_subscription(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
):
    """Foydalanuvchining hozirgi faol obunasini qaytaradi (bo'lmasa `subscription: null`)."""
    subscription = await get_active_subscription(session, user)
    if subscription is None:
        return {"subscription": None}
    return {
        "subscription": {
            "status": subscription.status.value,
            "starts_on": subscription.starts_on.isoformat(),
            "ends_on": subscription.ends_on.isoformat(),
            "meals_total": subscription.meals_total,
            "meals_used": subscription.meals_used,
            "meals_left": subscription.meals_left,
        }
    }
