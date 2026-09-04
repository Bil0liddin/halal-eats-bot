from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards import BACK_TO_MENU, STATUS_LABEL
from app.bot.services import get_or_create_user, list_user_orders
from app.db import get_session


def _format_orders(orders) -> str:
    if not orders:
        return "📋 You haven't placed any orders yet."
    lines = []
    for o in orders:
        lines.append(f"#{o.toss_order_id} — {STATUS_LABEL.get(o.status, o.status)} — {o.total_amount:,}원")
    return "📋 Your Orders:\n\n" + "\n".join(lines)


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with get_session() as session:
        user = get_or_create_user(session, update.effective_user, update.effective_chat.id)
        orders = list_user_orders(session, user)
        text = _format_orders(orders)

    if update.message:
        await update.message.reply_text(text, reply_markup=BACK_TO_MENU)
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text, reply_markup=BACK_TO_MENU)
