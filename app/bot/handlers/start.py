from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards import MAIN_MENU
from app.bot.services import get_or_create_user
from app.db import get_session

WELCOME = (
    "🕌 Welcome to Halal Eats Korea!\n\n"
    "Order halal food straight from Telegram and pay securely by card.\n"
    "What would you like to do?"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with get_session() as session:
        get_or_create_user(session, update.effective_user, update.effective_chat.id)

    await update.message.reply_text(WELCOME, reply_markup=MAIN_MENU)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("What would you like to do?", reply_markup=MAIN_MENU)
