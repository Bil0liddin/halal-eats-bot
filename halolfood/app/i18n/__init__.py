"""Butun tizimdagi barcha foydalanuvchiga ko'rinadigan matnlar shu yerda.

QOIDA: kod ichida (handlerlarda, servislarda) hech qanday matn to'g'ridan-to'g'ri
yozilmaydi — hammasi shu yerdan `t()` orqali olinadi.
"""
from __future__ import annotations

TEXTS: dict[str, dict[str, str]] = {
    # ---- Ro'yxatdan o'tish ----
    "choose_language": {
        "uz": "Tilni tanlang / Выберите язык / Choose language",
        "ru": "Tilni tanlang / Выберите язык / Choose language",
        "en": "Tilni tanlang / Выберите язык / Choose language",
    },
    "welcome": {
        "uz": "🍱 Halol Food botiga xush kelibsiz!\n\nBu bot orqali fabrikangizga haftalik yoki oylik halol tushlik yetkazib berish xizmatiga obuna bo'lasiz.\n\nKeling, ro'yxatdan o'tamiz.",
        "ru": "🍱 Добро пожаловать в Halol Food!\n\nЧерез этого бота вы можете оформить еженедельную или ежемесячную подписку на доставку халяльных обедов на вашу фабрику.\n\nДавайте зарегистрируемся.",
        "en": "🍱 Welcome to Halol Food!\n\nThis bot lets you subscribe to weekly or monthly halal lunch delivery at your factory.\n\nLet's get you registered.",
    },
    "ask_name": {
        "uz": "Ism va familiyangizni to'liq kiriting:",
        "ru": "Введите ваше полное имя:",
        "en": "Please enter your full name:",
    },
    "ask_phone": {
        "uz": "Telefon raqamingizni yuboring (tugma orqali yoki qo'lda yozing):",
        "ru": "Отправьте номер телефона (кнопкой или введите вручную):",
        "en": "Please share your phone number (use the button or type it manually):",
    },
    "share_contact_button": {
        "uz": "📱 Raqamni yuborish",
        "ru": "📱 Отправить номер",
        "en": "📱 Share number",
    },
    "invalid_phone": {
        "uz": "Telefon raqami noto'g'ri. Masalan: 010-1234-5678",
        "ru": "Неверный номер телефона. Пример: 010-1234-5678",
        "en": "Invalid phone number. Example: 010-1234-5678",
    },
    "ask_factory": {
        "uz": "Qaysi fabrikada ishlaysiz?",
        "ru": "На какой фабрике вы работаете?",
        "en": "Which factory do you work at?",
    },
    "factory_not_listed_button": {
        "uz": "📍 Mening fabrikam ro'yxatda yo'q",
        "ru": "📍 Моей фабрики нет в списке",
        "en": "📍 My factory isn't listed",
    },
    "factory_not_listed_ask_name": {
        "uz": "Fabrikangiz nomi va manzilini yozing. Adminlarga yuboramiz:",
        "ru": "Напишите название и адрес вашей фабрики. Отправим администраторам:",
        "en": "Please type your factory's name and address. We'll forward it to the admins:",
    },
    "factory_not_listed_sent": {
        "uz": "Rahmat! So'rovingiz adminlarga yuborildi, tez orada bog'lanishadi.",
        "ru": "Спасибо! Ваш запрос отправлен администраторам, скоро свяжутся.",
        "en": "Thank you! Your request was sent to the admins, they'll contact you soon.",
    },
    "ask_spot": {
        "uz": "Fabrika ichida sizni qayerdan topsak bo'ladi? (masalan: 2-sex, omborxona yonida)",
        "ru": "Где вас найти внутри фабрики? (например: цех №2, у склада)",
        "en": "Where inside the factory can we find you? (e.g. workshop 2, next to the warehouse)",
    },
    "registration_complete": {
        "uz": "✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!\n\nEndi pastdagi \"{open_app}\" tugmasi orqali menyuni ko'rib, obuna tanlashingiz mumkin.",
        "ru": "✅ Регистрация завершена!\n\nТеперь вы можете открыть меню и выбрать подписку через кнопку \"{open_app}\" внизу.",
        "en": "✅ Registration complete!\n\nNow you can view the menu and choose a plan using the \"{open_app}\" button below.",
    },
    # ---- Asosiy menyu ----
    "btn_open_app": {
        "uz": "🍽️ Menyu va obuna",
        "ru": "🍽️ Меню и подписка",
        "en": "🍽️ Menu & subscription",
    },
    "open_app_prompt": {
        "uz": "Reja tanlash va menyuni ko'rish uchun pastdagi tugmani bosing:",
        "ru": "Нажмите кнопку ниже, чтобы выбрать план и посмотреть меню:",
        "en": "Tap the button below to choose a plan and view the menu:",
    },
    "btn_my_subscription": {
        "uz": "📦 Mening obunam",
        "ru": "📦 Моя подписка",
        "en": "📦 My subscription",
    },
    "btn_profile": {
        "uz": "👤 Profil",
        "ru": "👤 Профиль",
        "en": "👤 Profile",
    },
    "btn_help": {
        "uz": "❓ Yordam",
        "ru": "❓ Помощь",
        "en": "❓ Help",
    },
    "help_text": {
        "uz": "Savollar bo'lsa shu botga yozing, admin javob beradi.\n\nBuyruqlar:\n/start — qayta boshlash\n/profile — profilingiz",
        "ru": "Если есть вопросы, напишите в этот бот — админ ответит.\n\nКоманды:\n/start — начать заново\n/profile — ваш профиль",
        "en": "If you have questions, message this bot — an admin will reply.\n\nCommands:\n/start — start over\n/profile — your profile",
    },
    # ---- Obuna ----
    "no_active_subscription": {
        "uz": "Sizda hozircha faol obuna yo'q. \"{open_app}\" tugmasi orqali tanlashingiz mumkin.",
        "ru": "У вас пока нет активной подписки. Выберите через кнопку \"{open_app}\".",
        "en": "You don't have an active subscription yet. Choose one via the \"{open_app}\" button.",
    },
    "subscription_status_heading": {
        "uz": "📦 Sizning obunangiz",
        "ru": "📦 Ваша подписка",
        "en": "📦 Your subscription",
    },
    "meals_left_label": {
        "uz": "Qolgan ovqatlar",
        "ru": "Осталось порций",
        "en": "Meals left",
    },
    "valid_until_label": {
        "uz": "Amal qilish muddati",
        "ru": "Действует до",
        "en": "Valid until",
    },
    "status_active": {"uz": "✅ Faol", "ru": "✅ Активна", "en": "✅ Active"},
    "status_paused": {"uz": "⏸ To'xtatilgan", "ru": "⏸ Приостановлена", "en": "⏸ Paused"},
    "status_expired": {"uz": "⌛ Muddati tugagan", "ru": "⌛ Истекла", "en": "⌛ Expired"},
    "status_cancelled": {"uz": "❌ Bekor qilingan", "ru": "❌ Отменена", "en": "❌ Cancelled"},
    "manage_in_app_hint": {
        "uz": "Kunlik ovqatni o'zgartirish yoki obunani bekor qilish uchun Mini App'ni oching.",
        "ru": "Чтобы изменить блюдо на день или отменить подписку, откройте Mini App.",
        "en": "To change a day's meal or cancel your subscription, open the Mini App.",
    },
    # ---- To'lov / checkout ----
    "checkout_heading": {
        "uz": "🧾 Buyurtmangiz",
        "ru": "🧾 Ваш заказ",
        "en": "🧾 Your order",
    },
    "checkout_instructions_heading": {
        "uz": "💳 To'lov ma'lumotlari",
        "ru": "💳 Данные для оплаты",
        "en": "💳 Payment details",
    },
    "i_paid_button": {
        "uz": "✅ To'ladim",
        "ru": "✅ Я оплатил",
        "en": "✅ I've paid",
    },
    "pay_now_button": {
        "uz": "💳 To'lash",
        "ru": "💳 Оплатить",
        "en": "💳 Pay now",
    },
    "i_paid_notify_admin": {
        "uz": "💰 Yangi to'lov da'vosi!\n\nBuyurtma: {reference}\nMijoz: {full_name} ({phone})\nSumma: {amount} won\n\nTasdiqlash uchun: /ok {reference}",
        "ru": "💰 Новое заявление об оплате!\n\nЗаказ: {reference}\nКлиент: {full_name} ({phone})\nСумма: {amount} вон\n\nДля подтверждения: /ok {reference}",
        "en": "💰 New payment claim!\n\nOrder: {reference}\nCustomer: {full_name} ({phone})\nAmount: {amount} won\n\nTo confirm: /ok {reference}",
    },
    "i_paid_thanks": {
        "uz": "Rahmat! To'lovingiz admin tomonidan tekshirilmoqda, tez orada tasdiqlanadi.",
        "ru": "Спасибо! Ваш платёж проверяется администратором, скоро подтвердим.",
        "en": "Thank you! Your payment is being checked by an admin and will be confirmed soon.",
    },
    "payment_confirmed_notify_user": {
        "uz": "✅ To'lovingiz tasdiqlandi! Obunangiz faollashtirildi.\n\nBoshlanish sanasi: {starts_on}\nTugash sanasi: {ends_on}",
        "ru": "✅ Ваш платёж подтверждён! Подписка активирована.\n\nНачало: {starts_on}\nОкончание: {ends_on}",
        "en": "✅ Your payment is confirmed! Your subscription is now active.\n\nStarts on: {starts_on}\nEnds on: {ends_on}",
    },
    "payment_rejected_notify_user": {
        "uz": "❌ To'lovingiz tasdiqlanmadi. Savollar bo'lsa admin bilan bog'laning.",
        "ru": "❌ Ваш платёж не подтверждён. Если есть вопросы — свяжитесь с админом.",
        "en": "❌ Your payment could not be confirmed. If you have questions, please contact an admin.",
    },
    # ---- Profil ----
    "profile_heading": {"uz": "👤 Sizning profilingiz", "ru": "👤 Ваш профиль", "en": "👤 Your profile"},
    "profile_name": {"uz": "Ism", "ru": "Имя", "en": "Name"},
    "profile_phone": {"uz": "Telefon", "ru": "Телефон", "en": "Phone"},
    "profile_factory": {"uz": "Fabrika", "ru": "Фабрика", "en": "Factory"},
    "profile_lang": {"uz": "Til", "ru": "Язык", "en": "Language"},
    "change_language_button": {
        "uz": "🌐 Tilni o'zgartirish",
        "ru": "🌐 Изменить язык",
        "en": "🌐 Change language",
    },
    "language_changed": {"uz": "Til o'zgartirildi ✅", "ru": "Язык изменён ✅", "en": "Language changed ✅"},
    "edit_profile_button": {"uz": "✏️ Tahrirlash", "ru": "✏️ Редактировать", "en": "✏️ Edit"},
    "back_button": {"uz": "🔙 Orqaga", "ru": "🔙 Назад", "en": "🔙 Back"},
    "edit_field_name": {"uz": "👤 Ismni o'zgartirish", "ru": "👤 Изменить имя", "en": "👤 Change name"},
    "edit_field_phone": {"uz": "📱 Telefonni o'zgartirish", "ru": "📱 Изменить телефон", "en": "📱 Change phone"},
    "edit_field_factory": {"uz": "🏭 Fabrikani o'zgartirish", "ru": "🏭 Изменить фабрику", "en": "🏭 Change factory"},
    "edit_field_spot": {"uz": "📍 Joylashuvni o'zgartirish", "ru": "📍 Изменить местоположение", "en": "📍 Change location"},
    "profile_updated": {
        "uz": "✅ Ma'lumot yangilandi!",
        "ru": "✅ Данные обновлены!",
        "en": "✅ Information updated!",
    },
    # ---- Skip (bitta kunni bekor qilish, endi Mini App orqali) ----
    "skip_too_late": {
        "uz": "Kechikdingiz — bu kunni endi bekor qilib bo'lmaydi (soat {cutoff}:00 dan keyin bekor qilinmaydi).",
        "ru": "Уже поздно — этот день нельзя отменить (после {cutoff}:00 отмена недоступна).",
        "en": "Too late — this day can no longer be cancelled (cancellation closes at {cutoff}:00).",
    },
    # ---- Xatolar ----
    "error_generic": {
        "uz": "Kechirasiz, xatolik yuz berdi. Qayta urinib ko'ring yoki admin bilan bog'laning.",
        "ru": "Извините, произошла ошибка. Попробуйте снова или свяжитесь с админом.",
        "en": "Sorry, something went wrong. Please try again or contact an admin.",
    },
    "error_cart_empty": {
        "uz": "Savatingiz bo'sh. Avval taomlarni tanlang.",
        "ru": "Ваша корзина пуста. Сначала выберите блюда.",
        "en": "Your cart is empty. Please choose meals first.",
    },
    "error_cart_wrong_count": {
        "uz": "Tanlangan kunlar soni ({selected}) rejadagi ovqatlar soniga ({required}) mos kelmayapti.",
        "ru": "Количество выбранных дней ({selected}) не совпадает с числом порций в плане ({required}).",
        "en": "The number of selected days ({selected}) doesn't match the plan's meal count ({required}).",
    },
    "error_item_not_on_menu": {
        "uz": "Tanlangan taom {date} kuni menyuda yo'q. Menyuni yangilab qayta tanlang.",
        "ru": "Выбранное блюдо недоступно в меню на {date}. Обновите меню и выберите снова.",
        "en": "The selected dish isn't on the menu for {date}. Please refresh the menu and choose again.",
    },
    "error_not_registered": {
        "uz": "Avval ro'yxatdan o'ting: /start",
        "ru": "Сначала зарегистрируйтесь: /start",
        "en": "Please register first: /start",
    },
    "error_blocked": {
        "uz": "Sizga botdan foydalanish taqiqlangan.",
        "ru": "Вам запрещено пользоваться ботом.",
        "en": "You are blocked from using this bot.",
    },
    "error_order_already_paid": {
        "uz": "Bu buyurtma allaqachon to'langan.",
        "ru": "Этот заказ уже оплачен.",
        "en": "This order has already been paid.",
    },
    "error_order_not_payable": {
        "uz": "Bu buyurtmani endi to'lab bo'lmaydi (bekor qilingan yoki qaytarilgan).",
        "ru": "Этот заказ больше нельзя оплатить (отменён или возвращён).",
        "en": "This order can no longer be paid (it was cancelled or refunded).",
    },
    # ---- Admin ----
    "admin_only": {"uz": "Bu buyruq faqat adminlar uchun.", "ru": "Эта команда только для админов.", "en": "This command is for admins only."},
    "stats_heading": {"uz": "📊 Statistika", "ru": "📊 Статистика", "en": "📊 Statistics"},
    "kitchen_heading": {"uz": "👨‍🍳 Oshxona rejasi", "ru": "👨‍🍳 План кухни", "en": "👨‍🍳 Kitchen plan"},
    "pending_heading": {"uz": "⏳ To'lov kutayotgan buyurtmalar", "ru": "⏳ Заказы, ожидающие оплаты", "en": "⏳ Orders awaiting payment"},
    "no_pending_orders": {"uz": "To'lov kutayotgan buyurtma yo'q.", "ru": "Нет заказов, ожидающих оплаты.", "en": "No orders awaiting payment."},
    "admin_confirm_button": {"uz": "✅ Tasdiqlash", "ru": "✅ Подтвердить", "en": "✅ Confirm"},
    "admin_reject_button": {"uz": "❌ Rad etish", "ru": "❌ Отклонить", "en": "❌ Reject"},
    "admin_order_confirmed": {"uz": "✅ {reference} tasdiqlandi.", "ru": "✅ {reference} подтверждён.", "en": "✅ {reference} confirmed."},
    "admin_order_rejected": {"uz": "❌ {reference} rad etildi.", "ru": "❌ {reference} отклонён.", "en": "❌ {reference} rejected."},
    "admin_order_not_found": {"uz": "Bunday buyurtma topilmadi.", "ru": "Такой заказ не найден.", "en": "No such order was found."},
    "factory_request_notify_admin": {
        "uz": "📍 Yangi fabrika so'rovi!\n\nMijoz: {full_name} (@{username})\nXabar: {text}",
        "ru": "📍 Новый запрос на фабрику!\n\nКлиент: {full_name} (@{username})\nСообщение: {text}",
        "en": "📍 New factory request!\n\nCustomer: {full_name} (@{username})\nMessage: {text}",
    },
    "renewal_reminder": {
        "uz": "⏰ Obunangiz {days} kundan keyin tugaydi. Yangilash uchun \"{open_app}\" tugmasini bosing.",
        "ru": "⏰ Ваша подписка истекает через {days} дн. Нажмите \"{open_app}\", чтобы продлить.",
        "en": "⏰ Your subscription ends in {days} day(s). Tap \"{open_app}\" to renew.",
    },
    "tomorrow_meal_reminder": {
        "uz": "🍱 Ertaga sizga \"{meal_name}\" yetkaziladi ({factory}, {window}).",
        "ru": "🍱 Завтра вам доставят \"{meal_name}\" ({factory}, {window}).",
        "en": "🍱 Tomorrow you'll get \"{meal_name}\" delivered ({factory}, {window}).",
    },
}

