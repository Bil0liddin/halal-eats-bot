"""Ro'yxatdan o'tish oqimi: til -> ism -> telefon -> fabrika -> joylashuv."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import (
    factory_keyboard,
    language_keyboard,
    main_menu_keyboard,
    menu_webapp_inline_keyboard,
    phone_keyboard,
)
from app.bot.notify import notify_admins
from app.bot.states import Registration
from app.i18n import t
from app.services.event_log import log_event
from app.services.users import (
    complete_registration,
    list_active_factories,
    normalize_phone,
    set_language,
)

router = Router(name="start")


async def _send_main_menu(target, lang: str) -> None:
    """Asosiy reply-menyuni va Mini App'ni ochuvchi inline tugmani birga yuboradi.

    Ikkalasi ALOHIDA xabarlar — chunki reply-klaviaturadagi `web_app` tugmasi
    `initData`ni ishonchli yubormaydi, shuning uchun Mini App faqat inline
    tugma orqali ochiladi (`menu_webapp_inline_keyboard`).
    """
    await target.answer(t("welcome", lang), reply_markup=main_menu_keyboard(lang))
    await target.answer(t("open_app_prompt", lang), reply_markup=menu_webapp_inline_keyboard(lang))


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, user, lang: str) -> None:
    """Botni /start bilan ishga tushirish. Ro'yxatdan o'tgan bo'lsa — to'g'ridan-to'g'ri asosiy menyu ko'rsatiladi."""
    await state.clear()
    if user.is_registered:
        await _send_main_menu(message, lang)
        return
    await message.answer(t("choose_language", lang), reply_markup=language_keyboard())
    await state.set_state(Registration.choosing_language)


@router.callback_query(F.data.startswith("lang:"))
async def on_language_chosen(callback: CallbackQuery, state: FSMContext, session, user) -> None:
    """Til tanlanganda ishga tushadi — ham ro'yxatdan o'tishda, ham profildan chaqirilganda."""
    lang = callback.data.split(":", 1)[1]
    await set_language(session, user, lang)
    await session.flush()
    await callback.answer()

    current_state = await state.get_state()
    if current_state == Registration.choosing_language.state:
        await callback.message.edit_text(t("welcome", lang))
        await callback.message.answer(t("ask_name", lang))
        await state.set_state(Registration.entering_name)
    else:
        # Profildan chaqirilgan bo'lsa — shunchaki tasdiqlaymiz va asosiy menyuni yangilaymiz
        await callback.message.edit_text(t("language_changed", lang))
        await _send_main_menu(callback.message, lang)
        await state.clear()


@router.message(Registration.entering_name)
async def on_name_entered(message: Message, state: FSMContext, lang: str) -> None:
    """Ism kiritilgach, telefon so'raladi."""
    full_name = (message.text or "").strip()
    if not full_name:
        await message.answer(t("ask_name", lang))
        return
    await state.update_data(full_name=full_name)
    await message.answer(t("ask_phone", lang), reply_markup=phone_keyboard(lang))
    await state.set_state(Registration.entering_phone)


@router.message(Registration.entering_phone, F.contact)
async def on_phone_shared(message: Message, state: FSMContext, session, lang: str) -> None:
    """Foydalanuvchi "Raqamni yuborish" tugmasini bosganda ishga tushadi."""
    await _save_phone_and_ask_factory(message, state, session, lang, raw_phone=message.contact.phone_number)


@router.message(Registration.entering_phone, F.text)
async def on_phone_typed(message: Message, state: FSMContext, session, lang: str) -> None:
    """Foydalanuvchi telefon raqamini qo'lda yozganda ishga tushadi."""
    await _save_phone_and_ask_factory(message, state, session, lang, raw_phone=message.text or "")


async def _save_phone_and_ask_factory(
    message: Message, state: FSMContext, session, lang: str, *, raw_phone: str
) -> None:
    """Telefon raqamini tekshiradi, to'g'ri bo'lsa fabrika tanlashga o'tkazadi."""
    phone = normalize_phone(raw_phone)
    if phone is None:
        await message.answer(t("invalid_phone", lang))
        return
    await state.update_data(phone=phone)

    factories = await list_active_factories(session)
    await message.answer(t("ask_factory", lang), reply_markup=factory_keyboard(factories, lang))
    await state.set_state(Registration.choosing_factory)


@router.callback_query(Registration.choosing_factory, F.data.startswith("factory:"))
async def on_factory_chosen(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    """Fabrika tanlanganda ishga tushadi. Ro'yxatda yo'q bo'lsa alohida oqimga o'tkaziladi."""
    await callback.answer()
    raw = callback.data.split(":", 1)[1]

    if raw == "none":
        await callback.message.answer(t("factory_not_listed_ask_name", lang))
        await state.set_state(Registration.entering_custom_factory)
        return

    await state.update_data(factory_id=int(raw))
    await callback.message.answer(t("ask_spot", lang))
    await state.set_state(Registration.entering_spot)


@router.message(Registration.entering_custom_factory)
async def on_custom_factory_entered(message: Message, state: FSMContext, user, lang: str) -> None:
    """Fabrika ro'yxatda topilmasa, foydalanuvchi yozgan ma'lumot adminlarga yuboriladi."""
    text = t(
        "factory_request_notify_admin",
        "uz",
        full_name=user.full_name or (message.from_user.full_name if message.from_user else "?"),
        username=user.username or "-",
        text=message.text or "",
    )
    await notify_admins(message.bot, text)

    await message.answer(t("factory_not_listed_sent", lang))
    await state.clear()


@router.message(Registration.entering_spot)
async def on_spot_entered(message: Message, state: FSMContext, session, user, lang: str) -> None:
    """Anketaning oxirgi qadami — ro'yxatdan o'tish shu yerda yakunlanadi."""
    data = await state.get_data()
    await complete_registration(
        session,
        user,
        full_name=data["full_name"],
        phone=data["phone"],
        factory_id=data["factory_id"],
        delivery_note=(message.text or "").strip() or None,
    )
    await session.flush()
    await state.clear()

    log_event(
        "user_signup",
        user.telegram_id,
        user.full_name or (message.from_user.username if message.from_user else "?"),
        f"{user.full_name}, tel: {user.phone}, factory_id: {user.factory_id}",
    )

    await message.answer(t("registration_complete", lang, open_app=t("btn_open_app", lang)))
    await _send_main_menu(message, lang)
