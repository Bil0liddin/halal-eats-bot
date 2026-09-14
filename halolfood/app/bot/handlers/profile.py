"""Profil bo'limi: ma'lumotlarni ko'rish, tahrirlash, tilni o'zgartirish, yordam."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import (
    edit_profile_menu_keyboard,
    factory_keyboard,
    is_btn,
    language_keyboard,
    main_menu_keyboard,
    phone_keyboard,
    profile_actions_keyboard,
)
from app.bot.notify import notify_admins
from app.bot.states import ChangeLanguage, EditProfile
from app.db.models import User
from app.i18n import t
from app.services.users import get_factory, list_active_factories, normalize_phone

router = Router(name="profile")


async def _profile_text(session, user: User, lang: str) -> str:
    factory = await get_factory(session, user.factory_id) if user.factory_id else None
    lines = [
        t("profile_heading", lang),
        "",
        f"{t('profile_name', lang)}: {user.full_name}",
        f"{t('profile_phone', lang)}: {user.phone}",
        f"{t('profile_factory', lang)}: {factory.name if factory else '-'}",
        f"{t('profile_lang', lang)}: {user.lang.value}",
    ]
    return "\n".join(lines)


@router.message(is_btn("btn_profile"))
async def show_profile(message: Message, state: FSMContext, session, user: User, lang: str) -> None:
    """Foydalanuvchi profilini ko'rsatadi — tahrirlash va tilni o'zgartirish tugmalari bilan."""
    await state.clear()
    await message.answer(await _profile_text(session, user, lang), reply_markup=profile_actions_keyboard(lang))


@router.message(is_btn("btn_help"))
async def show_help(message: Message, lang: str) -> None:
    """Yordam matnini yuboradi."""
    await message.answer(t("help_text", lang))


# ---------------------------------------------------------------------------
# Profil tugmalari: tahrirlash menyusi, orqaga, tilni o'zgartirish
# ---------------------------------------------------------------------------


@router.callback_query(F.data == "profile:edit")
async def on_edit_profile(callback: CallbackQuery, lang: str) -> None:
    """"Tahrirlash" bosilganda — qaysi maydonni o'zgartirish tanlanadi."""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=edit_profile_menu_keyboard(lang))


@router.callback_query(F.data == "profile:back")
async def on_edit_back(callback: CallbackQuery, session, user: User, lang: str) -> None:
    """Tahrirlash menyusidan profilga qaytish."""
    await callback.answer()
    await callback.message.edit_text(await _profile_text(session, user, lang), reply_markup=profile_actions_keyboard(lang))


@router.callback_query(F.data == "profile:change_lang")
async def on_change_lang(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    """"Tilni o'zgartirish" bosilganda."""
    await callback.answer()
    await callback.message.answer(t("choose_language", lang), reply_markup=language_keyboard())
    await state.set_state(ChangeLanguage.choosing)


# ---------------------------------------------------------------------------
# Ismni tahrirlash
# ---------------------------------------------------------------------------


@router.callback_query(F.data == "editfield:name")
async def on_edit_name_start(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await callback.answer()
    await callback.message.answer(t("ask_name", lang))
    await state.set_state(EditProfile.entering_name)


@router.message(EditProfile.entering_name)
async def on_edit_name_done(message: Message, state: FSMContext, session, user: User, lang: str) -> None:
    full_name = (message.text or "").strip()
    if not full_name:
        await message.answer(t("ask_name", lang))
        return
    user.full_name = full_name
    await state.clear()
    await message.answer(t("profile_updated", lang))
    await message.answer(await _profile_text(session, user, lang), reply_markup=profile_actions_keyboard(lang))


# ---------------------------------------------------------------------------
# Telefonni tahrirlash
# ---------------------------------------------------------------------------


@router.callback_query(F.data == "editfield:phone")
async def on_edit_phone_start(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await callback.answer()
    await callback.message.answer(t("ask_phone", lang), reply_markup=phone_keyboard(lang))
    await state.set_state(EditProfile.entering_phone)


@router.message(EditProfile.entering_phone, F.contact)
async def on_edit_phone_contact(message: Message, state: FSMContext, session, user: User, lang: str) -> None:
    await _finish_phone_edit(message, state, session, user, lang, raw_phone=message.contact.phone_number)


@router.message(EditProfile.entering_phone, F.text)
async def on_edit_phone_text(message: Message, state: FSMContext, session, user: User, lang: str) -> None:
    await _finish_phone_edit(message, state, session, user, lang, raw_phone=message.text or "")


async def _finish_phone_edit(
    message: Message, state: FSMContext, session, user: User, lang: str, *, raw_phone: str
) -> None:
    phone = normalize_phone(raw_phone)
    if phone is None:
        await message.answer(t("invalid_phone", lang))
        return
    user.phone = phone
    await state.clear()
    # Telefon-so'rash klaviaturasi o'rniga asosiy menyuni qaytaramiz
    await message.answer(t("profile_updated", lang), reply_markup=main_menu_keyboard(lang))
    await message.answer(await _profile_text(session, user, lang), reply_markup=profile_actions_keyboard(lang))


# ---------------------------------------------------------------------------
# Fabrikani tahrirlash
# ---------------------------------------------------------------------------


@router.callback_query(F.data == "editfield:factory")
async def on_edit_factory_start(callback: CallbackQuery, state: FSMContext, session, lang: str) -> None:
    await callback.answer()
    factories = await list_active_factories(session)
    await callback.message.answer(t("ask_factory", lang), reply_markup=factory_keyboard(factories, lang))
    await state.set_state(EditProfile.choosing_factory)


@router.callback_query(EditProfile.choosing_factory, F.data.startswith("factory:"))
async def on_edit_factory_chosen(callback: CallbackQuery, state: FSMContext, session, user: User, lang: str) -> None:
    await callback.answer()
    raw = callback.data.split(":", 1)[1]

    if raw == "none":
        await callback.message.answer(t("factory_not_listed_ask_name", lang))
        await state.set_state(EditProfile.entering_custom_factory)
        return

    user.factory_id = int(raw)
    await state.clear()
    await callback.message.answer(t("profile_updated", lang))
    await callback.message.answer(await _profile_text(session, user, lang), reply_markup=profile_actions_keyboard(lang))


@router.message(EditProfile.entering_custom_factory)
async def on_edit_custom_factory(message: Message, state: FSMContext, user: User, lang: str) -> None:
    """Fabrika ro'yxatda topilmasa, so'rov adminlarga yuboriladi (fabrika o'zgarishsiz qoladi)."""
    text = t(
        "factory_request_notify_admin",
        "uz",
        full_name=user.full_name or "?",
        username=user.username or "-",
        text=message.text or "",
    )
    await notify_admins(message.bot, text)

    await message.answer(t("factory_not_listed_sent", lang))
    await state.clear()


# ---------------------------------------------------------------------------
# Joylashuvni (fabrika ichidagi manzil) tahrirlash
# ---------------------------------------------------------------------------


@router.callback_query(F.data == "editfield:spot")
async def on_edit_spot_start(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await callback.answer()
    await callback.message.answer(t("ask_spot", lang))
    await state.set_state(EditProfile.entering_spot)


@router.message(EditProfile.entering_spot)
async def on_edit_spot_done(message: Message, state: FSMContext, session, user: User, lang: str) -> None:
    user.delivery_note = (message.text or "").strip() or None
    await state.clear()
    await message.answer(t("profile_updated", lang))
    await message.answer(await _profile_text(session, user, lang), reply_markup=profile_actions_keyboard(lang))
