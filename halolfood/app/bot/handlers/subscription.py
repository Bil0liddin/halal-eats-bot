"""Obuna holati, yetkazib berish jadvali va "to'ladim" tasdiqlash oqimi.

DIQQAT: haqiqiy checkout (savat -> buyurtma -> to'lov) Mini App orqali,
`app/api/routes/orders.py`dagi API chaqiruvi orqali sodir bo'ladi. Bu yerda
faqat botning o'z ichidagi qo'shimcha imkoniyatlar bor: obunani ko'rish,
jadvalni ko'rish/bekor qilish va to'lovni admin bilan yakunlash.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from app.bot.keyboards import admin_confirm_keyboard, is_btn, schedule_day_keyboard
from app.bot.notify import safe_send
from app.config import settings
from app.db.models import Delivery
from app.i18n import t
from app.services.subscriptions import (
    BusinessError,
    get_active_subscription,
    get_order_by_reference,
    skip_delivery,
)

router = Router(name="subscription")


@router.message(is_btn("btn_my_subscription"))
async def show_subscription(message: Message, session, user, lang: str) -> None:
    """Foydalanuvchining hozirgi obuna holatini ko'rsatadi."""
    subscription = await get_active_subscription(session, user)
    if subscription is None:
        await message.answer(t("no_active_subscription", lang, open_app=t("btn_open_app", lang)))
        return

    status_label = t(f"status_{subscription.status.value}", lang)
    lines = [
        t("subscription_status_heading", lang),
        "",
        status_label,
        f"{t('meals_left_label', lang)}: {subscription.meals_left}/{subscription.meals_total}",
        f"{t('valid_until_label', lang)}: {subscription.ends_on.isoformat()}",
    ]
    await message.answer("\n".join(lines))


@router.message(is_btn("btn_schedule"))
async def show_schedule(message: Message, session, user, lang: str) -> None:
    """Keyingi 10 kunlik yetkazib berish jadvalini ko'rsatadi, har biriga bekor qilish tugmasi bilan."""
    today = date.today()
    end = today + timedelta(days=9)
    result = await session.execute(
        select(Delivery)
        .where(Delivery.user_id == user.id, Delivery.delivery_date >= today, Delivery.delivery_date <= end)
        .order_by(Delivery.delivery_date)
    )
    deliveries = result.scalars().unique().all()

    if not deliveries:
        await message.answer(t("no_active_subscription", lang, open_app=t("btn_open_app", lang)))
        return

    await message.answer(t("schedule_heading", lang))
    for delivery in deliveries:
        status_text = t(f"delivery_status_{delivery.status.value}", lang)
        line = f"{delivery.delivery_date.isoformat()} — {delivery.menu_item.name(lang)} ({status_text})"
        keyboard = schedule_day_keyboard(delivery.id, lang) if delivery.status.value == "planned" else None
        await message.answer(line, reply_markup=keyboard)


@router.callback_query(F.data.startswith("skip:"))
async def on_skip(callback: CallbackQuery, session, lang: str) -> None:
    """"Bekor qilish" tugmasi bosilganda ishga tushadi."""
    delivery_id = int(callback.data.split(":", 1)[1])
    delivery = await session.get(Delivery, delivery_id)
    if delivery is None:
        await callback.answer()
        return

    now = datetime.now(ZoneInfo(settings.timezone))
    try:
        await skip_delivery(session, delivery, now=now, cutoff_hour=settings.order_cutoff_hour, lang=lang)
    except BusinessError as exc:
        await callback.answer(exc.message, show_alert=True)
        return

    await callback.answer(t("skip_confirmed", lang, date=delivery.delivery_date.isoformat()))
    await callback.message.edit_reply_markup(reply_markup=None)


@router.callback_query(F.data.startswith("paid:confirm:"))
async def on_i_paid(callback: CallbackQuery, session, user, lang: str) -> None:
    """Foydalanuvchi "To'ladim" tugmasini bosganda — adminlarga tasdiqlash so'rovi yuboriladi."""
    reference = callback.data.split(":", 2)[2]
    order = await get_order_by_reference(session, reference)
    await callback.answer(t("i_paid_thanks", lang))
    if order is None:
        return

    text = t(
        "i_paid_notify_admin",
        "uz",
        reference=order.reference,
        full_name=user.full_name or "-",
        phone=user.phone or "-",
        amount=f"{order.amount_krw:,}",
    )
    for admin_id in settings.admin_id_list:
        await safe_send(callback.bot, admin_id, text, reply_markup=admin_confirm_keyboard(order.reference))

    await callback.message.edit_reply_markup(reply_markup=None)
