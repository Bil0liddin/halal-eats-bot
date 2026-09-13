"""Telegram Mini App sahifasining o'zi (HTML/JS).

Vazifa ta'rifida "Mini App allaqachon mavjud, uni qayta yozmang" deyilgan edi,
lekin haqiqatda hali frontend yo'q edi — shuning uchun API bilan ishlaydigan
oddiy, ammo to'liq funksional sahifa shu yerda qo'shildi. Kelajakda alohida
frontend loyihasi bo'lsa, bu fayl butunlay almashtirilishi mumkin — u faqat
`/api/...` endpointlaridan foydalanadi, boshqa hech narsaga bog'liq emas.
"""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/webapp", response_class=HTMLResponse)
async def webapp_page():
    """Mini App sahifasini qaytaradi. Til va ma'lumotlar butunlay JS orqali `/api/...` dan olinadi."""
    return HTMLResponse(_PAGE)


_PAGE = r"""
<!DOCTYPE html>
<html lang="uz">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Halol Food</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0; padding: 0 14px 90px;
      background: var(--tg-theme-bg-color, #f5f6f8);
      color: var(--tg-theme-text-color, #111);
    }
    h1 { font-size: 18px; margin: 14px 0 4px; }
    .muted { opacity: .6; font-size: 12px; }
    .banner {
      background: linear-gradient(135deg, #34c759, #2ea6ff);
      color: #fff; border-radius: 12px; padding: 12px 14px; margin: 10px 0; font-size: 13px;
    }
    .banner b { font-size: 14px; }
    .tabbar {
      position: sticky; top: 0; z-index: 5; display: flex; gap: 6px;
      background: var(--tg-theme-bg-color, #f5f6f8); padding: 10px 0;
      margin: 0 -14px 10px; padding-left: 14px; padding-right: 14px;
      border-bottom: 1px solid rgba(128,128,128,.15);
    }
    .tab { flex: 1; background: transparent; color: inherit; border: none; border-radius: 8px; padding: 8px 6px; font-size: 12.5px; opacity: .55; }
    .tab.active { opacity: 1; background: var(--tg-theme-secondary-bg-color, #fff); font-weight: 600; }
    .view { display: none; }
    .view.active { display: block; }

    .plan-card {
      background: var(--tg-theme-secondary-bg-color, #fff);
      border: 2px solid transparent; border-radius: 14px; padding: 14px; margin-bottom: 10px;
    }
    .plan-card.selected { border-color: #2ea6ff; }
    .plan-card h3 { margin: 0 0 4px; font-size: 15px; }
    .plan-card .price { font-weight: 700; font-size: 16px; margin-top: 6px; }
    .plan-card .sub { font-size: 12px; opacity: .65; }
    .plan-card button { margin-top: 10px; }

    .day-card { background: var(--tg-theme-secondary-bg-color, #fff); border-radius: 12px; padding: 12px; margin-bottom: 10px; border: 2px solid transparent; }
    .day-card.day-selected { border-color: #34c759; }
    .day-card h4 { margin: 0 0 8px; font-size: 13px; }
    .dish-row { display: flex; flex-wrap: wrap; gap: 6px; }
    .dish-chip {
      background: transparent; border: 1px solid rgba(128,128,128,.35); color: inherit;
      border-radius: 999px; padding: 6px 12px; font-size: 12px;
    }
    .dish-chip.selected { background: #2ea6ff; border-color: #2ea6ff; color: #fff; }
    .empty { opacity: .6; text-align: center; margin-top: 30px; font-size: 13px; }

    button { background: var(--tg-theme-button-color, #2ea6ff); color: var(--tg-theme-button-text-color, #fff); border: none; border-radius: 8px; padding: 8px 14px; font-size: 13px; }
    button:disabled { opacity: .4; }

    .cart-bar {
      position: fixed; left: 0; right: 0; bottom: 0; z-index: 10;
      background: var(--tg-theme-secondary-bg-color, #fff);
      border-top: 1px solid rgba(128,128,128,.2);
      padding: 10px 14px; display: flex; align-items: center; justify-content: space-between;
    }
    .cart-bar span { font-size: 13px; font-weight: 600; }

    .overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; z-index: 20; padding: 20px; }
    .overlay[hidden] { display: none; }
    .overlay-card { background: var(--tg-theme-bg-color, #fff); color: inherit; border-radius: 16px; padding: 20px; width: 100%; max-width: 340px; text-align: left; white-space: pre-wrap; font-size: 13px; line-height: 1.5; }
    .overlay-card h2 { margin: 0 0 10px; font-size: 16px; }
    .overlay-card button { margin-top: 14px; width: 100%; }

    #toast { position: fixed; bottom: 70px; left: 14px; right: 14px; background: #2ea6ff; color: #fff; text-align: center; padding: 10px; border-radius: 10px; display: none; font-size: 13px; z-index: 30; }
  </style>
</head>
<body>
  <div id="app-content">
    <div id="status-banner" class="banner" hidden></div>

    <div class="tabbar">
      <button class="tab active" data-tab="plans" id="tab-plans">Rejalar</button>
      <button class="tab" data-tab="menu" id="tab-menu">Menyu</button>
    </div>

    <div id="view-plans" class="view active">
      <div id="plans-list"><p class="empty">…</p></div>
    </div>

    <div id="view-menu" class="view">
      <div id="menu-list"><p class="empty">Avval reja tanlang</p></div>
    </div>

    <div id="cart-bar" class="cart-bar" hidden>
      <span id="cart-progress">0/0</span>
      <button id="checkout-btn" disabled>Buyurtma berish</button>
    </div>

    <div id="pay-overlay" class="overlay" hidden>
      <div class="overlay-card">
        <h2 id="pay-heading"></h2>
        <div id="pay-body"></div>
        <button onclick="closePayOverlay()">Yopish</button>
      </div>
    </div>
  </div>

  <div id="toast"></div>

  <script>
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();

    const STR = {
      uz: { plans: "Rejalar", menu: "Menyu", choose_plan: "Avval reja tanlang", no_days: "Bu haftaga menyu e'lon qilinmagan",
            select_day: "kun tanlandi", checkout: "Buyurtma berish", not_registered: "Avval botda /start buyrug'ini bering va ro'yxatdan o'ting",
            error: "Xatolik yuz berdi", order_created: "Buyurtma yaratildi", close: "Yopish", pay_instructions_sent: "\n\nTo'lov ma'lumotlari bot chatiga ham yuborildi.",
            per_meal: "1 ovqat narxi", meals: "ovqat", days: "kun", choose: "Tanlash",
            limit_reached: "Kerakli kunlar soni tanlandi. Boshqa kunni qo'shish uchun avval birini bosib bekor qiling.",
            tap_to_remove: "Bekor qilish uchun bosing" },
      ru: { plans: "Планы", menu: "Меню", choose_plan: "Сначала выберите план", no_days: "Меню на эту неделю не опубликовано",
            select_day: "дней выбрано", checkout: "Оформить заказ", not_registered: "Сначала отправьте /start боту и зарегистрируйтесь",
            error: "Произошла ошибка", order_created: "Заказ создан", close: "Закрыть", pay_instructions_sent: "\n\nДанные для оплаты также отправлены в чат бота.",
            per_meal: "Цена за приём", meals: "приёмов", days: "дней", choose: "Выбрать",
            limit_reached: "Нужное количество дней уже выбрано. Чтобы добавить другой день, сначала отмените один.",
            tap_to_remove: "Нажмите, чтобы отменить" },
      ko: { plans: "플랜", menu: "메뉴", choose_plan: "먼저 플랜을 선택하세요", no_days: "이번 주 메뉴가 아직 게시되지 않았습니다",
            select_day: "일 선택됨", checkout: "주문하기", not_registered: "먼저 봇에서 /start로 등록해 주세요",
            error: "오류가 발생했습니다", order_created: "주문이 생성되었습니다", close: "닫기", pay_instructions_sent: "\n\n결제 정보가 봇 채팅에도 전송되었습니다.",
            per_meal: "1식 가격", meals: "식", days: "일", choose: "선택",
            limit_reached: "필요한 일수를 이미 선택했습니다. 다른 날을 추가하려면 먼저 하나를 취소하세요.",
            tap_to_remove: "취소하려면 누르세요" },
    };

    let LANG = "uz";
    let plans = [];
    let selectedPlanId = null;
    let cartByDate = {};  // { "2026-09-14": menu_item_id }
    let menuDays = [];    // [{date, label, items: [...]}]

    function L(key) { return (STR[LANG] || STR.uz)[key] || key; }

    function showToast(text) {
      const el = document.getElementById("toast");
      el.textContent = text;
      el.style.display = "block";
      setTimeout(() => { el.style.display = "none"; }, 2200);
    }

    async function api(path, opts = {}) {
      const res = await fetch(path, {
        ...opts,
        headers: { "Content-Type": "application/json", "X-Telegram-Init-Data": tg.initData, ...(opts.headers || {}) },
      });
      if (!res.ok) {
        let detail = L("error");
        try { detail = (await res.json()).detail || detail; } catch (e) {}
        throw new Error(detail);
      }
      return res.json();
    }

    document.querySelectorAll(".tab").forEach(btn => {
      btn.addEventListener("click", () => switchTab(btn.dataset.tab));
    });

    function switchTab(name) {
      document.querySelectorAll(".tab").forEach(b => b.classList.toggle("active", b.dataset.tab === name));
      document.querySelectorAll(".view").forEach(v => v.classList.toggle("active", v.id === "view-" + name));
      document.getElementById("cart-bar").hidden = !(name === "menu" && selectedPlanId);
    }

    function renderPlans() {
      document.getElementById("tab-plans").textContent = L("plans");
      document.getElementById("tab-menu").textContent = L("menu");
      const el = document.getElementById("plans-list");
      if (!plans.length) { el.innerHTML = `<p class="empty">${L("choose_plan")}</p>`; return; }
      el.innerHTML = plans.map(p => `
        <div class="plan-card ${p.id === selectedPlanId ? 'selected' : ''}">
          <h3>${p.name}</h3>
          <div class="sub">${p.meals_count} ${L("meals")} · ${p.duration_days} ${L("days")}</div>
          <div class="price">${p.price_krw.toLocaleString()}원</div>
          <div class="sub">${L("per_meal")}: ${p.price_per_meal.toLocaleString()}원</div>
          <button onclick="selectPlan(${p.id})">${p.id === selectedPlanId ? '✅' : L('choose')}</button>
        </div>
      `).join("");
    }

    async function selectPlan(planId) {
      selectedPlanId = planId;
      renderPlans();
      await loadCartAndMenu();
      switchTab("menu");
    }

    function currentPlan() { return plans.find(p => p.id === selectedPlanId); }

    async function loadCartAndMenu() {
      const [cartData, week1] = await Promise.all([api("/api/cart"), api("/api/menu")]);
      const nextStart = new Date(week1.week_start);
      nextStart.setDate(nextStart.getDate() + 7);
      const week2 = await api(`/api/menu?week_start=${nextStart.toISOString().slice(0, 10)}`);

      cartByDate = {};
      for (const item of cartData.items) cartByDate[item.delivery_date] = item.menu_item_id;
      menuDays = [...week1.days, ...week2.days].filter(d => d.items.length > 0);
      renderMenu();
    }

    function renderMenu() {
      const el = document.getElementById("menu-list");
      if (!selectedPlanId) { el.innerHTML = `<p class="empty">${L("choose_plan")}</p>`; return; }
      if (!menuDays.length) { el.innerHTML = `<p class="empty">${L("no_days")}</p>`; return; }

      el.innerHTML = menuDays.map(day => {
        const isDaySelected = day.date in cartByDate;
        return `
        <div class="day-card ${isDaySelected ? 'day-selected' : ''}">
          <h4>${isDaySelected ? '✅ ' : ''}${day.label} — ${day.date}</h4>
          <div class="dish-row">
            ${day.items.map(item => `
              <button class="dish-chip ${cartByDate[day.date] === item.menu_item_id ? 'selected' : ''}"
                      onclick="chooseDish('${day.date}', ${item.menu_item_id}, this)"
                      title="${cartByDate[day.date] === item.menu_item_id ? L('tap_to_remove') : ''}">${item.name}</button>
            `).join("")}
          </div>
        </div>
      `;
      }).join("");

      updateCartBar();
    }

    async function chooseDish(deliveryDate, menuItemId, btn) {
      const plan = currentPlan();
      const alreadySelectedHere = cartByDate[deliveryDate] === menuItemId;
      const isNewDay = !(deliveryDate in cartByDate);

      if (!alreadySelectedHere && isNewDay && Object.keys(cartByDate).length >= plan.meals_count) {
        showToast(L("limit_reached"));
        return;
      }

      btn.disabled = true;
      try {
        if (alreadySelectedHere) {
          await api("/api/cart", { method: "DELETE", body: JSON.stringify({ delivery_date: deliveryDate }) });
          delete cartByDate[deliveryDate];
        } else {
          await api("/api/cart", {
            method: "PUT",
            body: JSON.stringify({ plan_id: selectedPlanId, delivery_date: deliveryDate, menu_item_id: menuItemId, qty: 1 }),
          });
          cartByDate[deliveryDate] = menuItemId;
        }
        renderMenu();
      } catch (e) {
        showToast(e.message);
      } finally {
        btn.disabled = false;
      }
    }

    function updateCartBar() {
      const bar = document.getElementById("cart-bar");
      const plan = currentPlan();
      if (!plan) { bar.hidden = true; return; }
      const selectedCount = Object.keys(cartByDate).length;
      bar.hidden = false;
      document.getElementById("cart-progress").textContent = `${selectedCount}/${plan.meals_count} ${L('select_day')}`;
      document.getElementById("checkout-btn").textContent = L("checkout");
      document.getElementById("checkout-btn").disabled = selectedCount !== plan.meals_count;
    }

    document.getElementById("checkout-btn").addEventListener("click", async () => {
      try {
        const result = await api("/api/orders/checkout", { method: "POST", body: JSON.stringify({ plan_id: selectedPlanId }) });
        openPayOverlay(result);
        cartByDate = {};
        renderMenu();
      } catch (e) {
        showToast(e.message);
      }
    });

    function openPayOverlay(order) {
      document.getElementById("pay-heading").textContent = `${L("order_created")} — #${order.reference}`;
      let body = `${order.amount_krw.toLocaleString()}원\n\n`;
      if (order.instructions) {
        body += order.instructions;
      } else if (order.checkout_url) {
        body += `<a href="${order.checkout_url}" target="_blank">${L('checkout')}</a>`;
      }
      body += L("pay_instructions_sent");
      document.getElementById("pay-body").innerHTML = body.replace(/\n/g, "<br/>");
      document.getElementById("pay-overlay").hidden = false;
    }

    function closePayOverlay() {
      document.getElementById("pay-overlay").hidden = true;
    }

    async function loadSubscriptionBanner() {
      const data = await api("/api/orders/me/subscription");
      const banner = document.getElementById("status-banner");
      if (!data.subscription) { banner.hidden = true; return; }
      const s = data.subscription;
      banner.hidden = false;
      banner.innerHTML = `<b>${s.status}</b><br/>${s.meals_left}/${s.meals_total} · ${s.starts_on} → ${s.ends_on}`;
    }

    async function bootstrap() {
      const content = document.getElementById("app-content");
      try {
        const me = await api("/api/me");
        LANG = me.lang || "uz";
        if (!me.is_registered) {
          content.innerHTML = `<p class="empty" style="margin-top:60px;">${L("not_registered")}</p>`;
          return;
        }
        await loadSubscriptionBanner();
        plans = await api("/api/plans");
        renderPlans();
      } catch (e) {
        showToast(e.message);
      }
    }

    bootstrap();
  </script>
</body>
</html>
"""
