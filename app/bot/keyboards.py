from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.config import BASE_URL
from app.models import CartItem, OrderStatus, Product

MAIN_MENU = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🍽️ Browse Menu", callback_data="browse")],
        [InlineKeyboardButton("🛒 Cart", callback_data="cart")],
        [InlineKeyboardButton("📋 My Orders", callback_data="orders")],
    ]
)

BACK_TO_MENU = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]])


def browse_keyboard(products: list[Product]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(f"➕ {p.name} — {p.price:,}원", callback_data=f"add:{p.id}")]
        for p in products
    ]
    rows.append([InlineKeyboardButton("🛒 View Cart", callback_data="cart")])
    rows.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def cart_keyboard(items: list[CartItem]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(f"➖ {ci.product.name} x{ci.quantity}", callback_data=f"remove:{ci.product_id}")]
        for ci in items
    ]
    if items:
        rows.append([InlineKeyboardButton("✅ Checkout", callback_data="checkout")])
        rows.append([InlineKeyboardButton("🧹 Clear Cart", callback_data="clear")])
    rows.append([InlineKeyboardButton("🍽️ Keep Browsing", callback_data="browse")])
    rows.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def pay_now_keyboard(toss_order_id: str) -> InlineKeyboardMarkup:
    url = f"{BASE_URL}/checkout/{toss_order_id}"
    return InlineKeyboardMarkup([[InlineKeyboardButton("💳 Pay Now", url=url)]])


NEXT_STATUS = {
    OrderStatus.PAID: OrderStatus.PREPARING,
    OrderStatus.PREPARING: OrderStatus.READY,
    OrderStatus.READY: OrderStatus.COMPLETED,
}

STATUS_LABEL = {
    OrderStatus.PENDING_PAYMENT: "⏳ Awaiting payment",
    OrderStatus.PAID: "💰 Paid",
    OrderStatus.PREPARING: "👨‍🍳 Preparing",
    OrderStatus.READY: "✅ Ready for pickup",
    OrderStatus.COMPLETED: "🏁 Completed",
    OrderStatus.CANCELLED: "❌ Cancelled",
}


def admin_order_keyboard(order_id: int, status: str) -> InlineKeyboardMarkup:
    rows = []
    next_status = NEXT_STATUS.get(status)
    if next_status:
        rows.append(
            [InlineKeyboardButton(f"➡️ Mark as {STATUS_LABEL[next_status]}", callback_data=f"admin:advance:{order_id}")]
        )
    return InlineKeyboardMarkup(rows) if rows else None
