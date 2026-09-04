from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards import cart_keyboard, pay_now_keyboard
from app.bot.services import (
    cart_total,
    clear_cart,
    create_order_from_cart,
    get_cart_items,
    get_or_create_user,
    remove_from_cart,
)
from app.db import get_session


def _format_cart(items) -> str:
    if not items:
        return "🛒 Your cart is empty."
    lines = [f"{ci.product.name} x{ci.quantity} — {ci.product.price * ci.quantity:,}원" for ci in items]
    lines.append(f"\nTotal: {cart_total(items):,}원")
    return "🛒 Your Cart:\n\n" + "\n".join(lines)


async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    with get_session() as session:
        user = get_or_create_user(session, update.effective_user, update.effective_chat.id)
        items = get_cart_items(session, user)
        text = _format_cart(items)
        keyboard = cart_keyboard(items)

    await query.edit_message_text(text, reply_markup=keyboard)


async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    product_id = int(query.data.split(":")[1])

    with get_session() as session:
        user = get_or_create_user(session, update.effective_user, update.effective_chat.id)
        remove_from_cart(session, user, product_id)
        items = get_cart_items(session, user)
        text = _format_cart(items)
        keyboard = cart_keyboard(items)

    await query.answer()
    await query.edit_message_text(text, reply_markup=keyboard)


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    with get_session() as session:
        user = get_or_create_user(session, update.effective_user, update.effective_chat.id)
        clear_cart(session, user)

    await query.answer("Cart cleared")
    await query.edit_message_text("🛒 Your cart is empty.", reply_markup=cart_keyboard([]))


async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    with get_session() as session:
        user = get_or_create_user(session, update.effective_user, update.effective_chat.id)
        order = create_order_from_cart(session, user)
        if order is None:
            await query.answer("Your cart is empty.")
            return
        toss_order_id = order.toss_order_id
        total_amount = order.total_amount

    await query.answer()
    await query.edit_message_text(
        f"Order created ✅ (#{toss_order_id})\nTotal: {total_amount:,}원\n\nTap below to pay by card via Toss Payments.",
        reply_markup=pay_now_keyboard(toss_order_id),
    )
