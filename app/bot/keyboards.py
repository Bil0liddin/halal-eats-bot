from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.config import BASE_URL
from app.i18n import LANGUAGE_NAMES, t
from app.models import CartItem, OrderStatus, Product

LANGUAGE_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(LANGUAGE_NAMES["uz"], callback_data="lang:uz"),
            InlineKeyboardButton(LANGUAGE_NAMES["ko"], callback_data="lang:ko"),
        ],
        [
            InlineKeyboardButton(LANGUAGE_NAMES["en"], callback_data="lang:en"),
            InlineKeyboardButton(LANGUAGE_NAMES["ru"], callback_data="lang:ru"),
        ],
    ]
)


def main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(t("btn_browse", lang), callback_data="browse")],
            [InlineKeyboardButton(t("btn_cart", lang), callback_data="cart")],
            [InlineKeyboardButton(t("btn_orders", lang), callback_data="orders")],
        ]
    )


def back_to_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(t("btn_back_to_menu", lang), callback_data="menu")]])


def browse_keyboard(products: list[Product], lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(f"➕ {p.name} — {p.price:,}원", callback_data=f"add:{p.id}")]
        for p in products
    ]
    rows.append([InlineKeyboardButton(t("btn_view_cart", lang), callback_data="cart")])
    rows.append([InlineKeyboardButton(t("btn_back_to_menu", lang), callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def cart_keyboard(items: list[CartItem], lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(f"➖ {ci.product.name} x{ci.quantity}", callback_data=f"remove:{ci.product_id}")]
        for ci in items
    ]
    if items:
        rows.append([InlineKeyboardButton(t("btn_checkout", lang), callback_data="checkout")])
        rows.append([InlineKeyboardButton(t("btn_clear_cart", lang), callback_data="clear")])
    rows.append([InlineKeyboardButton(t("btn_keep_browsing", lang), callback_data="browse")])
    rows.append([InlineKeyboardButton(t("btn_back_to_menu", lang), callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def pay_now_keyboard(toss_order_id: str, lang: str) -> InlineKeyboardMarkup:
    url = f"{BASE_URL}/checkout/{toss_order_id}"
    return InlineKeyboardMarkup([[InlineKeyboardButton(t("btn_pay_now", lang), url=url)]])


NEXT_STATUS = {
    OrderStatus.PAID: OrderStatus.PREPARING,
    OrderStatus.PREPARING: OrderStatus.READY,
    OrderStatus.READY: OrderStatus.COMPLETED,
}


def admin_order_keyboard(order_id: int, status: str) -> InlineKeyboardMarkup:
    rows = []
    next_status = NEXT_STATUS.get(status)
    if next_status:
        rows.append(
            [
                InlineKeyboardButton(
                    f"➡️ {t(f'status_{next_status}', 'uz')} deb belgilash",
                    callback_data=f"admin:advance:{order_id}",
                )
            ]
        )
    return InlineKeyboardMarkup(rows) if rows else None
