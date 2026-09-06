from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards import back_to_menu_keyboard
from app.bot.services import get_or_create_user, list_user_orders
from app.db import get_session
from app.i18n import status_label, t, user_lang


def _format_orders(orders, lang: str) -> str:
    if not orders:
        return t("no_orders_yet", lang)
    lines = []
    for o in orders:
        lines.append(f"#{o.toss_order_id} — {status_label(o.status, lang)} — {o.total_amount:,}원")
    return t("orders_title", lang) + "\n".join(lines)


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with get_session() as session:
        user = get_or_create_user(session, update.effective_user, update.effective_chat.id)
        lang = user_lang(user)
        orders = list_user_orders(session, user)
        text = _format_orders(orders, lang)

    if update.message:
        await update.message.reply_text(text, reply_markup=back_to_menu_keyboard(lang))
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text, reply_markup=back_to_menu_keyboard(lang))
