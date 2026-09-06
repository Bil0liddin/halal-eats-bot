DEFAULT_LANG = "uz"
LANGUAGES = ("uz", "ko", "en", "ru")

LANGUAGE_NAMES = {
    "uz": "🇺🇿 O'zbekcha",
    "ko": "🇰🇷 한국어",
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
}

CHOOSE_LANGUAGE_PROMPT = (
    "🕌 Halal Eats Korea\n\n"
    "Tilni tanlang / 언어를 선택하세요 / Please choose your language / Пожалуйста, выберите язык"
)

TEXT = {
    "welcome": {
        "uz": "🕌 Halal Eats Korea botiga xush kelibsiz!\n\n"
        "Telegram orqali halal taomga buyurtma bering va xavfsiz tarzda karta bilan to'lang.\n"
        "Nima qilishni xohlaysiz?",
        "ko": "🕌 Halal Eats Korea 봇에 오신 것을 환영합니다!\n\n"
        "텔레그램에서 할랄 음식을 주문하고 카드로 안전하게 결제하실 수 있습니다.\n"
        "무엇을 하시겠습니까?",
        "en": "🕌 Welcome to Halal Eats Korea!\n\n"
        "Order halal food straight from Telegram and pay securely by card.\n"
        "What would you like to do?",
        "ru": "🕌 Добро пожаловать в Halal Eats Korea!\n\n"
        "Заказывайте халяльную еду прямо в Telegram и оплачивайте картой безопасно.\n"
        "Что вы хотели бы сделать?",
    },
    "menu_prompt": {
        "uz": "Nima qilishni xohlaysiz?",
        "ko": "무엇을 하시겠습니까?",
        "en": "What would you like to do?",
        "ru": "Что вы хотели бы сделать?",
    },
    "btn_browse": {
        "uz": "🍽️ Menyuni ko'rish",
        "ko": "🍽️ 메뉴 보기",
        "en": "🍽️ Browse Menu",
        "ru": "🍽️ Посмотреть меню",
    },
    "btn_cart": {
        "uz": "🛒 Savat",
        "ko": "🛒 장바구니",
        "en": "🛒 Cart",
        "ru": "🛒 Корзина",
    },
    "btn_orders": {
        "uz": "📋 Buyurtmalarim",
        "ko": "📋 내 주문",
        "en": "📋 My Orders",
        "ru": "📋 Мои заказы",
    },
    "btn_back_to_menu": {
        "uz": "🔙 Menyuga qaytish",
        "ko": "🔙 메뉴로 돌아가기",
        "en": "🔙 Back to Menu",
        "ru": "🔙 Назад в меню",
    },
    "btn_view_cart": {
        "uz": "🛒 Savatni ko'rish",
        "ko": "🛒 장바구니 보기",
        "en": "🛒 View Cart",
        "ru": "🛒 Посмотреть корзину",
    },
    "btn_keep_browsing": {
        "uz": "🍽️ Davom etish",
        "ko": "🍽️ 계속 둘러보기",
        "en": "🍽️ Keep Browsing",
        "ru": "🍽️ Продолжить покупки",
    },
    "btn_checkout": {
        "uz": "✅ Buyurtma berish",
        "ko": "✅ 주문하기",
        "en": "✅ Checkout",
        "ru": "✅ Оформить заказ",
    },
    "btn_clear_cart": {
        "uz": "🧹 Savatni tozalash",
        "ko": "🧹 장바구니 비우기",
        "en": "🧹 Clear Cart",
        "ru": "🧹 Очистить корзину",
    },
    "btn_pay_now": {
        "uz": "💳 To'lash",
        "ko": "💳 결제하기",
        "en": "💳 Pay Now",
        "ru": "💳 Оплатить",
    },
    "no_items": {
        "uz": "Hozircha menyuda mahsulot yo'q — birozdan keyin qayta urinib ko'ring!",
        "ko": "아직 메뉴에 상품이 없습니다. 잠시 후 다시 확인해 주세요!",
        "en": "No items on the menu yet — check back soon!",
        "ru": "Пока в меню нет блюд — загляните чуть позже!",
    },
    "browse_prompt": {
        "uz": "🍽️ Menyu — savatga qo'shish uchun mahsulotni tanlang:",
        "ko": "🍽️ 메뉴 — 장바구니에 담을 상품을 선택하세요:",
        "en": "🍽️ Menu — tap an item to add it to your cart:",
        "ru": "🍽️ Меню — выберите блюдо, чтобы добавить в корзину:",
    },
    "added_to_cart": {
        "uz": "Savatga qo'shildi ✅",
        "ko": "장바구니에 담았습니다 ✅",
        "en": "Added to cart ✅",
        "ru": "Добавлено в корзину ✅",
    },
    "cart_empty": {
        "uz": "🛒 Savatingiz bo'sh.",
        "ko": "🛒 장바구니가 비어 있습니다.",
        "en": "🛒 Your cart is empty.",
        "ru": "🛒 Ваша корзина пуста.",
    },
    "cart_title": {
        "uz": "🛒 Savatingiz:\n\n",
        "ko": "🛒 장바구니:\n\n",
        "en": "🛒 Your Cart:\n\n",
        "ru": "🛒 Ваша корзина:\n\n",
    },
    "cart_total_line": {
        "uz": "\nJami: ",
        "ko": "\n합계: ",
        "en": "\nTotal: ",
        "ru": "\nИтого: ",
    },
    "cart_cleared": {
        "uz": "Savat tozalandi",
        "ko": "장바구니를 비웠습니다",
        "en": "Cart cleared",
        "ru": "Корзина очищена",
    },
    "order_created": {
        "uz": "Buyurtma yaratildi ✅ (#{order_id})\nJami: {amount}원\n\n"
        "Toss Payments orqali karta bilan to'lash uchun quyidagi tugmani bosing.",
        "ko": "주문이 생성되었습니다 ✅ (#{order_id})\n합계: {amount}원\n\n"
        "아래 버튼을 눌러 Toss Payments로 카드 결제를 진행해 주세요.",
        "en": "Order created ✅ (#{order_id})\nTotal: {amount}원\n\n"
        "Tap below to pay by card via Toss Payments.",
        "ru": "Заказ создан ✅ (#{order_id})\nИтого: {amount}원\n\n"
        "Нажмите кнопку ниже, чтобы оплатить картой через Toss Payments.",
    },
    "no_orders_yet": {
        "uz": "📋 Siz hali birorta ham buyurtma bermagansiz.",
        "ko": "📋 아직 주문 내역이 없습니다.",
        "en": "📋 You haven't placed any orders yet.",
        "ru": "📋 У вас пока нет заказов.",
    },
    "orders_title": {
        "uz": "📋 Buyurtmalaringiz:\n\n",
        "ko": "📋 주문 내역:\n\n",
        "en": "📋 Your Orders:\n\n",
        "ru": "📋 Ваши заказы:\n\n",
    },
    "status_pending_payment": {
        "uz": "⏳ To'lov kutilmoqda",
        "ko": "⏳ 결제 대기 중",
        "en": "⏳ Awaiting payment",
        "ru": "⏳ Ожидает оплаты",
    },
    "status_paid": {
        "uz": "💰 To'landi",
        "ko": "💰 결제 완료",
        "en": "💰 Paid",
        "ru": "💰 Оплачено",
    },
    "status_preparing": {
        "uz": "👨‍🍳 Tayyorlanmoqda",
        "ko": "👨‍🍳 준비 중",
        "en": "👨‍🍳 Preparing",
        "ru": "👨‍🍳 Готовится",
    },
    "status_ready": {
        "uz": "✅ Olib ketishga tayyor",
        "ko": "✅ 픽업 준비 완료",
        "en": "✅ Ready for pickup",
        "ru": "✅ Готово к выдаче",
    },
    "status_completed": {
        "uz": "🏁 Yakunlandi",
        "ko": "🏁 완료",
        "en": "🏁 Completed",
        "ru": "🏁 Завершён",
    },
    "status_cancelled": {
        "uz": "❌ Bekor qilindi",
        "ko": "❌ 취소됨",
        "en": "❌ Cancelled",
        "ru": "❌ Отменён",
    },
    "payment_confirmed_notify": {
        "uz": "✅ #{order_id}-buyurtma uchun to'lov tasdiqlandi. Buyurtmangiz tayyorlanmoqda!",
        "ko": "✅ 주문 #{order_id}의 결제가 확인되었습니다. 조리를 시작합니다!",
        "en": "✅ Payment confirmed for order #{order_id}. Your order is now being prepared!",
        "ru": "✅ Оплата заказа #{order_id} подтверждена. Ваш заказ готовится!",
    },
    "order_status_update_notify": {
        "uz": "#{order_id}-buyurtma yangilandi: {status}",
        "ko": "주문 #{order_id} 상태 업데이트: {status}",
        "en": "Order #{order_id} update: {status}",
        "ru": "Обновление заказа #{order_id}: {status}",
    },
    "checkout_title": {
        "uz": "To'lov - {order_id}",
        "ko": "결제 - {order_id}",
        "en": "Checkout - {order_id}",
        "ru": "Оплата - {order_id}",
    },
    "checkout_heading": {
        "uz": "Halal taom buyurtmasi",
        "ko": "할랄 음식 주문",
        "en": "Halal Food Order",
        "ru": "Заказ халяльной еды",
    },
    "pay_with_card": {
        "uz": "Karta orqali to'lash",
        "ko": "카드로 결제하기",
        "en": "Pay with card",
        "ru": "Оплатить картой",
    },
    "order_already_status": {
        "uz": "Bu buyurtma allaqachon {status} holatida.",
        "ko": "이 주문은 이미 {status} 상태입니다.",
        "en": "This order is already {status}.",
        "ru": "Этот заказ уже в статусе «{status}».",
    },
    "payment_success_page": {
        "uz": "To'lov muvaffaqiyatli yakunlandi! Telegramga qaytishingiz mumkin.",
        "ko": "결제가 완료되었습니다! 텔레그램으로 돌아가셔도 됩니다.",
        "en": "Payment complete! You can return to Telegram.",
        "ru": "Оплата прошла успешно! Вы можете вернуться в Telegram.",
    },
    "payment_failed_page": {
        "uz": "To'lov amalga oshmadi: {message}",
        "ko": "결제 실패: {message}",
        "en": "Payment failed: {message}",
        "ru": "Оплата не прошла: {message}",
    },
    "payment_failed_retry_hint": {
        "uz": "Botdan qayta urinib ko'rishingiz mumkin.",
        "ko": "봇에서 다시 시도할 수 있습니다.",
        "en": "You can try again from the bot.",
        "ru": "Вы можете попробовать снова через бота.",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    entry = TEXT[key]
    template = entry.get(lang, entry[DEFAULT_LANG])
    return template.format(**kwargs) if kwargs else template


def status_label(status: str, lang: str) -> str:
    return t(f"status_{status}", lang)


def user_lang(user) -> str:
    return getattr(user, "language", None) or DEFAULT_LANG
