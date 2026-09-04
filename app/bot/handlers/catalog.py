from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards import browse_keyboard
from app.bot.services import add_to_cart, get_or_create_user, list_active_products
from app.db import get_session


async def browse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    with get_session() as session:
        products = list_active_products(session)

    if not products:
        await query.edit_message_text("No items on the menu yet — check back soon!")
        return

    await query.edit_message_text("🍽️ Menu — tap an item to add it to your cart:", reply_markup=browse_keyboard(products))


async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    product_id = int(query.data.split(":")[1])

    with get_session() as session:
        user = get_or_create_user(session, update.effective_user, update.effective_chat.id)
        add_to_cart(session, user, product_id)

    await query.answer("Added to cart ✅")
