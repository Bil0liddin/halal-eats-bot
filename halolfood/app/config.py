"""Ilova sozlamalari. Barcha qiymatlar .env faylidan o'qiladi (pydantic-settings)."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Butun tizim uchun yagona sozlamalar manbai."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Telegram
    bot_token: str
    webapp_url: str = "https://example.com"
    admin_ids: str = ""  # vergul bilan ajratilgan Telegram ID'lar, masalan "111,222"

    # Baza va kesh
    database_url: str = "postgresql+asyncpg://halol:halol@localhost:5432/halolfood"
    redis_url: str = "redis://localhost:6379/0"

    # Biznes qoidalari
    timezone: str = "Asia/Seoul"
    order_cutoff_hour: int = 20  # shu soatdan keyin ertangi kunni bekor qilib bo'lmaydi
    renewal_reminder_days: int = 3  # obuna tugashiga necha kun qolganda eslatish

    # To'lov
    payment_provider: str = "manual"
    manual_bank_name: str = "KB Kookmin Bank"
    manual_bank_account: str = "000-0000-0000-00"
    manual_bank_holder: str = "Halol Food"

    # Hodisalarni tashqi webhook'ga (n8n) yuborish — sinov uchun, ixtiyoriy.
    # Bo'sh bo'lsa hech narsa yuborilmaydi.
    n8n_webhook_url: str = ""

    @property
    def admin_id_list(self) -> list[int]:
        """ADMIN_IDS satrini butun sonlar ro'yxatiga aylantiradi."""
        return [int(x) for x in self.admin_ids.split(",") if x.strip()]


settings = Settings()
