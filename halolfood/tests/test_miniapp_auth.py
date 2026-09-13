"""Mini App autentifikatsiyasini (Telegram initData imzosi) sinovdan
o'tkazish — pytest SHART EMAS. Ishlatish: `python tests/test_miniapp_auth.py`

Sinovlar ro'yxati:
1. to'g'ri imzo qabul qilinishi
2. boshqa bot tokeni bilan soxtalashtirilgan imzo rad etilishi
3. o'zgartirilgan (tampered) ma'lumot rad etilishi
4. muddati o'tgan initData rad etilishi
5. hash yo'q bo'lganda rad etilishi
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ["BOT_TOKEN"] = "123456:REAL_TEST_TOKEN"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./_test_miniapp_auth.db"
os.environ.setdefault("WEBAPP_URL", "https://example.com")
os.environ.setdefault("ADMIN_IDS", "1")

import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

from fastapi import HTTPException

from app.api.auth import verify_init_data
from app.config import settings


def _sign(data: dict, bot_token: str) -> str:
    check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    return hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()


def _build_init_data(*, user_id: int = 12345, auth_date: int | None = None, bot_token: str | None = None) -> str:
    data = {
        "auth_date": str(auth_date if auth_date is not None else int(time.time())),
        "user": json.dumps({"id": user_id, "first_name": "Test"}),
        "query_id": "AAA",
    }
    data["hash"] = _sign(data, bot_token or settings.bot_token)
    return urlencode(data)


def main() -> None:
    # ---- 1. To'g'ri imzo qabul qilinishi ----
    valid = _build_init_data()
    user = verify_init_data(valid)
    assert user["id"] == 12345
    print("1. OK: to'g'ri imzo qabul qilindi")

    # ---- 2. Boshqa bot tokeni bilan soxtalashtirilgan imzo rad etilishi ----
    forged = _build_init_data(bot_token="000000:ANOTHER_BOT_TOKEN")
    try:
        verify_init_data(forged)
        raise AssertionError("Soxta imzo qabul qilindi — bu XATO!")
    except HTTPException as exc:
        assert exc.status_code == 401
        print("2. OK: boshqa token bilan soxtalashtirilgan imzo rad etildi")

    # ---- 3. O'zgartirilgan (tampered) ma'lumot rad etilishi ----
    data = {
        "auth_date": str(int(time.time())),
        "user": json.dumps({"id": 12345, "first_name": "Test"}),
        "query_id": "AAA",
    }
    data["hash"] = _sign(data, settings.bot_token)
    # Imzo hisoblab bo'lingandan KEYIN foydalanuvchi ID'sini o'zgartiramiz —
    # imzo endi mos kelmaydi
    data["user"] = json.dumps({"id": 99999, "first_name": "Hacker"})
    tampered = urlencode(data)
    try:
        verify_init_data(tampered)
        raise AssertionError("O'zgartirilgan ma'lumot qabul qilindi — bu XATO!")
    except HTTPException as exc:
        assert exc.status_code == 401
        print("3. OK: o'zgartirilgan (tampered) ma'lumot rad etildi")

    # ---- 4. Muddati o'tgan initData rad etilishi ----
    old_auth_date = int(time.time()) - 25 * 60 * 60  # 25 soat oldin — 24 soatlik limitdan oshadi
    expired = _build_init_data(auth_date=old_auth_date)
    try:
        verify_init_data(expired)
        raise AssertionError("Muddati o'tgan initData qabul qilindi — bu XATO!")
    except HTTPException as exc:
        assert exc.status_code == 401
        print("4. OK: muddati o'tgan (24 soatdan eski) initData rad etildi")

    # ---- 5. Hash yo'q bo'lganda rad etilishi ----
    data_no_hash = {
        "auth_date": str(int(time.time())),
        "user": json.dumps({"id": 12345, "first_name": "Test"}),
    }
    no_hash = urlencode(data_no_hash)
    try:
        verify_init_data(no_hash)
        raise AssertionError("Hash'siz ma'lumot qabul qilindi — bu XATO!")
    except HTTPException as exc:
        assert exc.status_code == 401
        print("5. OK: hash yo'q bo'lganda rad etildi")

    print("\nHAMMA 5 TA SINOV MUVAFFAQIYATLI O'TDI ✅")


if __name__ == "__main__":
    try:
        main()
    finally:
        db_path = "./_test_miniapp_auth.db"
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except OSError:
            pass
