import logging

from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from app.bot.handlers import admin, cart, orders, start
from app.config import BOT_TOKEN
from app.db import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")


def build_application() -> Application:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start.start))
    application.add_handler(CommandHandler("orders", orders.my_orders))
    application.add_handler(CommandHandler("adminorders", admin.admin_orders))
    application.add_handler(CommandHandler("addproduct", admin.add_product))

    application.add_handler(CallbackQueryHandler(start.set_language, pattern=r"^lang:(uz|ko|en|ru)$"))
    application.add_handler(CallbackQueryHandler(start.show_main_menu, pattern="^menu$"))
    application.add_handler(CallbackQueryHandler(cart.view_cart, pattern="^cart$"))
    application.add_handler(CallbackQueryHandler(cart.remove_item, pattern=r"^remove:\d+$"))
    application.add_handler(CallbackQueryHandler(cart.clear, pattern="^clear$"))
    application.add_handler(CallbackQueryHandler(cart.checkout, pattern="^checkout$"))
    application.add_handler(CallbackQueryHandler(orders.my_orders, pattern="^orders$"))
    application.add_handler(CallbackQueryHandler(admin.advance_status, pattern=r"^admin:advance:\d+$"))

    return application


def main() -> None:
    init_db()
    application = build_application()
    application.run_polling()


if __name__ == "__main__":
    main()
