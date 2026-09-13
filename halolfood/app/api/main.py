"""Mini App API va to'lov webhook'lari uchun FastAPI ilovasi."""
from __future__ import annotations

import logging
from urllib.parse import urlparse

from aiogram import Bot
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import current_user
from app.api.routes import cart, menu, orders, webapp
from app.bot.notify import safe_send
from app.config import settings
from app.db.models import User
from app.db.session import SessionMaker
from app.i18n import t
from app.services.payments import get_provider
from app.services.subscriptions import BusinessError, confirm_payment, get_order_by_reference

logger = logging.getLogger(__name__)

app = FastAPI(title="Halol Food API")

# Faqat Telegram Web App va bizning Mini App manzilimizdan kelgan so'rovlarga ruxsat.
# WEBAPP_URL to'liq sahifa yo'lini o'z ichiga olishi mumkin (masalan ".../webapp"),
# CORS esa faqat domen (origin) qismini kutadi — shuning uchun ajratib olinadi.
_webapp_origin = urlparse(settings.webapp_url)
_webapp_origin_str = f"{_webapp_origin.scheme}://{_webapp_origin.netloc}"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://web.telegram.org", _webapp_origin_str],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(menu.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(webapp.router)

_bot = Bot(token=settings.bot_token)


@app.get("/api/me")
async def get_me(user: User = Depends(current_user)):
    """Mini App ochilganda foydalanuvchining tili va ro'yxatdan o'tganligini bilish uchun."""
    return {
        "lang": user.lang.value if user.lang else "uz",
        "is_registered": user.is_registered,
        "full_name": user.full_name,
    }


@app.post("/webhook/payment/{provider_name}")
async def payment_webhook(provider_name: str, request: Request):
    """To'lov provayderidan kelgan webhook'ni qabul qiladi va to'lovni tasdiqlaydi.

    HOZIRCHA ISHLATILMAYDI — faqat "manual" (bank o'tkazmasi) provayderi bor,
    unda webhook mavjud emas. Lekin bu funksiya TO'LIQ ishlaydigan holda
    yozilgan: yangi (avtomatik) provayder qo'shilganda bu yerga HECH NARSA
    o'zgartirish shart emas, faqat provayderning o'zi ro'yxatdan o'tkaziladi.
    """
    provider = get_provider(provider_name)
    payload = await request.json()

    result = await provider.verify_callback(payload)
    if not result.success:
        logger.warning("Webhook tasdiqlanmadi (%s): %s", provider_name, result.message)
        raise HTTPException(status_code=400, detail=result.message or "Tasdiqlanmadi")

    async with SessionMaker() as session:
        order = await get_order_by_reference(session, result.order_reference)
        if order is None:
            raise HTTPException(status_code=404, detail="Buyurtma topilmadi")

        user = await session.get(User, order.user_id)
        lang = user.lang.value if user.lang else "uz"

        try:
            subscription = await confirm_payment(
                session, order, provider_payment_id=result.provider_payment_id, lang=lang
            )
        except BusinessError as exc:
            await session.rollback()
            raise HTTPException(status_code=400, detail=exc.message) from exc

        await session.commit()

        await safe_send(
            _bot,
            user.telegram_id,
            t(
                "payment_confirmed_notify_user",
                lang,
                starts_on=subscription.starts_on.isoformat(),
                ends_on=subscription.ends_on.isoformat(),
            ),
        )

    return {"ok": True}


@app.get("/health")
async def health():
    """Server ishga tushganini tekshirish uchun oddiy endpoint."""
    return {"status": "ok"}
