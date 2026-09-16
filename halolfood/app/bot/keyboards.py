"""Botning barcha klaviaturalari (reply va inline) shu yerda to'plangan."""
from __future__ import annotations

from aiogram import F
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from app.config import settings
from app.db.models import Factory
from app.i18n import TEXTS, t


def is_btn(key: str):
    """Reply-klaviatura tugmasini, foydalanuvchi tilidan qat'i nazar aniqlaydigan filtr.

    Tugma matni 3 tilda mavjud bo'lgani uchun oddiy `F.text == "..."` ishlamaydi —
    bu filtr `TEXTS[key]`dagi barcha tildagi variantlarni tekshiradi.
    """
    return F.text.in_(set(TEXTS[key].values()))


def language_keyboard() -> InlineKeyboardMarkup:
    """Til tanlash uchun inline klaviatura."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            ]
        ]
    )


def phone_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Telefon raqamini yuborish uchun klaviatura (tugma orqali; qo'lda yozish ham qabul qilinadi)."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("share_contact_button", lang), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def factory_keyboard(factories: list[Factory], lang: str) -> InlineKeyboardMarkup:
    """Fabrikalar ro'yxati va "ro'yxatda yo'q" tugmasi."""
    rows = [[InlineKeyboardButton(text=f.name, callback_data=f"factory:{f.id}")] for f in factories]
    rows.append([InlineKeyboardButton(text=t("factory_not_listed_button", lang), callback_data="factory:none")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Asosiy reply-menyu (navigatsiya tugmalari).

    DIQQAT: Mini App tugmasi ATAYLAB shu klaviaturaga QO'SHILMAGAN — reply
    klaviaturadagi (pastki, doimiy) `web_app` tugmalari ba'zi Telegram
    versiyalarida `initData`ni bo'sh yuboradi. Shu sabab Mini App alohida,
    INLINE tugma sifatida yuboriladi (`menu_webapp_inline_keyboard`) — bu
    usul ishonchli ishlaydi.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_my_subscription", lang))],
            [KeyboardButton(text=t("btn_profile", lang)), KeyboardButton(text=t("btn_help", lang))],
        ],
        resize_keyboard=True,
    )


def menu_webapp_inline_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Mini App'ni ochadigan INLINE tugma — reply klaviaturadagi web_app tugmasidan farqli, initData'ni ishonchli yuboradi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t("btn_open_app", lang), web_app=WebAppInfo(url=settings.webapp_url))]]
    )


def profile_actions_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Profil ostida ko'rsatiladigan tugmalar: tahrirlash va tilni o'zgartirish."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("edit_profile_button", lang), callback_data="profile:edit")],
            [InlineKeyboardButton(text=t("change_language_button", lang), callback_data="profile:change_lang")],
        ]
    )


def edit_profile_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Qaysi maydonni tahrirlashni tanlash menyusi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("edit_field_name", lang), callback_data="editfield:name")],
            [InlineKeyboardButton(text=t("edit_field_phone", lang), callback_data="editfield:phone")],
            [InlineKeyboardButton(text=t("edit_field_factory", lang), callback_data="editfield:factory")],
            [InlineKeyboardButton(text=t("edit_field_spot", lang), callback_data="editfield:spot")],
            [InlineKeyboardButton(text=t("back_button", lang), callback_data="profile:back")],
        ]
    )


def payment_action_keyboard(reference: str, lang: str) -> InlineKeyboardMarkup:
    """Qo'lda bank o'tkazmasi holatida ko'rsatiladigan "To'ladim" tugmasi. Buyurtma kodi callback'ga yashiriladi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t("i_paid_button", lang), callback_data=f"paid:confirm:{reference}")]]
    )


def pay_url_keyboard(url: str, lang: str) -> InlineKeyboardMarkup:
    """Karta orqali to'lov uchun tayyor havola (checkout_url mavjud bo'lgan provayderlar uchun)."""
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t("pay_now_button", lang), url=url)]])


def admin_confirm_keyboard(reference: str, lang: str = "uz") -> InlineKeyboardMarkup:
    """Admin uchun to'lovni tasdiqlash/rad etish tugmalari."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("admin_confirm_button", lang), callback_data=f"adminok:{reference}"),
                InlineKeyboardButton(text=t("admin_reject_button", lang), callback_data=f"adminno:{reference}"),
            ]
        ]
    )
