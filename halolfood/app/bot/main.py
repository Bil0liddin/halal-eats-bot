"""Botni ishga tushirish nuqtasi."""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.handlers import admin, profile, start, subscription
from app.bot.middlewares import DatabaseMiddleware, ErrorLogMiddleware, UserMiddleware
from app.config import settings
from app.db.session import init_models
from app.scheduler.jobs import setup_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def _build_storage():
    """FSM holatlarini saqlash uchun Redis'ga ulanishga urinadi.

    Redis ishlamayotgan bo'lsa (masalan hali sozlanmagan bo'lsa), botning
    o'zi ishlashdan to'xtamasligi uchun vaqtinchalik xotiradagi
    (MemoryStorage) saqlashga o'tadi.
    """
    try:
        import redis.asyncio as redis_asyncio
        from aiogram.fsm.storage.redis import RedisStorage

        client = redis_asyncio.from_url(settings.redis_url)
        await client.ping()
        logger.info("FSM uchun Redis ishlatilmoqda: %s", settings.redis_url)
        return RedisStorage(redis=client)
    except Exception as exc:  # noqa: BLE001 — Redis xatosining aniq turi muhim emas
        logger.warning("Redis mavjud emas (%s) — FSM vaqtinchalik xotirada (MemoryStorage) saqlanadi", exc)
        return MemoryStorage()


def build_dispatcher(storage) -> Dispatcher:
    """Dispatcher'ni middleware'lar va routerlar bilan yig'adi."""
    dp = Dispatcher(storage=storage)

    # Tartib muhim: ErrorLogMiddleware -> DatabaseMiddleware -> UserMiddleware
    for middleware in (ErrorLogMiddleware(), DatabaseMiddleware(), UserMiddleware()):
        dp.message.outer_middleware(middleware)
        dp.callback_query.outer_middleware(middleware)

    dp.include_router(start.router)
    dp.include_router(subscription.router)
    dp.include_router(profile.router)
    dp.include_router(admin.router)

    return dp


async def main() -> None:
    await init_models()

    storage = await _build_storage()
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = build_dispatcher(storage)

    scheduler = setup_scheduler(bot)
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
