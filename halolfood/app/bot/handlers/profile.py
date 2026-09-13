"""Profil bo'limi: ma'lumotlarni ko'rish, tilni o'zgartirish, yordam."""
from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.keyboards import is_btn, language_keyboard
from app.bot.states import ChangeLanguage
from app.i18n import t
from app.services.users import get_factory

router = Router(name="profile")


@router.message(is_btn("btn_profile"))
async def show_profile(message: Message, state: FSMContext, session, user, lang: str) -> None:
    """Foydalanuvchi profilini ko'rsatadi va tilni o'zgartirish imkonini beradi."""
    factory = await get_factory(session, user.factory_id) if user.factory_id else None
    lines = [
        t("profile_heading", lang),
        "",
        f"{t('profile_name', lang)}: {user.full_name}",
        f"{t('profile_phone', lang)}: {user.phone}",
        f"{t('profile_factory', lang)}: {factory.name if factory else '-'}",
        f"{t('profile_lang', lang)}: {user.lang.value}",
    ]
    await message.answer("\n".join(lines))
    await message.answer(t("change_language_button", lang), reply_markup=language_keyboard())
    await state.set_state(ChangeLanguage.choosing)


@router.message(is_btn("btn_help"))
async def show_help(message: Message, lang: str) -> None:
    """Yordam matnini yuboradi."""
    await message.answer(t("help_text", lang))
