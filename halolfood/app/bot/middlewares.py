"""Bot uchun middleware'lar.

ISHLASH TARTIBI (main.py'da shu tartibda ulanadi):
ErrorLogMiddleware -> DatabaseMiddleware -> UserMiddleware

ErrorLogMiddleware ENG TASHQARIDA turishi kerak — u ichkaridagi
DatabaseMiddleware va handler'lardan chiqadigan har qanday kutilmagan
xatolikni ham ushlab qolishi kerak.
"""
from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.config import settings
from app.db.session import SessionMaker
from app.i18n import DEFAULT_LANG, t
from app.services.users import get_or_create_user

logger = logging.getLogger(__name__)


def _extract_from_user(event: TelegramObject):
    if isinstance(event, (Message, CallbackQuery)):
        return event.from_user
    return None


def _extract_chat_id(event: TelegramObject) -> int | None:
    if isinstance(event, Message):
        return event.chat.id
    if isinstance(event, CallbackQuery) and event.message is not None:
        return event.message.chat.id
    return None


class DatabaseMiddleware(BaseMiddleware):
    """Har bir yangilanish uchun bitta ma'lumotlar bazasi sessiyasini ochadi va yopadi."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with SessionMaker() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise


class UserMiddleware(BaseMiddleware):
    """Foydalanuvchini bazadan topadi/yaratadi va `data["user"]`, `data["lang"]`ni to'ldiradi.

    Bloklangan foydalanuvchilarni handler'ga umuman kiritmaydi.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user = _extract_from_user(event)
        if tg_user is None:
            return await handler(event, data)

        session = data["session"]
        user = await get_or_create_user(session, telegram_id=tg_user.id, username=tg_user.username)

        # .env dagi ADMIN_IDS ro'yxatidagilarga avtomatik admin huquqi beriladi
        if tg_user.id in settings.admin_id_list and not user.is_admin:
            user.is_admin = True

        await session.flush()

        if user.is_blocked:
            return None  # bloklangan foydalanuvchiga hech qanday javob berilmaydi

        data["user"] = user
        data["lang"] = user.lang.value if user.lang else DEFAULT_LANG
        return await handler(event, data)


class ErrorLogMiddleware(BaseMiddleware):
    """Kutilmagan xatoliklarni jurnalga yozadi va foydalanuvchiga tushunarli xabar yuboradi.

    DIQQAT: bu faqat KUTILMAGAN (dasturchi bilmagan) xatoliklar uchun.
    Foydalanuvchi xatosi bo'lgan hollarda (masalan bo'sh savat) handler o'zi
    `BusinessError`ni ushlab, tushunarli xabar ko'rsatishi kerak.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception:
            logger.exception("Handlerda kutilmagan xatolik yuz berdi")
            bot = data.get("bot")
            chat_id = _extract_chat_id(event)
            lang = data.get("lang", DEFAULT_LANG)
            if bot is not None and chat_id is not None:
                try:
                    await bot.send_message(chat_id, t("error_generic", lang))
                except Exception:
                    logger.exception("Xato haqidagi xabarni ham yuborib bo'lmadi")
            return None
