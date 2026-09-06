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
from app.i18n import t, user_lang


def _format_cart(items, lang: str) -> str:
    if not items:
        return t("cart_empty", lang)
    lines = [f"{ci.product.name} x{ci.quantity} — {ci.product.price * ci.quantity:,}원" for ci in items]
    lines.append(f"{t('cart_total_line', lang)}{cart_total(items):,}원")
    return t("cart_title", lang) + "\n".join(lines)


async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    with get_session() as session:
        user = get_or_create_user(session, update.effective_user, update.effective_chat.id)
        lang = user_lang(user)
        items = get_cart_items(session, user)
        text = _format_cart(items, lang)
        keyboard = cart_keyboard(items, lang)

    await query.edit_message_text(text, reply_markup=keyboard)


async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    product_id = int(query.data.split(":")[1])

    with get_session() as session:
        user = get_or_create_user(session, update.effective_user, update.effective_chat.id)
        lang = user_lang(user)
        remove_from_cart(session, user, product_id)
        items = get_cart_items(session, user)
        text = _format_cart(items, lang)
        keyboard = cart_keyboard(items, lang)

    await query.answer()
    await query.edit_message_text(text, reply_markup=keyboard)


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    with get_session() as session:
        user = get_or_create_user(session, update.effective_user, update.effective_chat.id)
        lang = user_lang(user)
        clear_cart(session, user)

    await query.answer(t("cart_cleared", lang))
    await query.edit_message_text(t("cart_empty", lang), reply_markup=cart_keyboard([], lang))


async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    with get_session() as session:
        user = get_or_create_user(session, update.effective_user, update.effective_chat.id)
        lang = user_lang(user)
        order = create_order_from_cart(session, user)
        if order is None:
            await query.answer(t("cart_empty", lang))
            return
        toss_order_id = order.toss_order_id
        total_amount = order.total_amount

    await query.answer()
    await query.edit_message_text(
        t("order_created", lang, order_id=toss_order_id, amount=f"{total_amount:,}"),
        reply_markup=pay_now_keyboard(toss_order_id, lang),
    )
