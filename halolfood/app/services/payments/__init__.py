"""Barcha to'lov provayderlarini shu yerda import qilish kerak — shunda ular
`register_provider` dekoratori orqali avtomatik ro'yxatdan o'tadi.

Yangi provayder qo'shish uchun:
1. `app/services/payments/toss.py` (yoki boshqa nom) faylini yozing,
   `PaymentProvider`dan meros oling va `@register_provider` bilan belgilang.
2. Quyidagi ro'yxatga import qatorini qo'shing.
3. .env faylida PAYMENT_PROVIDER=toss deb o'zgartiring.
"""
from __future__ import annotations

from app.services.payments import manual  # noqa: F401 — ro'yxatdan o'tkazish uchun import qilinadi

# Kelajakda qo'shiladigan provayderlar shu yerga import qilinadi, masalan:
# from app.services.payments import toss  # noqa: F401
# from app.services.payments import kakaopay  # noqa: F401

from app.services.payments.base import PaymentIntent, PaymentProvider, PaymentResult, available_providers, get_provider  # noqa: E402,F401
