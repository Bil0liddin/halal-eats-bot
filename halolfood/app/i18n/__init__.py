"""Butun tizimdagi barcha foydalanuvchiga ko'rinadigan matnlar shu yerda.

QOIDA: kod ichida (handlerlarda, servislarda) hech qanday matn to'g'ridan-to'g'ri
yozilmaydi — hammasi shu yerdan `t()` orqali olinadi.
"""
from __future__ import annotations

TEXTS: dict[str, dict[str, str]] = {
    # ---- Ro'yxatdan o'tish ----
    "choose_language": {
        "uz": "Tilni tanlang / Выберите язык / 언어를 선택하세요",
        "ru": "Tilni tanlang / Выберите язык / 언어를 선택하세요",
        "ko": "Tilni tanlang / Выберите язык / 언어를 선택하세요",
    },
    "welcome": {
        "uz": "🍱 Halol Food botiga xush kelibsiz!\n\nBu bot orqali fabrikangizga haftalik yoki oylik halol tushlik yetkazib berish xizmatiga obuna bo'lasiz.\n\nKeling, ro'yxatdan o'tamiz.",
        "ru": "🍱 Добро пожаловать в Halol Food!\n\nЧерез этого бота вы можете оформить еженедельную или ежемесячную подписку на доставку халяльных обедов на вашу фабрику.\n\nДавайте зарегистрируемся.",
        "ko": "🍱 Halol Food 봇에 오신 것을 환영합니다!\n\n이 봇을 통해 공장으로 배달되는 할랄 점심 주간/월간 구독을 신청할 수 있습니다.\n\n등록을 시작하겠습니다.",
    },
    "ask_name": {
        "uz": "Ism va familiyangizni to'liq kiriting:",
        "ru": "Введите ваше полное имя:",
        "ko": "성함을 입력해 주세요:",
    },
    "ask_phone": {
        "uz": "Telefon raqamingizni yuboring (tugma orqali yoki qo'lda yozing):",
        "ru": "Отправьте номер телефона (кнопкой или введите вручную):",
        "ko": "전화번호를 보내주세요 (버튼을 누르거나 직접 입력하세요):",
    },
    "share_contact_button": {
        "uz": "📱 Raqamni yuborish",
        "ru": "📱 Отправить номер",
        "ko": "📱 번호 보내기",
    },
    "invalid_phone": {
        "uz": "Telefon raqami noto'g'ri. Masalan: 010-1234-5678",
        "ru": "Неверный номер телефона. Пример: 010-1234-5678",
        "ko": "전화번호가 올바르지 않습니다. 예: 010-1234-5678",
    },
    "ask_factory": {
        "uz": "Qaysi fabrikada ishlaysiz?",
        "ru": "На какой фабрике вы работаете?",
        "ko": "어느 공장에서 근무하십니까?",
    },
    "factory_not_listed_button": {
        "uz": "📍 Mening fabrikam ro'yxatda yo'q",
        "ru": "📍 Моей фабрики нет в списке",
        "ko": "📍 제 공장이 목록에 없어요",
    },
    "factory_not_listed_ask_name": {
        "uz": "Fabrikangiz nomi va manzilini yozing. Adminlarga yuboramiz:",
        "ru": "Напишите название и адрес вашей фабрики. Отправим администраторам:",
        "ko": "공장 이름과 주소를 입력해 주세요. 관리자에게 전달하겠습니다:",
    },
    "factory_not_listed_sent": {
        "uz": "Rahmat! So'rovingiz adminlarga yuborildi, tez orada bog'lanishadi.",
        "ru": "Спасибо! Ваш запрос отправлен администраторам, скоро свяжутся.",
        "ko": "감사합니다! 요청이 관리자에게 전달되었습니다. 곧 연락드리겠습니다.",
    },
    "ask_spot": {
        "uz": "Fabrika ichida sizni qayerdan topsak bo'ladi? (masalan: 2-sex, omborxona yonida)",
        "ru": "Где вас найти внутри фабрики? (например: цех №2, у склада)",
        "ko": "공장 내 정확한 위치를 알려주세요 (예: 2공장 창고 옆)",
    },
    "registration_complete": {
        "uz": "✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!\n\nEndi pastdagi \"{open_app}\" tugmasi orqali menyuni ko'rib, obuna tanlashingiz mumkin.",
        "ru": "✅ Регистрация завершена!\n\nТеперь вы можете открыть меню и выбрать подписку через кнопку \"{open_app}\" внизу.",
        "ko": "✅ 등록이 완료되었습니다!\n\n이제 아래 \"{open_app}\" 버튼을 눌러 메뉴를 보고 구독을 선택할 수 있습니다.",
    },
    # ---- Asosiy menyu ----
    "btn_open_app": {
        "uz": "🍽️ Menyu va obuna",
        "ru": "🍽️ Меню и подписка",
        "ko": "🍽️ 메뉴 및 구독",
    },
    "open_app_prompt": {
        "uz": "Reja tanlash va menyuni ko'rish uchun pastdagi tugmani bosing:",
        "ru": "Нажмите кнопку ниже, чтобы выбрать план и посмотреть меню:",
        "ko": "아래 버튼을 눌러 플랜을 선택하고 메뉴를 확인하세요:",
    },
    "btn_my_subscription": {
        "uz": "📦 Mening obunam",
        "ru": "📦 Моя подписка",
        "ko": "📦 내 구독",
    },
    "btn_schedule": {
        "uz": "📅 Yetkazib berish jadvali",
        "ru": "📅 График доставки",
        "ko": "📅 배달 일정",
    },
    "btn_profile": {
        "uz": "👤 Profil",
        "ru": "👤 Профиль",
        "ko": "👤 프로필",
    },
    "btn_help": {
        "uz": "❓ Yordam",
        "ru": "❓ Помощь",
        "ko": "❓ 도움말",
    },
    "help_text": {
        "uz": "Savollar bo'lsa shu botga yozing, admin javob beradi.\n\nBuyruqlar:\n/start — qayta boshlash\n/profile — profilingiz",
        "ru": "Если есть вопросы, напишите в этот бот — админ ответит.\n\nКоманды:\n/start — начать заново\n/profile — ваш профиль",
        "ko": "질문이 있으면 이 봇으로 문의해 주세요. 관리자가 답변드립니다.\n\n명령어:\n/start — 다시 시작\n/profile — 내 프로필",
    },
    # ---- Obuna ----
    "no_active_subscription": {
        "uz": "Sizda hozircha faol obuna yo'q. \"{open_app}\" tugmasi orqali tanlashingiz mumkin.",
        "ru": "У вас пока нет активной подписки. Выберите через кнопку \"{open_app}\".",
        "ko": "현재 활성화된 구독이 없습니다. \"{open_app}\" 버튼으로 선택해 주세요.",
    },
    "subscription_status_heading": {
        "uz": "📦 Sizning obunangiz",
        "ru": "📦 Ваша подписка",
        "ko": "📦 내 구독 정보",
    },
    "meals_left_label": {
        "uz": "Qolgan ovqatlar",
        "ru": "Осталось порций",
        "ko": "남은 식사",
    },
    "valid_until_label": {
        "uz": "Amal qilish muddati",
        "ru": "Действует до",
        "ko": "유효 기간",
    },
    "status_active": {"uz": "✅ Faol", "ru": "✅ Активна", "ko": "✅ 활성"},
    "status_paused": {"uz": "⏸ To'xtatilgan", "ru": "⏸ Приостановлена", "ko": "⏸ 일시중지"},
    "status_expired": {"uz": "⌛ Muddati tugagan", "ru": "⌛ Истекла", "ko": "⌛ 만료됨"},
    "status_cancelled": {"uz": "❌ Bekor qilingan", "ru": "❌ Отменена", "ko": "❌ 취소됨"},
    # ---- To'lov / checkout ----
    "checkout_heading": {
        "uz": "🧾 Buyurtmangiz",
        "ru": "🧾 Ваш заказ",
        "ko": "🧾 주문 내역",
    },
    "checkout_instructions_heading": {
        "uz": "💳 To'lov ma'lumotlari",
        "ru": "💳 Данные для оплаты",
        "ko": "💳 결제 정보",
    },
    "i_paid_button": {
        "uz": "✅ To'ladim",
        "ru": "✅ Я оплатил",
        "ko": "✅ 결제했어요",
    },
    "pay_now_button": {
        "uz": "💳 To'lash",
        "ru": "💳 Оплатить",
        "ko": "💳 결제하기",
    },
    "i_paid_notify_admin": {
        "uz": "💰 Yangi to'lov da'vosi!\n\nBuyurtma: {reference}\nMijoz: {full_name} ({phone})\nSumma: {amount} won\n\nTasdiqlash uchun: /ok {reference}",
        "ru": "💰 Новое заявление об оплате!\n\nЗаказ: {reference}\nКлиент: {full_name} ({phone})\nСумма: {amount} вон\n\nДля подтверждения: /ok {reference}",
        "ko": "💰 새 결제 확인 요청!\n\n주문: {reference}\n고객: {full_name} ({phone})\n금액: {amount}원\n\n승인하려면: /ok {reference}",
    },
    "i_paid_thanks": {
        "uz": "Rahmat! To'lovingiz admin tomonidan tekshirilmoqda, tez orada tasdiqlanadi.",
        "ru": "Спасибо! Ваш платёж проверяется администратором, скоро подтвердим.",
        "ko": "감사합니다! 관리자가 결제를 확인하는 중입니다. 곧 승인됩니다.",
    },
    "payment_confirmed_notify_user": {
        "uz": "✅ To'lovingiz tasdiqlandi! Obunangiz faollashtirildi.\n\nBoshlanish sanasi: {starts_on}\nTugash sanasi: {ends_on}",
        "ru": "✅ Ваш платёж подтверждён! Подписка активирована.\n\nНачало: {starts_on}\nОкончание: {ends_on}",
        "ko": "✅ 결제가 승인되었습니다! 구독이 활성화되었습니다.\n\n시작일: {starts_on}\n종료일: {ends_on}",
    },
    "payment_rejected_notify_user": {
        "uz": "❌ To'lovingiz tasdiqlanmadi. Savollar bo'lsa admin bilan bog'laning.",
        "ru": "❌ Ваш платёж не подтверждён. Если есть вопросы — свяжитесь с админом.",
        "ko": "❌ 결제가 승인되지 않았습니다. 문의사항은 관리자에게 연락해 주세요.",
    },
    # ---- Profil ----
    "profile_heading": {"uz": "👤 Sizning profilingiz", "ru": "👤 Ваш профиль", "ko": "👤 내 프로필"},
    "profile_name": {"uz": "Ism", "ru": "Имя", "ko": "이름"},
    "profile_phone": {"uz": "Telefon", "ru": "Телефон", "ko": "전화번호"},
    "profile_factory": {"uz": "Fabrika", "ru": "Фабрика", "ko": "공장"},
    "profile_lang": {"uz": "Til", "ru": "Язык", "ko": "언어"},
    "change_language_button": {
        "uz": "🌐 Tilni o'zgartirish",
        "ru": "🌐 Изменить язык",
        "ko": "🌐 언어 변경",
    },
    "language_changed": {"uz": "Til o'zgartirildi ✅", "ru": "Язык изменён ✅", "ko": "언어가 변경되었습니다 ✅"},
    "edit_profile_button": {"uz": "✏️ Tahrirlash", "ru": "✏️ Редактировать", "ko": "✏️ 수정"},
    "back_button": {"uz": "🔙 Orqaga", "ru": "🔙 Назад", "ko": "🔙 뒤로"},
    "edit_field_name": {"uz": "👤 Ismni o'zgartirish", "ru": "👤 Изменить имя", "ko": "👤 이름 변경"},
    "edit_field_phone": {"uz": "📱 Telefonni o'zgartirish", "ru": "📱 Изменить телефон", "ko": "📱 전화번호 변경"},
    "edit_field_factory": {"uz": "🏭 Fabrikani o'zgartirish", "ru": "🏭 Изменить фабрику", "ko": "🏭 공장 변경"},
    "edit_field_spot": {"uz": "📍 Joylashuvni o'zgartirish", "ru": "📍 Изменить местоположение", "ko": "📍 위치 변경"},
    "profile_updated": {
        "uz": "✅ Ma'lumot yangilandi!",
        "ru": "✅ Данные обновлены!",
        "ko": "✅ 정보가 업데이트되었습니다!",
    },
    # ---- Jadval / skip ----
    "schedule_heading": {
        "uz": "📅 Keyingi 10 kunlik yetkazib berish jadvali",
        "ru": "📅 График доставки на ближайшие 10 дней",
        "ko": "📅 향후 10일 배달 일정",
    },
    "skip_button": {"uz": "⏭ Bekor qilish", "ru": "⏭ Пропустить", "ko": "⏭ 건너뛰기"},
    "skip_confirmed": {
        "uz": "✅ {date} kuni bekor qilindi. Obunangiz muddati 1 kunga uzaytirildi.",
        "ru": "✅ Доставка {date} отменена. Срок подписки продлён на 1 день.",
        "ko": "✅ {date} 배달이 취소되었습니다. 구독 기간이 하루 연장되었습니다.",
    },
    "skip_too_late": {
        "uz": "Kechikdingiz — bu kunni endi bekor qilib bo'lmaydi (soat {cutoff}:00 dan keyin bekor qilinmaydi).",
        "ru": "Уже поздно — этот день нельзя отменить (после {cutoff}:00 отмена недоступна).",
        "ko": "이미 늦었습니다 — 이 날짜는 취소할 수 없습니다 ({cutoff}시 이후 취소 불가).",
    },
    "delivery_status_planned": {"uz": "🕒 Rejalashtirilgan", "ru": "🕒 Запланировано", "ko": "🕒 예정됨"},
    "delivery_status_confirmed": {"uz": "📦 Tasdiqlangan", "ru": "📦 Подтверждено", "ko": "📦 확정됨"},
    "delivery_status_delivered": {"uz": "✅ Yetkazildi", "ru": "✅ Доставлено", "ko": "✅ 배달완료"},
    "delivery_status_skipped": {"uz": "⏭ Bekor qilindi", "ru": "⏭ Пропущено", "ko": "⏭ 건너뜀"},
    "delivery_status_failed": {"uz": "⚠️ Yetkazilmadi", "ru": "⚠️ Не доставлено", "ko": "⚠️ 배달실패"},
    # ---- Xatolar ----
    "error_generic": {
        "uz": "Kechirasiz, xatolik yuz berdi. Qayta urinib ko'ring yoki admin bilan bog'laning.",
        "ru": "Извините, произошла ошибка. Попробуйте снова или свяжитесь с админом.",
        "ko": "죄송합니다, 오류가 발생했습니다. 다시 시도하거나 관리자에게 문의해 주세요.",
    },
    "error_cart_empty": {
        "uz": "Savatingiz bo'sh. Avval taomlarni tanlang.",
        "ru": "Ваша корзина пуста. Сначала выберите блюда.",
        "ko": "장바구니가 비어 있습니다. 먼저 음식을 선택해 주세요.",
    },
    "error_cart_wrong_count": {
        "uz": "Tanlangan kunlar soni ({selected}) rejadagi ovqatlar soniga ({required}) mos kelmayapti.",
        "ru": "Количество выбранных дней ({selected}) не совпадает с числом порций в плане ({required}).",
        "ko": "선택한 날짜 수({selected})가 요금제의 식사 수({required})와 일치하지 않습니다.",
    },
    "error_item_not_on_menu": {
        "uz": "Tanlangan taom {date} kuni menyuda yo'q. Menyuni yangilab qayta tanlang.",
        "ru": "Выбранное блюдо недоступно в меню на {date}. Обновите меню и выберите снова.",
        "ko": "선택한 메뉴가 {date}에 제공되지 않습니다. 메뉴를 새로고침 후 다시 선택해 주세요.",
    },
    "error_not_registered": {
        "uz": "Avval ro'yxatdan o'ting: /start",
        "ru": "Сначала зарегистрируйтесь: /start",
        "ko": "먼저 등록해 주세요: /start",
    },
    "error_blocked": {
        "uz": "Sizga botdan foydalanish taqiqlangan.",
        "ru": "Вам запрещено пользоваться ботом.",
        "ko": "봇 사용이 차단되었습니다.",
    },
    "error_order_already_paid": {
        "uz": "Bu buyurtma allaqachon to'langan.",
        "ru": "Этот заказ уже оплачен.",
        "ko": "이 주문은 이미 결제되었습니다.",
    },
    "error_order_not_payable": {
        "uz": "Bu buyurtmani endi to'lab bo'lmaydi (bekor qilingan yoki qaytarilgan).",
        "ru": "Этот заказ больше нельзя оплатить (отменён или возвращён).",
        "ko": "이 주문은 더 이상 결제할 수 없습니다 (취소 또는 환불됨).",
    },
    # ---- Admin ----
    "admin_only": {"uz": "Bu buyruq faqat adminlar uchun.", "ru": "Эта команда только для админов.", "ko": "이 명령어는 관리자 전용입니다."},
    "stats_heading": {"uz": "📊 Statistika", "ru": "📊 Статистика", "ko": "📊 통계"},
    "kitchen_heading": {"uz": "👨‍🍳 Oshxona rejasi", "ru": "👨‍🍳 План кухни", "ko": "👨‍🍳 주방 계획"},
    "pending_heading": {"uz": "⏳ To'lov kutayotgan buyurtmalar", "ru": "⏳ Заказы, ожидающие оплаты", "ko": "⏳ 결제 대기 중인 주문"},
    "no_pending_orders": {"uz": "To'lov kutayotgan buyurtma yo'q.", "ru": "Нет заказов, ожидающих оплаты.", "ko": "결제 대기 중인 주문이 없습니다."},
    "admin_confirm_button": {"uz": "✅ Tasdiqlash", "ru": "✅ Подтвердить", "ko": "✅ 승인"},
    "admin_reject_button": {"uz": "❌ Rad etish", "ru": "❌ Отклонить", "ko": "❌ 거부"},
    "admin_order_confirmed": {"uz": "✅ {reference} tasdiqlandi.", "ru": "✅ {reference} подтверждён.", "ko": "✅ {reference} 승인됨."},
    "admin_order_rejected": {"uz": "❌ {reference} rad etildi.", "ru": "❌ {reference} отклонён.", "ko": "❌ {reference} 거부됨."},
    "admin_order_not_found": {"uz": "Bunday buyurtma topilmadi.", "ru": "Такой заказ не найден.", "ko": "해당 주문을 찾을 수 없습니다."},
    "factory_request_notify_admin": {
        "uz": "📍 Yangi fabrika so'rovi!\n\nMijoz: {full_name} (@{username})\nXabar: {text}",
        "ru": "📍 Новый запрос на фабрику!\n\nКлиент: {full_name} (@{username})\nСообщение: {text}",
        "ko": "📍 새로운 공장 등록 요청!\n\n고객: {full_name} (@{username})\n메시지: {text}",
    },
    "renewal_reminder": {
        "uz": "⏰ Obunangiz {days} kundan keyin tugaydi. Yangilash uchun \"{open_app}\" tugmasini bosing.",
        "ru": "⏰ Ваша подписка истекает через {days} дн. Нажмите \"{open_app}\", чтобы продлить.",
        "ko": "⏰ 구독이 {days}일 후 만료됩니다. \"{open_app}\"을(를) 눌러 갱신해 주세요.",
    },
    "tomorrow_meal_reminder": {
        "uz": "🍱 Ertaga sizga \"{meal_name}\" yetkaziladi ({factory}, {window}).",
        "ru": "🍱 Завтра вам доставят \"{meal_name}\" ({factory}, {window}).",
        "ko": "🍱 내일 \"{meal_name}\"이(가) 배달됩니다 ({factory}, {window}).",
    },
}

WEEKDAY_NAMES: dict[int, dict[str, str]] = {
    0: {"uz": "Dushanba", "ru": "Понедельник", "ko": "월요일"},
    1: {"uz": "Seshanba", "ru": "Вторник", "ko": "화요일"},
    2: {"uz": "Chorshanba", "ru": "Среда", "ko": "수요일"},
    3: {"uz": "Payshanba", "ru": "Четверг", "ko": "목요일"},
    4: {"uz": "Juma", "ru": "Пятница", "ko": "금요일"},
    5: {"uz": "Shanba", "ru": "Суббота", "ko": "토요일"},
    6: {"uz": "Yakshanba", "ru": "Воскресенье", "ko": "일요일"},
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
