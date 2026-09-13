"""Xabar yuborishda xavfsizlik: botni bloklagan foydalanuvchilarni "yutib
yuborish" va Telegramning tezlik chekloviga (flood limit) rioya qilish.
"""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

logger = logging.getLogger(__name__)


async def safe_send(bot: Bot, chat_id: int, text: str, **kwargs) -> bool:
    """Bitta foydalanuvchiga xabar yuboradi.

    Foydalanuvchi botni bloklagan bo'lishi mumkin (TelegramForbiddenError) —
    bu butun ommaviy yuborish jarayonini to'xtatib qo'ymasligi kerak, shuning
    uchun xato shu yerning o'zida ushlab qolinadi.
    """
    try:
        await bot.send_message(chat_id, text, **kwargs)
        return True
    except TelegramForbiddenError:
        logger.info("Foydalanuvchi botni bloklagan: chat_id=%s", chat_id)
        return False
    except TelegramRetryAfter as exc:
        logger.warning("Telegram flood-limit: %s soniya kutilmoqda", exc.retry_after)
        await asyncio.sleep(exc.retry_after)
        return await safe_send(bot, chat_id, text, **kwargs)
    except Exception:
        logger.exception("Xabar yuborishda kutilmagan xatolik: chat_id=%s", chat_id)
        return False


async def broadcast(
    bot: Bot,
    chat_ids: list[int],
    *,
    text: str | None = None,
    text_by_chat: dict[int, str] | None = None,
) -> int:
    """Bir nechta foydalanuvchiga xabar yuboradi, Telegram limitiga rioya qilib
    soniyasiga ko'pi bilan 20 tadan yuboradi. Muvaffaqiyatli yuborilganlar sonini qaytaradi.
    """
    sent = 0
    for i, chat_id in enumerate(chat_ids, start=1):
        message = text_by_chat[chat_id] if text_by_chat is not None else text
        if message is None:
            continue
        if await safe_send(bot, chat_id, message):
            sent += 1
        if i % 20 == 0:
            await asyncio.sleep(1)
    return sent
