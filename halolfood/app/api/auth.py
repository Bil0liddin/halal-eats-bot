"""Mini App'dan kelgan so'rovlarni tekshirish.

ENG XAVFSIZLIK JIHATIDAN MUHIM FAYL. Telegram WebApp `initData`sining
haqiqiyligini HMAC imzo orqali tekshiradi. Bu tekshiruvsiz HECH QANDAY API
endpoint ishlamasligi kerak — aks holda istalgan kishi boshqa foydalanuvchi
nomidan so'rov yubora oladi.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from collections.abc import AsyncIterator
from urllib.parse import parse_qsl

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import User
from app.db.session import SessionMaker
from app.services.users import get_or_create_user

MAX_AUTH_AGE_SECONDS = 24 * 60 * 60  # 24 soat — bundan eski initData rad etiladi


def verify_init_data(init_data: str) -> dict:
    """`initData` imzosini tekshiradi va ichidagi Telegram foydalanuvchi ma'lumotini qaytaradi.

    Formula: secret = HMAC_SHA256(key=b"WebAppData", msg=bot_token)
             hash   = HMAC_SHA256(key=secret, msg=data_check_string)

    Har qanday nomuvofiqlikda HTTPException(401) chiqaradi.
    """
    if not init_data:
        raise HTTPException(status_code=401, detail="initData yo'q")

    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        raise HTTPException(status_code=401, detail="initData formati noto'g'ri") from None

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=401, detail="hash yo'q")

    # data_check_string: "hash"dan boshqa barcha kalitlar, alifbo tartibida, "key=value" ko'rinishida, "\n" bilan qo'shilgan
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))

    secret_key = hmac.new(b"WebAppData", settings.bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    # hmac.compare_digest — vaqt bo'yicha hujumdan (timing attack) himoya qiladi
    if not hmac.compare_digest(computed_hash, received_hash):
        raise HTTPException(status_code=401, detail="Imzo noto'g'ri")

    auth_date = parsed.get("auth_date")
    if auth_date is None:
        raise HTTPException(status_code=401, detail="auth_date yo'q")
    if time.time() - int(auth_date) > MAX_AUTH_AGE_SECONDS:
        raise HTTPException(status_code=401, detail="initData muddati o'tgan (24 soatdan eski)")

    user_raw = parsed.get("user")
    if not user_raw:
        raise HTTPException(status_code=401, detail="user ma'lumoti yo'q")

    try:
        return json.loads(user_raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=401, detail="user ma'lumoti noto'g'ri formatda") from None


async def get_session() -> AsyncIterator[AsyncSession]:
    """Bitta HTTP so'rov davomida ishlatiladigan ma'lumotlar bazasi sessiyasi."""
    async with SessionMaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def current_user(
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    session: AsyncSession = Depends(get_session),
) -> User:
    """So'rovni yuborgan Telegram foydalanuvchisini aniqlaydi (imzoni tekshirgach) va bazadan topadi/yaratadi."""
    tg_user = verify_init_data(x_telegram_init_data)
    user = await get_or_create_user(session, telegram_id=tg_user["id"], username=tg_user.get("username"))
    return user
