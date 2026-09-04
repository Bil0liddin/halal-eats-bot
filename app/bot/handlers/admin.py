from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards import NEXT_STATUS, STATUS_LABEL, admin_order_keyboard
from app.config import ADMIN_TELEGRAM_IDS
from app.db import get_session
from app.models import Order, OrderStatus, Product


def _is_admin(update: Update) -> bool:
    return update.effective_user.id in ADMIN_TELEGRAM_IDS


async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        await update.message.reply_text("You're not authorized to use this command.")
        return

    with get_session() as session:
        orders = (
            session.query(Order)
            .filter(Order.status.in_((OrderStatus.PAID, OrderStatus.PREPARING, OrderStatus.READY)))
            .order_by(Order.created_at.asc())
            .all()
        )
        if not orders:
            await update.message.reply_text("No active orders right now.")
            return

        for o in orders:
            items_text = "\n".join(f"  - {i.product_name} x{i.quantity}" for i in o.items)
            text = (
                f"#{o.toss_order_id} — {STATUS_LABEL.get(o.status, o.status)}\n"
                f"Buyer: {o.user.display_name}\n"
                f"{items_text}\n"
                f"Total: {o.total_amount:,}원"
            )
            await update.message.reply_text(text, reply_markup=admin_order_keyboard(o.id, o.status))


async def advance_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not _is_admin(update):
        await query.answer("Not authorized", show_alert=True)
        return

    order_id = int(query.data.split(":")[2])

    with get_session() as session:
        order = session.query(Order).filter_by(id=order_id).first()
        if order is None:
            await query.answer("Order not found", show_alert=True)
            return
        next_status = NEXT_STATUS.get(order.status)
        if next_status is None:
            await query.answer("No further status to advance to.")
            return
        order.status = next_status
        new_status = next_status
        buyer_chat_id = order.user.chat_id
        toss_order_id = order.toss_order_id

    await query.answer(f"Marked as {STATUS_LABEL[new_status]}")
    await query.edit_message_reply_markup(reply_markup=admin_order_keyboard(order_id, new_status))
    await context.bot.send_message(
        chat_id=buyer_chat_id,
        text=f"Order #{toss_order_id} update: {STATUS_LABEL[new_status]}",
    )


async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        await update.message.reply_text("You're not authorized to use this command.")
        return

    raw = update.message.text.partition(" ")[2]
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) < 2:
        await update.message.reply_text(
            "Usage: /addproduct Name|Price|Description\n"
            "Example: /addproduct Chicken Biryani|12000|Spicy halal chicken biryani"
        )
        return

    name = parts[0]
    try:
        price = int(parts[1])
    except ValueError:
        await update.message.reply_text("Price must be a whole number in KRW, e.g. 12000")
        return
    description = parts[2] if len(parts) > 2 else ""

    with get_session() as session:
        session.add(Product(name=name, price=price, description=description))

    await update.message.reply_text(f"Added product: {name} — {price:,}원")
