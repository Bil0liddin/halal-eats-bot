"""Telegram Mini App sahifasining o'zi (HTML/JS).

Uch ekran: Reja tanlash -> Menyu tuzish (kun/hafta bo'yicha) -> Checkout, va
alohida "Mening obunam" bo'limi (kunlik ovqatlarni ko'rish/o'zgartirish,
obunani bekor qilish). Til, narxlar, menyu va kesim (cutoff) vaqti butunlay
`/api/...` orqali serverdan olinadi — bu faylda hech qanday hardcoded matn
yoki qiymat yo'q.
"""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/webapp", response_class=HTMLResponse)
async def webapp_page():
    """Mini App sahifasini qaytaradi."""
    return HTMLResponse(_PAGE)


_PAGE = r"""
<!DOCTYPE html>
<html lang="uz">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Halol Food</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://js.tosspayments.com/v1/payment"></script>
  <style>
    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0; padding: 14px 14px 24px;
      background: var(--tg-theme-bg-color, #f5f6f8);
      color: var(--tg-theme-text-color, #111);
    }
    h1 { font-size: 18px; margin: 4px 0 4px; }
    h2 { font-size: 15px; margin: 0 0 10px; }
    p { margin: 0; }
    .muted { opacity: .6; font-size: 12px; }
    .hidden { display: none !important; }

    .tabbar {
      position: sticky; top: 0; z-index: 5; display: flex; gap: 6px;
      background: var(--tg-theme-bg-color, #f5f6f8); padding: 0 0 10px;
      margin-bottom: 10px; border-bottom: 1px solid rgba(128,128,128,.15);
    }
    .tab { flex: 1; background: transparent; color: inherit; border: none; border-radius: 8px; padding: 8px 6px; font-size: 12.5px; opacity: .55; }
    .tab.active { opacity: 1; background: var(--tg-theme-secondary-bg-color, #fff); font-weight: 600; }

    .screen { display: none; }
    .screen.active { display: block; }

    .skeleton { background: linear-gradient(90deg, rgba(128,128,128,.15) 25%, rgba(128,128,128,.25) 37%, rgba(128,128,128,.15) 63%); background-size: 400% 100%; animation: skeleton 1.4s ease infinite; border-radius: 12px; }
    @keyframes skeleton { 0% { background-position: 100% 50%; } 100% { background-position: 0 50%; } }
    .skeleton-card { height: 90px; margin-bottom: 10px; }

    .banner { background: linear-gradient(135deg, #34c759, #2ea6ff); color: #fff; border-radius: 12px; padding: 12px 14px; margin-bottom: 12px; font-size: 13px; }
    .banner.info { background: rgba(46,166,255,.15); color: var(--tg-theme-text-color, #111); border: 1px solid rgba(46,166,255,.35); }
    .banner b { font-size: 14px; }

    /* --- Reja kartalari --- */
    .plan-card { background: var(--tg-theme-secondary-bg-color, #fff); border-radius: 16px; padding: 16px; margin-bottom: 12px; }
    .plan-card h3 { margin: 0 0 6px; font-size: 16px; }
    .plan-card .sub { font-size: 12px; opacity: .65; margin-bottom: 8px; }
    .plan-card .price { font-weight: 700; font-size: 20px; margin-bottom: 12px; }
    .plan-card .price small { font-weight: 400; font-size: 12px; opacity: .6; }
    .plan-card button { width: 100%; }

    .cancel-link { display: block; text-align: center; color: #ff3b30; font-size: 12.5px; background: none; border: none; padding: 10px; margin: 4px auto 0; }

    /* --- Kun kartalari (menyu tuzish) --- */
    .day-grid { display: flex; flex-direction: column; gap: 8px; }
    .day-card { display: flex; align-items: center; gap: 10px; background: var(--tg-theme-secondary-bg-color, #fff); border-radius: 12px; padding: 10px 12px; border: 2px solid transparent; }
    .day-card.filled { border-color: #34c759; }
    .day-card.locked { opacity: .5; }
    .day-card .day-name { font-weight: 600; font-size: 13px; width: 84px; flex-shrink: 0; }
    .day-card .day-status { flex: 1; font-size: 12.5px; opacity: .75; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .day-card .day-icon { font-size: 16px; }

    .week-tabs { display: flex; gap: 6px; margin-bottom: 12px; overflow-x: auto; }
    .week-tab { flex-shrink: 0; background: var(--tg-theme-secondary-bg-color, #fff); color: inherit; border: 2px solid transparent; border-radius: 10px; padding: 8px 14px; font-size: 12.5px; }
    .week-tab.active { border-color: #2ea6ff; font-weight: 600; }

    .progress-bar { background: var(--tg-theme-secondary-bg-color, #fff); border-radius: 10px; padding: 8px 12px; margin-bottom: 12px; font-size: 12.5px; font-weight: 600; text-align: center; }

    /* --- Ovqat kartasi (kun tanlovchida) --- */
    .food-card { position: relative; display: flex; gap: 10px; background: var(--tg-theme-secondary-bg-color, #fff); border-radius: 14px; padding: 10px; margin-bottom: 10px; border: 2px solid transparent; }
    .food-card.selected { border-color: #34c759; }
    .food-thumb { width: 56px; height: 56px; border-radius: 10px; flex-shrink: 0; overflow: hidden; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #ffd76b, #ff9f43); font-size: 26px; }
    .food-thumb img { width: 100%; height: 100%; object-fit: cover; }
    .food-info { flex: 1; min-width: 0; }
    .food-info h4 { margin: 0 0 4px; font-size: 13.5px; }
    .food-info .food-sub { font-size: 11.5px; opacity: .6; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .info-btn { position: absolute; top: 8px; right: 8px; background: rgba(128,128,128,.18); color: inherit; border: none; border-radius: 50%; width: 26px; height: 26px; font-size: 13px; line-height: 1; }

    /* --- Obuna ro'yxati --- */
    .sub-summary { background: var(--tg-theme-secondary-bg-color, #fff); border-radius: 14px; padding: 14px; margin-bottom: 14px; }
    .sub-summary .row { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px; }
    .week-group-label { font-size: 12.5px; font-weight: 700; opacity: .7; margin: 14px 0 6px; }
    .delivery-row { display: flex; align-items: center; gap: 10px; background: var(--tg-theme-secondary-bg-color, #fff); border-radius: 12px; padding: 10px; margin-bottom: 8px; }
    .delivery-row .food-thumb { width: 44px; height: 44px; font-size: 20px; }
    .delivery-row .d-info { flex: 1; min-width: 0; }
    .delivery-row .d-date { font-size: 11.5px; opacity: .6; }
    .delivery-row .d-name { font-size: 13px; font-weight: 600; }
    .delivery-row button { font-size: 11.5px; padding: 6px 10px; }
    .delivery-row .locked-label { font-size: 11px; opacity: .55; white-space: nowrap; }

    button { background: var(--tg-theme-button-color, #2ea6ff); color: var(--tg-theme-button-text-color, #fff); border: none; border-radius: 10px; padding: 10px 14px; font-size: 13px; }
    button:disabled { opacity: .4; }
    .ghost-btn { background: transparent; color: inherit; border: 1px solid rgba(128,128,128,.35); }

    .overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); display: flex; align-items: flex-end; justify-content: center; z-index: 30; }
    .overlay[hidden] { display: none; }
    .sheet { background: var(--tg-theme-bg-color, #fff); color: inherit; border-radius: 18px 18px 0 0; padding: 20px; width: 100%; max-width: 480px; max-height: 80vh; overflow-y: auto; }
    .sheet.centered { border-radius: 18px; margin-bottom: auto; margin-top: auto; }
    .sheet h2 { margin: 0 0 12px; }
    .sheet .field { display: flex; justify-content: space-between; font-size: 13px; padding: 6px 0; border-bottom: 1px solid rgba(128,128,128,.15); }
    .sheet .field:last-of-type { border-bottom: none; }
    .sheet-actions { display: flex; gap: 8px; margin-top: 16px; }
    .sheet-actions button { flex: 1; }

    #toast { position: fixed; bottom: 16px; left: 16px; right: 16px; background: #2ea6ff; color: #fff; text-align: center; padding: 10px; border-radius: 10px; display: none; font-size: 13px; z-index: 40; }
  </style>
</head>
<body>
  <div id="skeleton" class="skeleton skeleton-card"></div>
  <div id="skeleton2" class="skeleton skeleton-card"></div>

  <div id="app" class="hidden">
    <div class="tabbar">
      <button class="tab active" data-tab="plans" id="tab-plans"></button>
      <button class="tab" data-tab="subscription" id="tab-subscription"></button>
    </div>

    <!-- 1-ekran: Reja tanlash -->
    <div id="screen-plans" class="screen active">
      <div id="plans-list"></div>
    </div>

    <!-- 2-ekran: Menyu tuzish -->
    <div id="screen-builder" class="screen">
      <h1 id="builder-heading"></h1>
      <div id="builder-cutoff-banner" class="banner info"></div>
      <div id="builder-progress" class="progress-bar hidden"></div>
      <div id="week-tabs" class="week-tabs hidden"></div>
      <div id="day-grid" class="day-grid"></div>
    </div>

    <!-- 3-ekran: Mening obunam -->
    <div id="screen-subscription" class="screen">
      <div id="subscription-content"></div>
    </div>
  </div>

  <!-- Kun uchun ovqat tanlash varag'i -->
  <div id="day-sheet-overlay" class="overlay" hidden>
    <div class="sheet">
      <h2 id="day-sheet-heading"></h2>
      <div id="day-sheet-list"></div>
    </div>
  </div>

  <!-- Ovqat haqida ma'lumot varag'i -->
  <div id="info-sheet-overlay" class="overlay" hidden>
    <div class="sheet">
      <h2 id="info-sheet-name"></h2>
      <div id="info-sheet-body"></div>
      <div class="sheet-actions"><button id="info-sheet-close" class="ghost-btn"></button></div>
    </div>
  </div>

  <!-- Obunani bekor qilishni tasdiqlash -->
  <div id="cancel-confirm-overlay" class="overlay" hidden>
    <div class="sheet centered">
      <h2 id="cancel-confirm-title"></h2>
      <p id="cancel-confirm-body" class="muted"></p>
      <div class="sheet-actions">
        <button id="cancel-confirm-no" class="ghost-btn"></button>
        <button id="cancel-confirm-yes"></button>
      </div>
    </div>
  </div>

  <!-- To'lov / buyurtma natijasi -->
  <div id="pay-overlay" class="overlay" hidden>
    <div class="sheet centered">
      <h2 id="pay-heading"></h2>
      <div id="pay-body" class="muted"></div>
      <div class="sheet-actions"><button id="pay-close"></button></div>
    </div>
  </div>

  <div id="toast"></div>

  <script>
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();

    const STR = {
      uz: {
        plans_tab: "Reja", subscription_tab: "Mening obunam",
        meals: "ovqat", days: "kun", per_meal: "1 ovqat narxi", choose: "Tanlash",
        cancel_link: "Obunani bekor qilish",
        cancel_title: "Obunani bekor qilishni tasdiqlaysizmi?",
        cancel_body: "Qolgan ovqatlar bekor qilinadi.",
        cancel_yes: "Ha, bekor qilish", cancel_no: "Yo'q, davom etish",
        builder_weekly: "Kelasi hafta uchun menyuni tanlang",
        builder_monthly: "Kelasi oy uchun menyuni tanlang",
        cutoff_banner: (h) => `Ovqatni yetkazib berilishidan bir kun oldin, soat ${h}:00 gacha o'zgartirishingiz mumkin.`,
        week_tab: (n) => `Hafta ${n}`,
        progress: (used, total) => `${used} / ${total} ovqat tanlandi`,
        empty_day: "Tanlanmagan", locked_day: "Kesim o'tgan",
        confirm_order: "Buyurtmani tasdiqlash →",
        choose_food_for: (day) => `${day} kuni uchun ovqat tanlang`,
        info_description: "Tavsif", info_calories: "Kaloriya", info_allergens: "Allergenlar",
        info_halal: "Halal sertifikat", info_meat: "Go'sht turi", info_vegetarian: "Vegetarian",
        info_spicy: "Achchiqlik darajasi", close: "Yopish",
        meat_beef: "Mol go'shti", meat_chicken: "Tovuq", meat_lamb: "Qo'y go'shti", meat_none: "-",
        yes: "Ha", no: "Yo'q",
        sub_heading: "📦 Mening obunam", no_subscription: "Sizda hozircha faol obuna yo'q.",
        meals_left: "Qolgan ovqatlar", valid_until: "Amal qilish muddati",
        change_button: "O'zgartirish", locked_label: "🔒 O'zgartirib bo'lmaydi",
        view_details: "Batafsil →",
        order_created: "Buyurtma yaratildi", pay_instructions_sent: "\n\nTo'lov ma'lumotlari bot chatiga ham yuborildi.",
        not_registered: "Avval botda /start buyrug'ini bering va ro'yxatdan o'ting",
        error: "Xatolik yuz berdi", network_error: "Tarmoq xatosi — internetni tekshiring",
      },
      ru: {
        plans_tab: "Планы", subscription_tab: "Моя подписка",
        meals: "приёмов", days: "дней", per_meal: "Цена за приём", choose: "Выбрать",
        cancel_link: "Отменить подписку",
        cancel_title: "Отменить подписку?",
        cancel_body: "Оставшиеся приёмы пищи будут отменены.",
        cancel_yes: "Да, отменить", cancel_no: "Нет, продолжить",
        builder_weekly: "Выберите меню на следующую неделю",
        builder_monthly: "Выберите меню на следующий месяц",
        cutoff_banner: (h) => `Изменить можно за день до доставки, до ${h}:00.`,
        week_tab: (n) => `Неделя ${n}`,
        progress: (used, total) => `Выбрано ${used} / ${total}`,
        empty_day: "Не выбрано", locked_day: "Срок истёк",
        confirm_order: "Оформить заказ →",
        choose_food_for: (day) => `Выберите блюдо на ${day}`,
        info_description: "Описание", info_calories: "Калории", info_allergens: "Аллергены",
        info_halal: "Халяль сертификат", info_meat: "Вид мяса", info_vegetarian: "Вегетарианское",
        info_spicy: "Острота", close: "Закрыть",
        meat_beef: "Говядина", meat_chicken: "Курица", meat_lamb: "Баранина", meat_none: "-",
        yes: "Да", no: "Нет",
        sub_heading: "📦 Моя подписка", no_subscription: "У вас пока нет активной подписки.",
        meals_left: "Осталось порций", valid_until: "Действует до",
        change_button: "Изменить", locked_label: "🔒 Изменить нельзя",
        view_details: "Подробнее →",
        order_created: "Заказ создан", pay_instructions_sent: "\n\nДанные для оплаты также отправлены в чат бота.",
        not_registered: "Сначала отправьте /start боту и зарегистрируйтесь",
        error: "Произошла ошибка", network_error: "Ошибка сети — проверьте интернет",
      },
      en: {
        plans_tab: "Plans", subscription_tab: "My Subscription",
        meals: "meals", days: "days", per_meal: "Price per meal", choose: "Choose",
        cancel_link: "Cancel subscription",
        cancel_title: "Cancel your subscription?",
        cancel_body: "Your remaining meals will be cancelled.",
        cancel_yes: "Yes, cancel", cancel_no: "No, keep it",
        builder_weekly: "Choose the menu for next week",
        builder_monthly: "Choose the menu for next month",
        cutoff_banner: (h) => `You can change a day up until ${h}:00 the day before delivery.`,
        week_tab: (n) => `Week ${n}`,
        progress: (used, total) => `${used} / ${total} meals chosen`,
        empty_day: "Not chosen", locked_day: "Cutoff passed",
        confirm_order: "Confirm order →",
        choose_food_for: (day) => `Choose a meal for ${day}`,
        info_description: "Description", info_calories: "Calories", info_allergens: "Allergens",
        info_halal: "Halal certified", info_meat: "Meat type", info_vegetarian: "Vegetarian",
        info_spicy: "Spice level", close: "Close",
        meat_beef: "Beef", meat_chicken: "Chicken", meat_lamb: "Lamb", meat_none: "-",
        yes: "Yes", no: "No",
        sub_heading: "📦 My Subscription", no_subscription: "You don't have an active subscription yet.",
        meals_left: "Meals left", valid_until: "Valid until",
        change_button: "Change", locked_label: "🔒 Can't be changed",
        view_details: "View details →",
        order_created: "Order created", pay_instructions_sent: "\n\nPayment details were also sent to the bot chat.",
        not_registered: "Please register first with /start in the bot",
        error: "Something went wrong", network_error: "Network error — check your internet connection",
      },
    };

    let LANG = "uz";
    let CUTOFF_HOUR = 20;
    let TOSS_CLIENT_KEY = "";
    let BASE_URL = "";

    let plans = [];
    let activeSubscription = null;
    let selectedPlan = null;
    let builderWeeks = [];       // [{week_start, days:[{weekday,date,label,items}]}]
    let builderWeekIndex = 0;
    let cartByDate = {};         // { "2026-09-14": menu_item_id }
    let dayPickerMode = null;    // "builder" | "change"
    let dayPickerDate = null;

    function L(key) { return (STR[LANG] || STR.uz)[key]; }

    function showToast(text) {
      const el = document.getElementById("toast");
      el.textContent = text;
      el.style.display = "block";
      setTimeout(() => { el.style.display = "none"; }, 2400);
    }

    async function api(path, opts = {}) {
      let res;
      try {
        res = await fetch(path, {
          ...opts,
          headers: { "Content-Type": "application/json", "X-Telegram-Init-Data": tg.initData, ...(opts.headers || {}) },
        });
      } catch (e) {
        throw new Error(L("network_error"));
      }
      if (!res.ok) {
        let detail = L("error");
        try { detail = (await res.json()).detail || detail; } catch (e) {}
        throw new Error(detail);
      }
      return res.json();
    }

    // --- Tab navigatsiyasi ---
    document.querySelectorAll(".tab").forEach(btn => {
      btn.addEventListener("click", () => switchTab(btn.dataset.tab));
    });

    function switchTab(name) {
      document.querySelectorAll(".tab").forEach(b => b.classList.toggle("active", b.dataset.tab === name));
      document.querySelectorAll(".screen").forEach(s => s.classList.toggle("active", s.id === "screen-" + name));
      updateNativeButtons(name);
      if (name === "subscription") renderSubscriptionScreen();
    }

    // --- Telegram native Back/Main tugmalari ---
    // BackButton STEK sifatida ishlaydi: har ochilgan qatlam (kun varag'i,
    // ma'lumot varag'i, tasdiqlash varag'i, obuna tafsiloti va h.k.) o'zining
    // yopish funksiyasini stekka qo'shadi (pushBack), yopilganda stekdan
    // olib tashlaydi (popBack) — shunda bir nechta qatlam ustma-ust ochiq
    // bo'lganda ham "Orqaga" tugmasi har doim ENG USTKI qatlamni to'g'ri
    // yopadi (avval faqat bitta global handler bo'lgani uchun, masalan
    // ma'lumot varag'i kun varag'i ustida ochilganda "Orqaga" ishlamay
    // qolardi — mobil qurilmalarda aynan shu muammo edi).
    let backStack = [];
    tg.BackButton.onClick(() => {
      const handler = backStack[backStack.length - 1];
      if (handler) handler();
    });
    function pushBack(handler) {
      backStack.push(handler);
      tg.BackButton.show();
    }
    function popBack() {
      backStack.pop();
      if (backStack.length === 0) tg.BackButton.hide();
    }
    function resetBack(baseHandler) {
      // Yangi tub (top-level) ekranga o'tilganda butun stek tozalanadi —
      // qatlamlar orasida biror joyda unutilib qolgan handler bo'lmasin.
      backStack = baseHandler ? [baseHandler] : [];
      if (backStack.length === 0) tg.BackButton.hide(); else tg.BackButton.show();
    }

    let mainHandler = null;
    function setMainButton(text, handler, enabled) {
      if (mainHandler) tg.MainButton.offClick(mainHandler);
      if (!text) { tg.MainButton.hide(); mainHandler = null; return; }
      tg.MainButton.setText(text);
      mainHandler = handler;
      tg.MainButton.onClick(mainHandler);
      if (enabled) tg.MainButton.enable(); else tg.MainButton.disable();
      tg.MainButton.show();
    }

    function updateNativeButtons(screenName) {
      if (screenName === "plans") { resetBack(null); setMainButton(null); }
      else if (screenName === "subscription") { resetBack(() => switchTab("plans")); setMainButton(null); }
      else if (screenName === "builder") { resetBack(() => switchTab("plans")); updateBuilderMainButton(); }
    }

    // --- 1-ekran: Reja tanlash ---
    function renderPlans() {
      const el = document.getElementById("plans-list");
      el.innerHTML = plans.map(p => `
        <div class="plan-card">
          <h3>${p.name}</h3>
          <div class="sub">${p.meals_count} ${L("meals")} · ${p.duration_days} ${L("days")}</div>
          <div class="price">${p.price_krw.toLocaleString()}원 <small>(${L("per_meal")}: ${p.price_per_meal.toLocaleString()}원)</small></div>
          <button onclick="startBuilder(${p.id})">${L("choose")}</button>
        </div>
      `).join("");
    }

    // Bitta umumiy tasdiqlash varag'i — hozircha faqat "obunani bekor
    // qilish" shu varaqdan foydalanadi.
    let pendingConfirmAction = null;

    function openConfirmSheet({ title, body, yesText, noText, onConfirm }) {
      document.getElementById("cancel-confirm-title").textContent = title;
      document.getElementById("cancel-confirm-body").textContent = body;
      document.getElementById("cancel-confirm-yes").textContent = yesText;
      document.getElementById("cancel-confirm-no").textContent = noText;
      pendingConfirmAction = onConfirm;
      document.getElementById("cancel-confirm-overlay").hidden = false;
      pushBack(closeConfirmSheet);
    }

    function closeConfirmSheet() {
      document.getElementById("cancel-confirm-overlay").hidden = true;
      pendingConfirmAction = null;
      popBack();
    }

    document.getElementById("cancel-confirm-no").addEventListener("click", closeConfirmSheet);
    document.getElementById("cancel-confirm-yes").addEventListener("click", async () => {
      const action = pendingConfirmAction;
      closeConfirmSheet();
      if (!action) return;
      try { await action(); } catch (e) { showToast(e.message); }
    });

    // --- 2-ekran: Menyu tuzish ---
    async function startBuilder(planId) {
      selectedPlan = plans.find(p => p.id === planId);
      document.getElementById("builder-heading").textContent =
        selectedPlan.period === "weekly" ? L("builder_weekly") : L("builder_monthly");
      document.getElementById("builder-cutoff-banner").textContent = L("cutoff_banner")(CUTOFF_HOUR);

      const weekCount = selectedPlan.period === "monthly" ? Math.max(1, Math.ceil(selectedPlan.duration_days / 7)) : 1;
      const [cartData, firstWeek] = await Promise.all([api("/api/cart"), api("/api/menu")]);
      cartByDate = {};
      for (const item of cartData.items) cartByDate[item.delivery_date] = item.menu_item_id;

      builderWeeks = [firstWeek];
      for (let i = 1; i < weekCount; i++) {
        const start = new Date(firstWeek.week_start);
        start.setDate(start.getDate() + 7 * i);
        const week = await api(`/api/menu?week_start=${start.toISOString().slice(0, 10)}`);
        builderWeeks.push(week);
      }
      builderWeekIndex = 0;

      const tabsEl = document.getElementById("week-tabs");
      if (weekCount > 1) {
        tabsEl.classList.remove("hidden");
        tabsEl.innerHTML = builderWeeks.map((w, i) => `
          <button class="week-tab ${i === 0 ? 'active' : ''}" onclick="selectBuilderWeek(${i})">${L('week_tab')(i + 1)}</button>
        `).join("");
      } else {
        tabsEl.classList.add("hidden");
        tabsEl.innerHTML = "";
      }

      switchScreen("builder");
      renderBuilderDays();
    }

    function switchScreen(name) {
      document.querySelectorAll(".screen").forEach(s => s.classList.toggle("active", s.id === "screen-" + name));
      document.querySelectorAll(".tab").forEach(b => b.classList.remove("active"));
      updateNativeButtons(name);
    }

    function selectBuilderWeek(i) {
      builderWeekIndex = i;
      document.querySelectorAll(".week-tab").forEach((b, idx) => b.classList.toggle("active", idx === i));
      renderBuilderDays();
    }

    function selectedCountForPlan() {
      // Faqat shu reja doirasidagi kunlar hisoblanadi: barcha builderWeeks kunlaridan tanlanganlar
      let count = 0;
      for (const week of builderWeeks) {
        for (const day of week.days) {
          if (cartByDate[day.date]) count++;
        }
      }
      return count;
    }

    function renderBuilderDays() {
      const week = builderWeeks[builderWeekIndex];
      const progressEl = document.getElementById("builder-progress");
      if (selectedPlan.period === "monthly") {
        progressEl.classList.remove("hidden");
        progressEl.textContent = L("progress")(selectedCountForPlan(), selectedPlan.meals_count);
      } else {
        progressEl.classList.add("hidden");
      }

      const el = document.getElementById("day-grid");
      el.innerHTML = week.days.map(day => {
        const chosenId = cartByDate[day.date];
        const chosenItem = chosenId ? day.items.find(i => i.menu_item_id === chosenId) : null;
        const locked = isPastCutoff(day.date) && !chosenId;
        return `
          <div class="day-card ${chosenId ? 'filled' : ''} ${locked ? 'locked' : ''}"
               onclick="${locked || !day.items.length ? '' : `openDaySheet('builder', '${day.date}')`}">
            <span class="day-icon">${chosenId ? '✅' : (locked ? '🔒' : '⚪')}</span>
            <span class="day-name">${day.label}</span>
            <span class="day-status">${chosenItem ? chosenItem.name : (locked ? L('locked_day') : (day.items.length ? L('empty_day') : '—'))}</span>
          </div>
        `;
      }).join("");

      updateBuilderMainButton();
    }

    function isPastCutoff(dateStr) {
      // Mijozning qurilma vaqtidan taxminiy hisoblanadi — faqat vizual maslahat
      // uchun; haqiqiy tekshiruv har doim serverda ("Mening obunam"dagi
      // can_change maydoni) amalga oshadi.
      const d = new Date(dateStr + "T00:00:00");
      const deadline = new Date(d);
      deadline.setDate(deadline.getDate() - 1);
      deadline.setHours(CUTOFF_HOUR, 0, 0, 0);
      return new Date() >= deadline;
    }

    function updateBuilderMainButton() {
      const count = selectedCountForPlan();
      const ready = selectedPlan && count === selectedPlan.meals_count;
      setMainButton(L("confirm_order"), doCheckout, ready);
    }

    async function doCheckout() {
      try {
        const result = await api("/api/orders/checkout", { method: "POST", body: JSON.stringify({ plan_id: selectedPlan.id }) });
        openPayOverlay(result);
      } catch (e) { showToast(e.message); }
    }

    // --- Kun uchun ovqat tanlash varag'i ---
    function openDaySheet(mode, dateStr) {
      dayPickerMode = mode;
      dayPickerDate = dateStr;
      let day;
      if (mode === "builder") {
        day = builderWeeks[builderWeekIndex].days.find(d => d.date === dateStr);
      } else {
        const delivery = activeSubscription.deliveries.find(d => d.delivery_date === dateStr);
        day = { label: delivery.weekday_label, items: dayPickerMenuItems || [] };
      }

      document.getElementById("day-sheet-heading").textContent = L("choose_food_for")(day.label);
      const chosenId = mode === "builder" ? cartByDate[dateStr] : (activeSubscription.deliveries.find(d => d.delivery_date === dateStr) || {}).menu_item_id;

      document.getElementById("day-sheet-list").innerHTML = day.items.map(item => `
        <div class="food-card ${item.menu_item_id === chosenId ? 'selected' : ''}" onclick="chooseFood(${item.menu_item_id})">
          <div class="food-thumb">${item.photo_url ? `<img src="${item.photo_url}" onerror="this.parentElement.innerHTML='🍽️'" />` : '🍽️'}</div>
          <div class="food-info">
            <h4>${item.name}</h4>
            <div class="food-sub">${item.description || ""}</div>
          </div>
          <button class="info-btn" onclick="event.stopPropagation(); openInfoSheet(${item.menu_item_id}, '${mode}')">ℹ️</button>
        </div>
      `).join("");

      document.getElementById("day-sheet-overlay").hidden = false;
      pushBack(closeDaySheet);
    }

    function closeDaySheet() {
      document.getElementById("day-sheet-overlay").hidden = true;
      popBack();
      if (dayPickerMode === "builder") updateBuilderMainButton();
    }

    async function chooseFood(menuItemId) {
      try {
        if (dayPickerMode === "builder") {
          await api("/api/cart", {
            method: "PUT",
            body: JSON.stringify({ plan_id: selectedPlan.id, delivery_date: dayPickerDate, menu_item_id: menuItemId, qty: 1 }),
          });
          cartByDate[dayPickerDate] = menuItemId;
          closeDaySheet();
          renderBuilderDays();
        } else {
          await api("/api/deliveries/change", {
            method: "POST",
            body: JSON.stringify({ delivery_date: dayPickerDate, menu_item_id: menuItemId }),
          });
          closeDaySheet();
          await loadSubscription();
          renderSubscriptionDetail();
        }
      } catch (e) { showToast(e.message); }
    }

    // --- Ovqat haqida ma'lumot varag'i ---
    let dayPickerMenuItems = null;

    function openInfoSheet(menuItemId, mode) {
      const source = mode === "builder" ? builderWeeks[builderWeekIndex].days.flatMap(d => d.items) : dayPickerMenuItems;
      const item = (source || []).find(i => i.menu_item_id === menuItemId);
      if (!item) return;

      document.getElementById("info-sheet-name").textContent = item.name;
      const meat = item.contains_beef ? L("meat_beef") : item.contains_chicken ? L("meat_chicken") : item.contains_lamb ? L("meat_lamb") : L("meat_none");
      const rows = [
        [L("info_description"), item.description || "-"],
        [L("info_calories"), item.calories ? `${item.calories} kcal` : "-"],
        [L("info_allergens"), item.allergens || "-"],
        [L("info_halal"), item.is_halal_certified ? "✅" : "-"],
        [L("info_meat"), meat],
        [L("info_vegetarian"), item.is_vegetarian ? L("yes") : L("no")],
      ];
      if (item.spicy_level > 0) rows.push([L("info_spicy"), "🌶️".repeat(item.spicy_level)]);

      document.getElementById("info-sheet-body").innerHTML = rows.map(([k, v]) => `
        <div class="field"><span>${k}</span><span>${v}</span></div>
      `).join("");
      document.getElementById("info-sheet-close").textContent = L("close");
      document.getElementById("info-sheet-overlay").hidden = false;
      pushBack(closeInfoSheet);
    }

    function closeInfoSheet() {
      document.getElementById("info-sheet-overlay").hidden = true;
      popBack();
    }

    document.getElementById("info-sheet-close").addEventListener("click", closeInfoSheet);

    // --- 3-ekran: Mening obunam ---
    // Ikki qatlam: avval umumiy KARTA (reja nomi + qisqa holat), keyin
    // shu kartani bosib ICHIGA kirilganda kunma-kun ro'yxat + pastda
    // "obunani bekor qilish" tugmasi ko'rinadi.
    let subscriptionView = "overview"; // "overview" | "detail"

    async function loadSubscription() {
      const data = await api("/api/orders/me/subscription");
      activeSubscription = data.subscription;
    }

    function renderSubscriptionScreen() {
      subscriptionView = "overview";
      document.getElementById("tab-subscription").textContent = L("subscription_tab");
      renderSubscriptionOverview();
    }

    function renderSubscriptionOverview() {
      const el = document.getElementById("subscription-content");
      if (!activeSubscription) {
        el.innerHTML = `<h1>${L("sub_heading")}</h1><p class="muted">${L("no_subscription")}</p>`;
        return;
      }
      const s = activeSubscription;
      el.innerHTML = `
        <h1>${L("sub_heading")}</h1>
        <div class="plan-card">
          <h3>${s.plan_name || ""}</h3>
          <div class="sub">${L("meals_left")}: ${s.meals_left}/${s.meals_total}</div>
          <div class="sub">${L("valid_until")}: ${s.ends_on}</div>
          <button onclick="openSubscriptionDetail()">${L("view_details")}</button>
        </div>`;
    }

    function openSubscriptionDetail() {
      subscriptionView = "detail";
      renderSubscriptionDetail();
      pushBack(closeSubscriptionDetail);
    }

    function closeSubscriptionDetail() {
      subscriptionView = "overview";
      renderSubscriptionOverview();
      popBack();
    }

    function renderSubscriptionDetail() {
      const el = document.getElementById("subscription-content");
      const s = activeSubscription;
      if (!s) { renderSubscriptionOverview(); return; }

      const groups = {};
      for (const d of s.deliveries) {
        if (!groups[d.week_start]) groups[d.week_start] = [];
        groups[d.week_start].push(d);
      }
      const weekStarts = Object.keys(groups).sort();

      let html = `<h1>${s.plan_name || L("sub_heading")}</h1>
        <div class="sub-summary">
          <div class="row"><span>${L("meals_left")}</span><span>${s.meals_left}/${s.meals_total}</span></div>
          <div class="row"><span>${L("valid_until")}</span><span>${s.ends_on}</span></div>
        </div>`;

      weekStarts.forEach((ws, idx) => {
        if (weekStarts.length > 1) html += `<div class="week-group-label">${L('week_tab')(idx + 1)}</div>`;
        for (const d of groups[ws]) {
          html += `
            <div class="delivery-row">
              <div class="food-thumb">🍽️</div>
              <div class="d-info">
                <div class="d-date">${d.weekday_label} · ${d.delivery_date}</div>
                <div class="d-name">${d.menu_item_name}</div>
              </div>
              ${d.can_change
                ? `<button onclick="openChangeSheet('${d.delivery_date}')">${L('change_button')}</button>`
                : `<span class="locked-label">${L('locked_label')}</span>`}
            </div>`;
        }
      });

      html += `<button id="cancel-sub-link" class="cancel-link">${L("cancel_link")}</button>`;
      el.innerHTML = html;
      document.getElementById("cancel-sub-link").addEventListener("click", onCancelSubscriptionClick);
    }

    function onCancelSubscriptionClick() {
      openConfirmSheet({
        title: L("cancel_title"), body: L("cancel_body"),
        yesText: L("cancel_yes"), noText: L("cancel_no"),
        onConfirm: async () => {
          await api("/api/subscriptions/cancel", { method: "POST" });
          activeSubscription = null;
          closeSubscriptionDetail();
          showToast(L("cancel_yes"));
        },
      });
    }

    async function openChangeSheet(dateStr) {
      // O'sha kunning haftasi (week_start) menyusidan variantlarni olamiz
      const delivery = activeSubscription.deliveries.find(d => d.delivery_date === dateStr);
      try {
        const week = await api(`/api/menu?week_start=${delivery.week_start}`);
        const day = week.days.find(d => d.date === dateStr);
        dayPickerMenuItems = day ? day.items : [];
      } catch (e) {
        dayPickerMenuItems = [];
      }
      openDaySheet("change", dateStr);
    }

    // --- To'lov natijasi ---
    function openPayOverlay(order) {
      document.getElementById("pay-heading").textContent = `${L("order_created")} — #${order.reference}`;
      let body = `${order.amount_krw.toLocaleString()}원\n\n`;
      body += order.instructions || (order.checkout_url ? order.checkout_url : "");
      body += L("pay_instructions_sent");
      document.getElementById("pay-body").textContent = body;
      document.getElementById("pay-close").textContent = L("close");
      document.getElementById("pay-overlay").hidden = false;
      pushBack(closePayOverlay);
    }
    function closePayOverlay() {
      document.getElementById("pay-overlay").hidden = true;
      popBack();
    }
    document.getElementById("pay-close").addEventListener("click", async () => {
      closePayOverlay();
      await loadSubscription();
      switchTab("plans");
      renderPlans();
    });

    // --- Ilovani ishga tushirish ---
    async function bootstrap() {
      try {
        const me = await api("/api/me");
        LANG = me.lang || "uz";
        CUTOFF_HOUR = me.cutoff_hour || 20;

        if (!me.is_registered) {
          document.getElementById("skeleton").classList.add("hidden");
          document.getElementById("skeleton2").classList.add("hidden");
          document.body.insertAdjacentHTML("beforeend", `<p class="muted" style="margin-top:40px;text-align:center;">${L("not_registered")}</p>`);
          return;
        }

        document.getElementById("tab-plans").textContent = L("plans_tab");
        document.getElementById("tab-subscription").textContent = L("subscription_tab");

        const [plansData] = await Promise.all([api("/api/plans"), loadSubscription()]);
        plans = plansData;
        renderPlans();
        updateNativeButtons("plans");

        document.getElementById("skeleton").classList.add("hidden");
        document.getElementById("skeleton2").classList.add("hidden");
        document.getElementById("app").classList.remove("hidden");
      } catch (e) {
        showToast(e.message);
      }
    }

    bootstrap();
  </script>
</body>
</html>
"""
