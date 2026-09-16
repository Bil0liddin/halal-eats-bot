"""Botdagi muhim hodisalarni tashqi webhook'ga (hozircha n8n, sinov uchun) yuboradi.

QOIDA: bu butunlay YON tarafdagi (side-effect) funksiya — webhook sekin
ishlasa, xato qaytarsa yoki umuman javob bermasa ham, botning asosiy
ishi (foydalanuvchiga javob berish, buyurtma yaratish va h.k.) HECH
QACHON to'xtab qolmasligi kerak. Shu sabab `log_event()` hech narsani
`await` qilishga majburlamaydi — HTTP so'rovini fon vazifasi (background
task) sifatida ishga tushiradi va o'zi darhol qaytadi; barcha xatolar
faqat log'ga yoziladi.
"""
from __future__ import annotations

import asyncio
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 5.0


def log_event(event_type: str, user_id: int | str, user_name: str, details: str) -> None:
    """Hodisani webhook'ga yuborishni fon vazifasi sifatida ishga tushiradi (fire-and-forget)."""
    if not settings.n8n_webhook_url:
        return
    asyncio.create_task(_send_event(event_type, str(user_id), user_name, details))


async def _send_event(event_type: str, user_id: str, user_name: str, details: str) -> None:
    payload = {
        "event_type": event_type,
        "user_id": user_id,
        "user_name": user_name,
        "details": details,
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            await client.post(
                settings.n8n_webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
    except Exception:
        logger.warning("n8n webhook yuborilmadi (event_type=%s)", event_type, exc_info=True)
