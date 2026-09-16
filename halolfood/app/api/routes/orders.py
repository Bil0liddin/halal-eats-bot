"""Buyurtma, to'lov, obuna holati va kunlik ovqatlarni boshqarish uchun API'lar."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import Bot
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import current_user, get_session
from app.bot.keyboards import payment_action_keyboard, pay_url_keyboard
from app.bot.notify import safe_send
from app.config import settings
from app.db.models import Delivery, User
from app.i18n import t, weekday_name
from app.services.payments import get_provider
from app.services.subscriptions import (
    BusinessError,
    cancel_subscription,
    change_delivery_meal,
    create_order_from_cart,
    get_active_subscription,
    get_order_by_reference,
    is_before_cutoff,
    skip_delivery,
)

router = APIRouter()

# Botning o'zi (polling) ishlab-ishlamaganidan qat'i nazar, API alohida
# jarayon sifatida ishlaganda ham foydalanuvchiga xabar yubora olishi uchun
# bitta umumiy Bot obyekti.
_bot = Bot(token=settings.bot_token)
_TZ = ZoneInfo(settings.timezone)


class CheckoutIn(BaseModel):
    """Checkout uchun kiruvchi ma'lumot."""

    plan_id: int


class ChangeDeliveryIn(BaseModel):
    """Bitta kunning ovqatini almashtirish uchun kiruvchi ma'lumot."""

    delivery_date: date
    menu_item_id: int


class SkipDeliveryIn(BaseModel):
    """Bitta kunlik yetkazishni bekor qilish uchun kiruvchi ma'lumot."""

    delivery_date: date


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
    """Foydalanuvchining faol obunasini va har bir kunlik yetkazishni (o'zgartirish mumkinligi bilan) qaytaradi."""
    lang = user.lang.value if user.lang else "uz"
    subscription = await get_active_subscription(session, user)
    if subscription is None:
        return {"subscription": None}

    now = datetime.now(_TZ)
    result = await session.execute(
        select(Delivery).where(Delivery.subscription_id == subscription.id).order_by(Delivery.delivery_date)
    )
    deliveries = result.scalars().unique().all()

    delivery_list = [
        {
            "id": d.id,
            "delivery_date": d.delivery_date.isoformat(),
            "weekday": d.delivery_date.weekday(),
            "weekday_label": weekday_name(d.delivery_date.weekday(), lang),
            "week_start": (d.delivery_date - timedelta(days=d.delivery_date.weekday())).isoformat(),
            "menu_item_id": d.menu_item_id,
            "menu_item_name": d.menu_item.name(lang),
            "status": d.status.value,
            "can_change": d.status.value == "planned"
            and is_before_cutoff(d.delivery_date, now=now, cutoff_hour=settings.order_cutoff_hour),
        }
        for d in deliveries
    ]

    return {
        "subscription": {
            "status": subscription.status.value,
            "starts_on": subscription.starts_on.isoformat(),
            "ends_on": subscription.ends_on.isoformat(),
            "meals_total": subscription.meals_total,
            "meals_used": subscription.meals_used,
            "meals_left": subscription.meals_left,
            "deliveries": delivery_list,
        }
    }


@router.post("/subscriptions/cancel")
async def cancel_my_subscription(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
):
    """Foydalanuvchining faol obunasini butunlay bekor qiladi."""
    subscription = await get_active_subscription(session, user)
    if subscription is None:
        raise HTTPException(status_code=404, detail="Faol obuna topilmadi")

    await cancel_subscription(session, subscription, today=date.today())
    return {"ok": True}


@router.post("/deliveries/change")
async def change_my_delivery(
    payload: ChangeDeliveryIn,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
):
    """"Mening obunam" bo'limidan bitta kunning ovqatini almashtiradi."""
    lang = user.lang.value if user.lang else "uz"
    result = await session.execute(
        select(Delivery).where(Delivery.user_id == user.id, Delivery.delivery_date == payload.delivery_date)
    )
    delivery = result.scalar_one_or_none()
    if delivery is None:
        raise HTTPException(status_code=404, detail="Yetkazish topilmadi")

    now = datetime.now(_TZ)
    try:
        await change_delivery_meal(
            session, delivery, payload.menu_item_id, now=now, cutoff_hour=settings.order_cutoff_hour, lang=lang
        )
    except BusinessError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc

    return {"ok": True}


@router.post("/deliveries/skip")
async def skip_my_delivery(
    payload: SkipDeliveryIn,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
):
    """"Mening obunam" bo'limidan bitta kunni butunlay bekor qiladi (obuna muddati 1 kunga uzayadi)."""
    lang = user.lang.value if user.lang else "uz"
    result = await session.execute(
        select(Delivery).where(Delivery.user_id == user.id, Delivery.delivery_date == payload.delivery_date)
    )
    delivery = result.scalar_one_or_none()
    if delivery is None:
        raise HTTPException(status_code=404, detail="Yetkazish topilmadi")

    now = datetime.now(_TZ)
    try:
        await skip_delivery(session, delivery, now=now, cutoff_hour=settings.order_cutoff_hour, lang=lang)
    except BusinessError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc

    return {"ok": True}
