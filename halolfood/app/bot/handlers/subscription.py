"""Obuna holati va "to'ladim" tasdiqlash oqimi.

DIQQAT: haqiqiy checkout (savat -> buyurtma -> to'lov) HAM, obunani
boshqarish (kunlik ovqatni almashtirish, bitta kunni yoki butun obunani
bekor qilish) HAM endi faqat Mini App orqali amalga oshiriladi
(`app/api/routes/orders.py`) — botning o'z ichida alohida jadval/bekor
qilish tugmalari ATAYLAB yo'q, chunki bir nechta alohida xabar+tugma
ko'rinishida ko'rsatish noqulay edi. Bu yerda faqat qisqa holat xulosasi
va to'lovni admin bilan yakunlash qoldi.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import admin_confirm_keyboard, is_btn
from app.bot.notify import notify_admins
from app.i18n import t
from app.services.subscriptions import get_active_subscription, get_order_by_reference

router = Router(name="subscription")


@router.message(is_btn("btn_my_subscription"))
async def show_subscription(message: Message, session, user, lang: str) -> None:
    """Foydalanuvchining hozirgi obuna holatini ko'rsatadi (batafsil boshqarish uchun Mini App'ga yo'naltiradi)."""
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
        "",
        t("manage_in_app_hint", lang),
    ]
    await message.answer("\n".join(lines))


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
    await notify_admins(callback.bot, text, reply_markup=admin_confirm_keyboard(order.reference))

    await callback.message.edit_reply_markup(reply_markup=None)
