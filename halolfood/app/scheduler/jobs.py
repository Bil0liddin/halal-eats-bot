"""Rejalashtirilgan (vaqti bilan avtomatik ishlaydigan) vazifalar.

Barcha vaqtlar .env dagi TIMEZONE (odatda Asia/Seoul) bo'yicha hisoblanadi.
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from app.bot.notify import broadcast, safe_send
from app.config import settings
from app.db.models import BroadcastLog, Delivery, DeliveryStatus, Factory, MenuItem, Subscription, SubscriptionStatus, User
from app.db.session import SessionMaker
from app.i18n import t
from app.services.reports import confirm_tomorrow_deliveries, get_kitchen_plan
from app.services.subscriptions import expire_finished_subscriptions, expire_stale_orders

logger = logging.getLogger(__name__)

_TZ = ZoneInfo(settings.timezone)


async def job_remind_tomorrow_meal(bot: Bot) -> None:
    """19:00 — ertangi ovqat haqida eslatma yuboradi.

    `BroadcastLog` orqali bitta foydalanuvchiga bir kunda ikki marta
    yuborilmasligi ta'minlanadi (masalan vazifa qayta ishga tushirilsa ham).
    """
    tomorrow = date.today() + timedelta(days=1)
    kind = "tomorrow_meal_reminder"

    async with SessionMaker() as session:
        result = await session.execute(
            select(Delivery, User, Factory, MenuItem)
            .join(User, Delivery.user_id == User.id)
            .join(Factory, Delivery.factory_id == Factory.id)
            .join(MenuItem, Delivery.menu_item_id == MenuItem.id)
            .where(
                Delivery.delivery_date == tomorrow,
                Delivery.status.in_((DeliveryStatus.PLANNED, DeliveryStatus.CONFIRMED)),
            )
        )
        rows = result.all()

        already_sent = await session.execute(
            select(BroadcastLog.user_id).where(BroadcastLog.kind == kind, BroadcastLog.ref_date == tomorrow)
        )
        already_sent_ids = {row[0] for row in already_sent.all()}

        sent_count = 0
        for delivery, user, factory, menu_item in rows:
            if user.id in already_sent_ids:
                continue
            lang = user.lang.value if user.lang else "uz"
            text = t(
                "tomorrow_meal_reminder",
                lang,
                meal_name=menu_item.name(lang),
                factory=factory.name,
                window=factory.delivery_window,
            )
            if await safe_send(bot, user.telegram_id, text):
                sent_count += 1
            session.add(BroadcastLog(kind=kind, user_id=user.id, ref_date=tomorrow))

        await session.commit()
    logger.info("Ertangi ovqat eslatmasi: %s ta foydalanuvchiga yuborildi", sent_count)


async def job_kitchen_plan(bot: Bot) -> None:
    """20:30 — barcha "planned" yetkazishlarni "confirmed" holatiga o'tkazadi va oshxona rejasini adminlarga yuboradi."""
    tomorrow = date.today() + timedelta(days=1)

    async with SessionMaker() as session:
        flipped = await confirm_tomorrow_deliveries(session, tomorrow)
        await session.commit()
        rows = await get_kitchen_plan(session, tomorrow, lang="uz")

    if not rows:
        text = f"{t('kitchen_heading', 'uz')} ({tomorrow.isoformat()})\n\n—"
    else:
        lines = [f"{t('kitchen_heading', 'uz')} ({tomorrow.isoformat()})", ""]
        lines.extend(f"{row.factory_name} — {row.dish_name}: {row.count}" for row in rows)
        text = "\n".join(lines)

    await broadcast(bot, settings.admin_id_list, text=text)
    logger.info("Oshxona rejasi yuborildi, %s ta yetkazish tasdiqlandi", flipped)


async def job_renewal_reminder(bot: Bot) -> None:
    """09:00 — obunasi tez orada tugaydigan foydalanuvchilarga eslatma yuboradi (har biriga faqat bir marta)."""
    today = date.today()
    threshold = today + timedelta(days=settings.renewal_reminder_days)

    async with SessionMaker() as session:
        result = await session.execute(
            select(Subscription, User)
            .join(User, Subscription.user_id == User.id)
            .where(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.ends_on <= threshold,
                Subscription.ends_on >= today,
                Subscription.renewal_reminded_at.is_(None),
            )
        )
        rows = result.all()

        sent_count = 0
        for subscription, user in rows:
            lang = user.lang.value if user.lang else "uz"
            days_left = (subscription.ends_on - today).days
            text = t("renewal_reminder", lang, days=days_left, open_app=t("btn_open_app", lang))
            if await safe_send(bot, user.telegram_id, text):
                sent_count += 1
            subscription.renewal_reminded_at = datetime.now(_TZ)

        await session.commit()
    logger.info("Obuna tugash eslatmasi: %s ta foydalanuvchiga yuborildi", sent_count)


async def job_expire_stale(bot: Bot) -> None:
    """03:00 — muddati o'tgan (48 soatdan ortiq to'lanmagan) buyurtmalar va tugagan obunalarni yopadi."""
    now = datetime.now(_TZ)
    async with SessionMaker() as session:
        expired_orders = await expire_stale_orders(session, now=now)
        expired_subs = await expire_finished_subscriptions(session, today=now.date())
        await session.commit()
    logger.info("Muddati o'tgani uchun yopildi: %s ta buyurtma, %s ta obuna", expired_orders, expired_subs)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Barcha rejalashtirilgan vazifalarni sozlangan vaqt mintaqasida ro'yxatga oladi."""
    scheduler = AsyncIOScheduler(timezone=_TZ)

    scheduler.add_job(job_remind_tomorrow_meal, CronTrigger(hour=19, minute=0, timezone=_TZ), args=[bot])
    scheduler.add_job(job_kitchen_plan, CronTrigger(hour=20, minute=30, timezone=_TZ), args=[bot])
    scheduler.add_job(job_renewal_reminder, CronTrigger(hour=9, minute=0, timezone=_TZ), args=[bot])
    scheduler.add_job(job_expire_stale, CronTrigger(hour=3, minute=0, timezone=_TZ), args=[bot])

    return scheduler
