"""Qo'lda bank o'tkazmasi orqali to'lov provayderi.

Hozircha yagona ishlaydigan provayder shu. Bank hisob ma'lumotlari FAQAT .env
faylida saqlanadi, kodga yozilmaydi.
"""
from __future__ import annotations

from app.config import settings
from app.services.payments.base import PaymentIntent, PaymentProvider, PaymentResult, register_provider

_INSTRUCTIONS = {
    "uz": (
        "💳 To'lov uchun quyidagi hisobga o'tkazma qiling:\n\n"
        "Bank: {bank_name}\n"
        "Hisob raqami: {bank_account}\n"
        "Qabul qiluvchi: {bank_holder}\n"
        "Summa: {amount} won\n\n"
        "⚠️ Jo'natuvchi ismi o'rniga, aynan shuni kiriting: {reference}\n\n"
        "To'lovni amalga oshirgach, pastdagi \"To'ladim\" tugmasini bosing."
    ),
    "ru": (
        "💳 Переведите оплату на следующий счёт:\n\n"
        "Банк: {bank_name}\n"
        "Номер счёта: {bank_account}\n"
        "Получатель: {bank_holder}\n"
        "Сумма: {amount} вон\n\n"
        "⚠️ Вместо имени отправителя введите именно это: {reference}\n\n"
        "После оплаты нажмите кнопку \"Я оплатил\" ниже."
    ),
    "en": (
        "💳 Please transfer the payment to this account:\n\n"
        "Bank: {bank_name}\n"
        "Account number: {bank_account}\n"
        "Account holder: {bank_holder}\n"
        "Amount: {amount} won\n\n"
        "⚠️ Instead of the sender's name, enter exactly this: {reference}\n\n"
        "After paying, tap the \"I've paid\" button below."
    ),
}


@register_provider
class ManualBankTransfer(PaymentProvider):
    """Bank o'tkazmasi — admin qo'lda tasdiqlaydi, webhook orqali avtomatik tasdiqlanmaydi."""

    name = "manual"
    auto_confirm = False

    async def create_payment(
        self,
        *,
        reference: str,
        amount_krw: int,
        description: str,
        lang: str = "uz",
        **extra,
    ) -> PaymentIntent:
        """Bank o'tkazmasi ma'lumotlarini foydalanuvchi tiliga mos matn ko'rinishida qaytaradi."""
        template = _INSTRUCTIONS.get(lang, _INSTRUCTIONS["uz"])
        text = template.format(
            bank_name=settings.manual_bank_name,
            bank_account=settings.manual_bank_account,
            bank_holder=settings.manual_bank_holder,
            amount=f"{amount_krw:,}",
            reference=reference,
        )
        return PaymentIntent(
            provider=self.name,
            instructions=text,
            checkout_url=None,
            provider_payment_id=None,
            raw={"reference": reference, "amount_krw": amount_krw},
        )

    async def verify_callback(self, payload: dict) -> PaymentResult:
        """Bank o'tkazmasida avtomatik webhook yo'q — tasdiqlash faqat admin orqali (/ok buyrug'i)."""
        return PaymentResult(
            success=False,
            message="Qo'lda bank o'tkazmasi avtomatik tasdiqlanmaydi — admin /ok buyrug'i orqali tasdiqlaydi.",
        )