WEEKDAY_NAMES: dict[int, dict[str, str]] = {
    0: {"uz": "Dushanba", "ru": "Понедельник", "en": "Monday"},
    1: {"uz": "Seshanba", "ru": "Вторник", "en": "Tuesday"},
    2: {"uz": "Chorshanba", "ru": "Среда", "en": "Wednesday"},
    3: {"uz": "Payshanba", "ru": "Четверг", "en": "Thursday"},
    4: {"uz": "Juma", "ru": "Пятница", "en": "Friday"},
    5: {"uz": "Shanba", "ru": "Суббота", "en": "Saturday"},
    6: {"uz": "Yakshanba", "ru": "Воскресенье", "en": "Sunday"},
}

DEFAULT_LANG = "uz"


def t(key: str, lang: str, **kwargs) -> str:
    """Berilgan kalit va tilga mos matnni qaytaradi, kerak bo'lsa {placeholder}larni almashtiradi."""
    entry = TEXTS[key]
    template = entry.get(lang, entry[DEFAULT_LANG])
    return template.format(**kwargs) if kwargs else template


def weekday_name(weekday: int, lang: str) -> str:
    """Hafta kuni raqamidan (0=dushanba) nomini qaytaradi."""
    entry = WEEKDAY_NAMES[weekday]
    return entry.get(lang, entry[DEFAULT_LANG])


def money(amount: int) -> str:
    """Pul summasini o'qish qulay formatga o'tkazadi: 89000 -> '89,000'."""
    return f"{amount:,}"
