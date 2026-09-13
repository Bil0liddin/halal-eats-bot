"""Admin buyruqlari: statistika, oshxona rejasi, kuryer ro'yxati, to'lovlarni tasdiqlash."""
from __future__ import annotations

import csv
import io
from datetime import date, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy import select

from app.bot.notify import safe_send
from app.db.models import Order, OrderStatus, User
from app.i18n import money, t
from app.services.reports import get_courier_sheet, get_kitchen_plan, get_stats
from app.services.subscriptions import BusinessError, confirm_payment, get_order_by_reference

router = Router(name="admin")


async def _require_admin(message: Message, user: User, lang: str) -> bool:
    """Buyruq faqat adminlar uchunligini tekshiradi, bo'lmasa rad etuvchi xabar yuboradi."""
    if not user.is_admin:
        await message.answer(t("admin_only", lang))
        return False
    return True


@router.message(Command("stats"))
async def cmd_stats(message: Message, session, user: User, lang: str) -> None:
    """Umumiy statistika: foydalanuvchilar, obunalar, tushum."""
    if not await _require_admin(message, user, lang):
        return
    stats = await get_stats(session)
    lines = [
        t("stats_heading", lang),
        "",
        f"👥 Foydalanuvchilar: {stats.total_users} (ro'yxatdan o'tgan: {stats.registered_users})",
        f"📦 Faol obunalar: {stats.active_subscriptions}",
        f"📈 Konversiya: {stats.conversion_pct}%",
        f"🏭 Fabrikalar: {stats.factories}",
        f"💰 Umumiy tushum: {money(stats.total_revenue_krw)} won",
        f"⏳ To'lov kutayotgan buyurtmalar: {stats.pending_payments}",
    ]
    await message.answer("\n".join(lines))


async def _send_kitchen_plan(message: Message, session, lang: str, target: date) -> None:
    rows = await get_kitchen_plan(session, target, lang)
    if not rows:
        await message.answer(f"{t('kitchen_heading', lang)} ({target.isoformat()})\n\n—")
        return
    lines = [f"{t('kitchen_heading', lang)} ({target.isoformat()})", ""]
    for row in rows:
        lines.append(f"{row.factory_name} — {row.dish_name}: {row.count}")
    await message.answer("\n".join(lines))


@router.message(Command("kitchen"))
async def cmd_kitchen(message: Message, session, user: User, lang: str) -> None:
    """Ertangi kun uchun oshxona ishlab chiqarish rejasi."""
    if not await _require_admin(message, user, lang):
        return
    await _send_kitchen_plan(message, session, lang, date.today() + timedelta(days=1))


@router.message(Command("kitchen_today"))
async def cmd_kitchen_today(message: Message, session, user: User, lang: str) -> None:
    """Bugungi kun uchun oshxona ishlab chiqarish rejasi."""
    if not await _require_admin(message, user, lang):
        return
    await _send_kitchen_plan(message, session, lang, date.today())


@router.message(Command("sheet"))
async def cmd_sheet(message: Message, session, user: User, lang: str) -> None:
    """Ertangi kunlik kuryer ro'yxatini CSV fayl ko'rinishida yuboradi."""
    if not await _require_admin(message, user, lang):
        return
    target = date.today() + timedelta(days=1)
    rows = await get_courier_sheet(session, target, lang)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Fabrika", "Manzil", "Vaqt oralig'i", "Ism", "Telefon", "Joylashuv", "Taom"])
    for row in rows:
        writer.writerow(
            [row.factory_name, row.address, row.delivery_window, row.full_name, row.phone, row.delivery_note, row.dish_name]
        )

    # utf-8-sig — Excel faylni ochganda o'zbekcha/ruscha harflarni to'g'ri ko'rsatishi uchun
    data = buffer.getvalue().encode("utf-8-sig")
    document = BufferedInputFile(data, filename=f"kuryer_{target.isoformat()}.csv")
    await message.answer_document(document)


