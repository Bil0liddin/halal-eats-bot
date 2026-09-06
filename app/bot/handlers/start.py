from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards import LANGUAGE_KEYBOARD, main_menu_keyboard
from app.bot.services import get_or_create_user
from app.db import get_session
from app.i18n import CHOOSE_LANGUAGE_PROMPT, t, user_lang


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with get_session() as session:
        get_or_create_user(session, update.effective_user, update.effective_chat.id)

    await update.message.reply_text(CHOOSE_LANGUAGE_PROMPT, reply_markup=LANGUAGE_KEYBOARD)


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    lang = query.data.split(":")[1]

    with get_session() as session:
        user = get_or_create_user(session, update.effective_user, update.effective_chat.id)
        user.language = lang

    await query.edit_message_text(t("welcome", lang), reply_markup=main_menu_keyboard(lang))


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    with get_session() as session:
        user = get_or_create_user(session, update.effective_user, update.effective_chat.id)
        lang = user_lang(user)

    await query.edit_message_text(t("menu_prompt", lang), reply_markup=main_menu_keyboard(lang))
