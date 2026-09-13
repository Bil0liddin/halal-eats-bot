"""To'lov provayderlari uchun mavhum interfeys (abstraction layer).

BU ENG MUHIM FAYL. Kelajakda haqiqiy to'lov provayderi (Toss, KakaoPay va h.k.)
qo'shilganda, faqat: (1) shu interfeysni amalga oshiruvchi BITTA yangi fayl
yoziladi, (2) .env faylida PAYMENT_PROVIDER qiymati o'zgartiriladi. Boshqa hech
narsaga — na botga, na servislarga — tegilmaydi.

`instructions` va `checkout_url` ikkalasi ham mavjudligi sababi: bank o'tkazmasi
matn (instructions) qaytaradi, karta orqali to'lov esa havola (checkout_url)
qaytaradi. Ikkalasi ham BITTA interfeysga sig'ishi kerak.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.config import settings


@dataclass
class PaymentIntent:
    """To'lovni boshlash natijasi — foydalanuvchiga ko'rsatiladigan ma'lumot."""

    provider: str
    instructions: str | None = None  # bank o'tkazmasi tafsilotlari — matn ko'rinishida
    checkout_url: str | None = None  # tayyor karta to'lov sahifasi havolasi
    provider_payment_id: str | None = None
    raw: dict = field(default_factory=dict)


@dataclass
class PaymentResult:
    """To'lovni tasdiqlash (webhook yoki admin tasdig'i) natijasi."""

    success: bool
    order_reference: str | None = None
    amount_krw: int | None = None
    provider_payment_id: str | None = None
    message: str = ""
    raw: dict = field(default_factory=dict)


class PaymentProvider(ABC):
    """Har qanday to'lov provayderi shu klassdan meros olishi kerak."""

    name: str = "base"
    auto_confirm: bool = False  # True bo'lsa — webhook to'lovni o'zi avtomatik tasdiqlaydi

    @abstractmethod
    async def create_payment(
        self,
        *,
        reference: str,
        amount_krw: int,
        description: str,
        lang: str = "uz",
        **extra,
    ) -> PaymentIntent:
        """Yangi to'lovni boshlaydi va foydalanuvchiga ko'rsatiladigan ma'lumotni qaytaradi."""
        raise NotImplementedError

    @abstractmethod
    async def verify_callback(self, payload: dict) -> PaymentResult:
        """Provayderdan kelgan webhook/callback ma'lumotini tekshiradi va natijasini qaytaradi."""
        raise NotImplementedError

    async def refund(self, *, provider_payment_id: str, amount_krw: int) -> PaymentResult:
        """Pulni qaytarish. Ko'pchilik provayderlar (masalan qo'lda o'tkazma) buni qo'llab-quvvatlamaydi."""
        return PaymentResult(success=False, message="not supported")


_REGISTRY: dict[str, PaymentProvider] = {}


def register_provider(cls: type[PaymentProvider]) -> type[PaymentProvider]:
    """Provayder klassini ro'yxatga oladigan dekorator. `app/services/payments/__init__.py` orqali chaqiriladi."""
    instance = cls()
    _REGISTRY[instance.name] = instance
    return cls


def get_provider(name: str | None = None) -> PaymentProvider:
    """Nomi bo'yicha provayderni qaytaradi. Nom berilmasa, .env dagi PAYMENT_PROVIDER ishlatiladi."""
    provider_name = name or settings.payment_provider
    if provider_name not in _REGISTRY:
        raise ValueError(
            f"Noma'lum to'lov provayderi: '{provider_name}'. Mavjudlari: {available_providers()}"
        )
    return _REGISTRY[provider_name]


def available_providers() -> list[str]:
    """Ro'yxatga olingan barcha provayderlar nomini qaytaradi."""
    return list(_REGISTRY.keys())