@router.message(Command("pending"))
async def cmd_pending(message: Message, session, user: User, lang: str) -> None:
    """To'lov kutayotgan barcha buyurtmalar ro'yxati."""
    if not await _require_admin(message, user, lang):
        return
    result = await session.execute(
        select(Order).where(Order.status == OrderStatus.AWAITING_PAYMENT).order_by(Order.created_at)
    )
    orders = result.scalars().all()
    if not orders:
        await message.answer(t("no_pending_orders", lang))
        return

    lines = [t("pending_heading", lang), ""]
    for order in orders:
        lines.append(f"{order.reference} — {money(order.amount_krw)} won — /ok {order.reference}")
    await message.answer("\n".join(lines))


@router.message(Command("ok"))
async def cmd_ok(message: Message, session, user: User, lang: str) -> None:
    """/ok BUYURTMA_KODI — to'lovni qo'lda tasdiqlaydi."""
    if not await _require_admin(message, user, lang):
        return
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer("Foydalanish: /ok HLXXXXXX")
        return
    await _confirm_order(message.bot, session, reference=parts[1], notify_message=message)


@router.callback_query(F.data.startswith("adminok:"))
async def on_admin_confirm(callback: CallbackQuery, session, user: User, lang: str) -> None:
    """Admin inline "Tasdiqlash" tugmasini bosganda."""
    if not user.is_admin:
        await callback.answer(t("admin_only", lang), show_alert=True)
        return
    reference = callback.data.split(":", 1)[1]
    await _confirm_order(callback.bot, session, reference=reference, notify_callback=callback)


@router.callback_query(F.data.startswith("adminno:"))
async def on_admin_reject(callback: CallbackQuery, session, user: User, lang: str) -> None:
    """Admin inline "Rad etish" tugmasini bosganda."""
    if not user.is_admin:
        await callback.answer(t("admin_only", lang), show_alert=True)
        return

    reference = callback.data.split(":", 1)[1]
    order = await get_order_by_reference(session, reference)
    if order is None:
        await callback.answer(t("admin_order_not_found", lang), show_alert=True)
        return

    order.status = OrderStatus.CANCELLED
    await session.flush()

    order_user = await session.get(User, order.user_id)
    user_lang = order_user.lang.value if order_user.lang else "uz"
    await safe_send(callback.bot, order_user.telegram_id, t("payment_rejected_notify_user", user_lang))

    await callback.answer(t("admin_order_rejected", lang, reference=reference))
    await callback.message.edit_reply_markup(reply_markup=None)


async def _confirm_order(
    bot,
    session,
    *,
    reference: str,
    notify_message: Message | None = None,
    notify_callback: CallbackQuery | None = None,
) -> None:
    """`/ok` buyrug'i va inline "Tasdiqlash" tugmasi uchun umumiy mantiq."""
    order = await get_order_by_reference(session, reference)
    if order is None:
        text = t("admin_order_not_found", "uz")
        if notify_message:
            await notify_message.answer(text)
        if notify_callback:
            await notify_callback.answer(text, show_alert=True)
        return

    try:
        subscription = await confirm_payment(session, order, lang="uz")
    except BusinessError as exc:
        if notify_message:
            await notify_message.answer(exc.message)
        if notify_callback:
            await notify_callback.answer(exc.message, show_alert=True)
        return

    order_user = await session.get(User, order.user_id)
    user_lang = order_user.lang.value if order_user.lang else "uz"
    await safe_send(
        bot,
        order_user.telegram_id,
        t(
            "payment_confirmed_notify_user",
            user_lang,
            starts_on=subscription.starts_on.isoformat(),
            ends_on=subscription.ends_on.isoformat(),
        ),
    )

    confirm_text = t("admin_order_confirmed", "uz", reference=reference)
    if notify_message:
        await notify_message.answer(confirm_text)
    if notify_callback:
        await notify_callback.answer(confirm_text)
        await notify_callback.message.edit_reply_markup(reply_markup=None)
