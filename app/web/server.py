import hashlib
import hmac
import json
import logging
from datetime import datetime
from urllib.parse import parse_qsl

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from telegram import Bot

from app.bot.services import (
    add_to_cart,
    cart_total,
    clear_cart,
    create_order_from_cart,
    get_cart_items,
    list_active_products,
    list_user_orders,
    remove_from_cart,
)
from app.config import BASE_URL, BOT_TOKEN, TOSS_CLIENT_KEY
from app.db import get_session
from app.i18n import DEFAULT_LANG, LANGUAGES, status_label, t, user_lang
from app.models import Order, OrderStatus, Payment, Product, User
from app.payments.toss import TossPaymentError, confirm_payment
from app.product_i18n import localized_product, product_emoji

logger = logging.getLogger(__name__)
app = FastAPI(title="Halal Food Ordering - Payment Backend")
notifier_bot = Bot(token=BOT_TOKEN)


def _order_name(order: Order) -> str:
    if len(order.items) == 1:
        return order.items[0].product_name
    return f"{order.items[0].product_name} +{len(order.items) - 1}"


def _validate_web_app_init_data(init_data: str) -> dict:
    """Verify Telegram WebApp initData signature and return the embedded user dict.

    See: https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
    """
    parsed = dict(parse_qsl(init_data, strict_parsing=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise ValueError("Hash yo'q")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed_hash, received_hash):
        raise ValueError("Imzo noto'g'ri")

    return json.loads(parsed["user"])


def _normalize_lang(lang: str) -> str:
    return lang if lang in LANGUAGES else DEFAULT_LANG


def _user_from_init_data(session, init_data: str) -> User:
    try:
        tg_user = _validate_web_app_init_data(init_data)
    except (ValueError, KeyError):
        raise HTTPException(status_code=403, detail="Telegram ma'lumotlari tasdiqlanmadi")
    user = session.query(User).filter_by(telegram_id=tg_user["id"]).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Avval botda /start buyrug'ini bering")
    return user


def _cart_payload(session, user: User, lang: str) -> dict:
    items = get_cart_items(session, user)
    out = []
    for ci in items:
        name, _ = localized_product(ci.product.name, ci.product.description, lang)
        out.append(
            {
                "product_id": ci.product_id,
                "name": name,
                "qty": ci.quantity,
                "unit_price": ci.product.price,
                "line_total": ci.product.price * ci.quantity,
            }
        )
    return {"items": out, "total": cart_total(items)}


@app.get("/menu", response_class=HTMLResponse)
def menu_page(lang: str = Query(DEFAULT_LANG)):
    lang = _normalize_lang(lang)

    with get_session() as session:
        products = list_active_products(session)
        rows = [(p.id, p.name, p.description, p.price, p.image_url) for p in products]

    if not rows:
        cards_html = f'<p class="empty">{t("no_items", lang)}</p>'
    else:
        add_label = t("btn_add_item", lang)
        cards = []
        for pid, name, description, price, image_url in rows:
            display_name, display_description = localized_product(name, description, lang)
            emoji = product_emoji(name)
            if image_url:
                media_html = (
                    f'<img src="{image_url}" alt="{display_name}" '
                    f'onerror="this.replaceWith(Object.assign(document.createElement(\'div\'),'
                    f'{{className:\'thumb-emoji\',textContent:\'{emoji}\'}}))" />'
                )
            else:
                media_html = f'<div class="thumb-emoji">{emoji}</div>'
            cards.append(f"""
    <div class="card">
      <div class="thumb">{media_html}</div>
      <div class="info">
        <h3>{display_name}</h3>
        <p>{display_description}</p>
        <div class="row">
          <span class="price">{price:,}원</span>
          <button onclick="addToCart({pid}, this)">{add_label}</button>
        </div>
      </div>
    </div>""")
        cards_html = '<div class="grid">' + "".join(cards) + "</div>"

    labels = {
        "tab_menu": t("tab_menu", lang),
        "tab_cart": t("tab_cart", lang),
        "tab_orders": t("tab_orders", lang),
        "cart_empty": t("cart_empty", lang),
        "total": t("total_label", lang),
        "checkout": t("btn_checkout", lang),
        "clear_cart": t("btn_clear_cart", lang),
        "no_orders": t("no_orders_yet", lang),
        "review_order": t("review_order_heading", lang),
        "pay_with_card": t("pay_with_card", lang),
        "resume_payment": t("resume_payment", lang),
        "item_added": t("item_added_toast", lang),
        "error": t("generic_error", lang),
        "status": {
            "pending_payment": status_label(OrderStatus.PENDING_PAYMENT, lang),
            "paid": status_label(OrderStatus.PAID, lang),
            "preparing": status_label(OrderStatus.PREPARING, lang),
            "ready": status_label(OrderStatus.READY, lang),
            "completed": status_label(OrderStatus.COMPLETED, lang),
            "cancelled": status_label(OrderStatus.CANCELLED, lang),
        },
    }
    i18n_json = json.dumps(labels, ensure_ascii=False)

    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{t('menu_title', lang)}</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://js.tosspayments.com/v1/payment"></script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0; padding: 0 16px 32px;
      background: var(--tg-theme-bg-color, #f5f6f8);
      color: var(--tg-theme-text-color, #111);
    }}
    header {{ margin: 16px 0; }}
    header h1 {{ margin: 0 0 4px; font-size: 20px; }}
    header p {{ margin: 0; font-size: 13px; opacity: .65; }}
    .empty {{ opacity: .7; text-align: center; margin-top: 40px; }}

    .tabbar {{
      position: sticky; top: 0; z-index: 5;
      display: flex; gap: 6px; padding: 10px 0;
      background: var(--tg-theme-bg-color, #f5f6f8);
      border-bottom: 1px solid rgba(128,128,128,.15);
      margin: 0 -16px 12px; padding-left: 16px; padding-right: 16px;
    }}
    .tab {{
      flex: 1; background: transparent; color: inherit;
      border: none; border-radius: 8px; padding: 8px 6px;
      font-size: 12.5px; opacity: .55;
    }}
    .tab.active {{ opacity: 1; background: var(--tg-theme-secondary-bg-color, #fff); font-weight: 600; }}

    .view {{ display: none; }}
    .view.active {{ display: block; }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      gap: 12px;
    }}
    .card {{
      background: var(--tg-theme-secondary-bg-color, #fff);
      border-radius: 14px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 1px 3px rgba(0,0,0,.08);
    }}
    .thumb {{
      width: 100%;
      aspect-ratio: 4 / 3;
      display: flex; align-items: center; justify-content: center;
      background: linear-gradient(135deg, #ffd76b, #ff9f43);
    }}
    .thumb img {{ width: 100%; height: 100%; object-fit: cover; }}
    .thumb-emoji {{ font-size: 42px; line-height: 1; }}
    .info {{ padding: 10px 12px 12px; display: flex; flex-direction: column; gap: 6px; flex: 1; }}
    .info h3 {{ margin: 0; font-size: 14px; }}
    .info p {{
      margin: 0; font-size: 12px; opacity: .65; line-height: 1.35;
      display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
      flex: 1;
    }}
    .row {{ display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-top: auto; }}
    .price {{ font-weight: 700; font-size: 13px; white-space: nowrap; }}

    button {{
      background: var(--tg-theme-button-color, #2ea6ff);
      color: var(--tg-theme-button-text-color, #fff);
      border: none; border-radius: 8px; padding: 7px 10px;
      font-size: 12px; white-space: nowrap;
    }}
    button:disabled {{ opacity: .5; }}
    .primary-btn {{ padding: 10px 16px; font-size: 13px; border-radius: 10px; }}
    .primary-btn.full {{ width: 100%; margin-top: 8px; }}
    .ghost-btn {{
      background: transparent; color: inherit; border: 1px solid rgba(128,128,128,.35);
      padding: 10px 16px; font-size: 13px; border-radius: 10px;
    }}
    .icon-btn {{ padding: 4px 8px; font-size: 13px; border-radius: 6px; }}

    .cart-line {{
      display: flex; justify-content: space-between; align-items: center;
      background: var(--tg-theme-secondary-bg-color, #fff);
      border-radius: 10px; padding: 10px 12px; margin-bottom: 8px;
    }}
    .cl-name {{ font-size: 13.5px; font-weight: 600; }}
    .cl-sub {{ font-size: 12px; opacity: .6; margin-top: 2px; }}
    .cl-actions {{ display: flex; align-items: center; gap: 10px; }}
    .cl-total {{ font-size: 13px; font-weight: 700; }}
    .cart-total-row {{
      display: flex; justify-content: space-between; font-size: 15px; font-weight: 700;
      padding: 12px 2px; border-top: 1px solid rgba(128,128,128,.2); margin-top: 4px;
    }}
    .cart-actions {{ display: flex; gap: 8px; margin-top: 10px; }}
    .cart-actions .ghost-btn {{ flex: 1; }}
    .cart-actions .primary-btn {{ flex: 2; }}

    .order-card {{
      background: var(--tg-theme-secondary-bg-color, #fff);
      border-radius: 12px; padding: 12px 14px; margin-bottom: 10px;
    }}
    .order-row {{ display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px; }}
    .order-id {{ font-weight: 700; }}
    .order-status {{ opacity: .8; }}

    .overlay {{
      position: fixed; inset: 0; background: rgba(0,0,0,.5);
      display: flex; align-items: center; justify-content: center; z-index: 20; padding: 20px;
    }}
    .overlay[hidden] {{ display: none; }}
    .overlay-card {{
      background: var(--tg-theme-bg-color, #fff); color: inherit;
      border-radius: 16px; padding: 20px; width: 100%; max-width: 320px;
      position: relative; text-align: center;
    }}
    .overlay-card h2 {{ margin: 0 0 12px; font-size: 16px; }}
    .overlay-card .price {{ font-size: 20px; display: block; margin: 8px 0 16px; }}
    .overlay-close {{
      position: absolute; top: 10px; right: 10px; background: transparent; color: inherit;
      opacity: .6; padding: 4px 8px;
    }}

    #toast {{
      position: fixed; bottom: 16px; left: 16px; right: 16px;
      background: #2ea6ff; color: #fff; text-align: center;
      padding: 10px; border-radius: 10px; display: none; font-size: 13px; z-index: 30;
    }}
  </style>
</head>
<body>
  <div class="tabbar">
    <button class="tab active" data-tab="menu">{t('tab_menu', lang)}</button>
    <button class="tab" data-tab="cart">{t('tab_cart', lang)}</button>
    <button class="tab" data-tab="orders">{t('tab_orders', lang)}</button>
  </div>

  <div id="view-menu" class="view active">
    <header>
      <h1>🍽️ {t('menu_title', lang)}</h1>
      <p>{t('menu_subtitle', lang)}</p>
    </header>
    {cards_html}
  </div>

  <div id="view-cart" class="view">
    <div id="cart-content" class="empty">…</div>
  </div>

  <div id="view-orders" class="view">
    <div id="orders-content" class="empty">…</div>
  </div>

  <div id="toast"></div>

  <div id="pay-overlay" class="overlay" hidden>
    <div class="overlay-card">
      <button class="overlay-close" onclick="closePayOverlay()">✕</button>
      <h2>{t('review_order_heading', lang)}</h2>
      <p id="pay-order-name"></p>
      <span class="price" id="pay-amount"></span>
      <button id="pay-button" class="primary-btn full"></button>
    </div>
  </div>

  <script>
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();

    const LANG = "{lang}";
    const TOSS_CLIENT_KEY = "{TOSS_CLIENT_KEY}";
    const BASE_URL = "{BASE_URL}";
    const I18N = {i18n_json};
    let lastOrders = [];

    function showToast(text) {{
      const toast = document.getElementById("toast");
      toast.textContent = text;
      toast.style.display = "block";
      setTimeout(() => {{ toast.style.display = "none"; }}, 1800);
    }}

    document.querySelectorAll(".tab").forEach(btn => {{
      btn.addEventListener("click", () => switchTab(btn.dataset.tab));
    }});

    function switchTab(tabName) {{
      document.querySelectorAll(".tab").forEach(b => b.classList.toggle("active", b.dataset.tab === tabName));
      document.querySelectorAll(".view").forEach(v => v.classList.toggle("active", v.id === "view-" + tabName));
      if (tabName === "cart") loadCart();
      if (tabName === "orders") loadOrders();
    }}

    async function apiPost(url, extra) {{
      const res = await fetch(url, {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify(Object.assign({{ init_data: tg.initData, lang: LANG }}, extra || {{}})),
      }});
      if (!res.ok) throw new Error("request failed: " + res.status);
      return res.json();
    }}

    async function addToCart(productId, btn) {{
      btn.disabled = true;
      try {{
        const res = await fetch("/menu/add", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ init_data: tg.initData, product_id: productId }}),
        }});
        if (!res.ok) throw new Error("request failed");
        if (tg.HapticFeedback) tg.HapticFeedback.notificationOccurred("success");
        showToast(I18N.item_added);
      }} catch (e) {{
        showToast(I18N.error);
      }} finally {{
        btn.disabled = false;
      }}
    }}

    function renderCart(data) {{
      const el = document.getElementById("cart-content");
      if (!data.items.length) {{
        el.innerHTML = `<p class="empty">${{I18N.cart_empty}}</p>`;
        return;
      }}
      const lines = data.items.map(it => `
        <div class="cart-line">
          <div>
            <div class="cl-name">${{it.name}}</div>
            <div class="cl-sub">${{it.unit_price.toLocaleString()}}원 × ${{it.qty}}</div>
          </div>
          <div class="cl-actions">
            <span class="cl-total">${{it.line_total.toLocaleString()}}원</span>
            <button class="icon-btn" onclick="removeFromCart(${{it.product_id}})">➖</button>
          </div>
        </div>
      `).join("");
      el.innerHTML = `
        ${{lines}}
        <div class="cart-total-row"><span>${{I18N.total}}</span><span>${{data.total.toLocaleString()}}원</span></div>
        <div class="cart-actions">
          <button class="ghost-btn" onclick="clearCartAll()">${{I18N.clear_cart}}</button>
          <button class="primary-btn" onclick="doCheckout()">${{I18N.checkout}}</button>
        </div>
      `;
    }}

    async function loadCart() {{
      const el = document.getElementById("cart-content");
      el.innerHTML = "…";
      try {{
        renderCart(await apiPost("/menu/cart"));
      }} catch (e) {{
        el.innerHTML = `<p class="empty">${{I18N.error}}</p>`;
      }}
    }}

    async function removeFromCart(productId) {{
      try {{ renderCart(await apiPost("/menu/cart/remove", {{ product_id: productId }})); }}
      catch (e) {{ showToast(I18N.error); }}
    }}

    async function clearCartAll() {{
      try {{ renderCart(await apiPost("/menu/cart/clear")); }}
      catch (e) {{ showToast(I18N.error); }}
    }}

    async function doCheckout() {{
      try {{
        const data = await apiPost("/menu/checkout");
        if (!data.ok) {{ showToast(I18N.cart_empty); return; }}
        openPayOverlay(data.order);
        loadCart();
      }} catch (e) {{ showToast(I18N.error); }}
    }}

    function renderOrders(data) {{
      lastOrders = data.orders;
      const el = document.getElementById("orders-content");
      if (!data.orders.length) {{
        el.innerHTML = `<p class="empty">${{I18N.no_orders}}</p>`;
        return;
      }}
      el.innerHTML = data.orders.map((o, idx) => `
        <div class="order-card">
          <div class="order-row"><span class="order-id">#${{o.toss_order_id}}</span><span class="order-status">${{o.status_label}}</span></div>
          <div class="order-row"><span>${{o.order_name}}</span><span>${{o.total_amount.toLocaleString()}}원</span></div>
          ${{o.pending ? `<button class="primary-btn full" onclick="resumePaymentByIndex(${{idx}})">${{I18N.resume_payment}}</button>` : ""}}
        </div>
      `).join("");
    }}

    async function loadOrders() {{
      const el = document.getElementById("orders-content");
      el.innerHTML = "…";
      try {{
        renderOrders(await apiPost("/menu/orders"));
      }} catch (e) {{
        el.innerHTML = `<p class="empty">${{I18N.error}}</p>`;
      }}
    }}

    function resumePaymentByIndex(idx) {{
      const o = lastOrders[idx];
      openPayOverlay({{
        toss_order_id: o.toss_order_id,
        amount: o.total_amount,
        order_name: o.order_name,
        customer_name: o.customer_name || "",
      }});
    }}

    function openPayOverlay(order) {{
      document.getElementById("pay-order-name").textContent = order.order_name;
      document.getElementById("pay-amount").textContent = order.amount.toLocaleString() + "원";
      const btn = document.getElementById("pay-button");
      btn.textContent = I18N.pay_with_card;
      btn.onclick = () => {{
        const tossPayments = TossPayments(TOSS_CLIENT_KEY);
        tossPayments.requestPayment("카드", {{
          amount: order.amount,
          orderId: order.toss_order_id,
          orderName: order.order_name,
          customerName: order.customer_name || "Customer",
          successUrl: BASE_URL + "/payments/success",
          failUrl: BASE_URL + "/payments/fail",
        }});
      }};
      document.getElementById("pay-overlay").hidden = false;
    }}

    function closePayOverlay() {{
      document.getElementById("pay-overlay").hidden = true;
    }}
  </script>
</body>
</html>
""")


@app.post("/menu/add")
def menu_add_to_cart(payload: dict = Body(...)):
    product_id = payload.get("product_id")
    with get_session() as session:
        user = _user_from_init_data(session, payload.get("init_data", ""))
        product = session.query(Product).filter_by(id=product_id, is_active=True).first()
        if product is None:
            raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
        add_to_cart(session, user, product_id)

    return {"ok": True}


@app.post("/menu/cart")
def menu_cart(payload: dict = Body(...)):
    lang = _normalize_lang(payload.get("lang", DEFAULT_LANG))
    with get_session() as session:
        user = _user_from_init_data(session, payload.get("init_data", ""))
        return _cart_payload(session, user, lang)


@app.post("/menu/cart/remove")
def menu_cart_remove(payload: dict = Body(...)):
    lang = _normalize_lang(payload.get("lang", DEFAULT_LANG))
    with get_session() as session:
        user = _user_from_init_data(session, payload.get("init_data", ""))
        remove_from_cart(session, user, payload.get("product_id"))
        session.flush()
        return _cart_payload(session, user, lang)


@app.post("/menu/cart/clear")
def menu_cart_clear(payload: dict = Body(...)):
    lang = _normalize_lang(payload.get("lang", DEFAULT_LANG))
    with get_session() as session:
        user = _user_from_init_data(session, payload.get("init_data", ""))
        clear_cart(session, user)
        session.flush()
        return _cart_payload(session, user, lang)


@app.post("/menu/checkout")
def menu_checkout(payload: dict = Body(...)):
    with get_session() as session:
        user = _user_from_init_data(session, payload.get("init_data", ""))
        order = create_order_from_cart(session, user)
        if order is None:
            return {"ok": False, "reason": "empty"}
        return {
            "ok": True,
            "order": {
                "toss_order_id": order.toss_order_id,
                "amount": order.total_amount,
                "order_name": _order_name(order),
                "customer_name": user.display_name,
            },
        }


@app.post("/menu/orders")
def menu_orders(payload: dict = Body(...)):
    lang = _normalize_lang(payload.get("lang", DEFAULT_LANG))
    with get_session() as session:
        user = _user_from_init_data(session, payload.get("init_data", ""))
        orders = list_user_orders(session, user)
        out = [
            {
                "toss_order_id": o.toss_order_id,
                "status": o.status,
                "status_label": status_label(o.status, lang),
                "total_amount": o.total_amount,
                "order_name": _order_name(o),
                "customer_name": user.display_name,
                "pending": o.status == OrderStatus.PENDING_PAYMENT,
            }
            for o in orders
        ]
        return {"orders": out}


@app.get("/checkout/{toss_order_id}", response_class=HTMLResponse)
def checkout_page(toss_order_id: str):
    with get_session() as session:
        order = session.query(Order).filter_by(toss_order_id=toss_order_id).first()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        lang = user_lang(order.user)
        if order.status != OrderStatus.PENDING_PAYMENT:
            return HTMLResponse(f"<h1>{t('order_already_status', lang, status=status_label(order.status, lang))}</h1>")

        order_name = _order_name(order)
        amount = order.total_amount
        customer_name = order.user.display_name

    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8" />
  <title>{t('checkout_title', lang, order_id=toss_order_id)}</title>
  <script src="https://js.tosspayments.com/v1/payment"></script>
</head>
<body>
  <h2>{t('checkout_heading', lang)}</h2>
  <p>{order_name} — {amount:,}원</p>
  <button id="pay-button">{t('pay_with_card', lang)}</button>
  <script>
    const tossPayments = TossPayments("{TOSS_CLIENT_KEY}");
    document.getElementById("pay-button").addEventListener("click", function () {{
      tossPayments.requestPayment("카드", {{
        amount: {amount},
        orderId: "{toss_order_id}",
        orderName: "{order_name}",
        customerName: "{customer_name}",
        successUrl: "{BASE_URL}/payments/success",
        failUrl: "{BASE_URL}/payments/fail",
      }});
    }});
  </script>
</body>
</html>
""")


def _done_page(message: str, lang: str, success: bool) -> str:
    emoji = "✅" if success else "❌"
    return f"""
<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{emoji}</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; min-height: 100vh;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      background: var(--tg-theme-bg-color, #f5f6f8); color: var(--tg-theme-text-color, #111);
      text-align: center; padding: 24px;
    }}
    .emoji {{ font-size: 56px; margin-bottom: 16px; }}
    p {{ font-size: 15px; line-height: 1.5; max-width: 320px; }}
    button {{
      margin-top: 20px; background: var(--tg-theme-button-color, #2ea6ff);
      color: var(--tg-theme-button-text-color, #fff); border: none;
      border-radius: 10px; padding: 12px 24px; font-size: 14px;
    }}
  </style>
</head>
<body>
  <div class="emoji">{emoji}</div>
  <p>{message}</p>
  <button onclick="closeOrBack()">{t('close_button', lang)}</button>
  <script>
    function closeOrBack() {{
      if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.close) {{
        window.Telegram.WebApp.close();
      }} else {{
        window.history.back();
      }}
    }}
  </script>
</body>
</html>
"""


@app.get("/payments/success", response_class=HTMLResponse)
async def payment_success(
    paymentKey: str = Query(...),
    orderId: str = Query(...),
    amount: int = Query(...),
):
    with get_session() as session:
        order = session.query(Order).filter_by(toss_order_id=orderId).first()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.total_amount != amount:
            raise HTTPException(status_code=400, detail="Amount mismatch")
        lang = user_lang(order.user)

        try:
            result = await confirm_payment(paymentKey, orderId, amount)
        except TossPaymentError as exc:
            logger.warning("Toss confirm failed for %s: %s", orderId, exc)
            return HTMLResponse(
                _done_page(t("payment_failed_page", lang, message=exc.message), lang, success=False),
                status_code=400,
            )

        order.status = OrderStatus.PAID
        payment = order.payment or Payment(order_id=order.id)
        payment.payment_key = paymentKey
        payment.method = result.get("method")
        payment.status = "approved"
        payment.approved_at = datetime.utcnow()
        session.add(payment)

        chat_id = order.user.chat_id
        toss_order_id = order.toss_order_id

    await notifier_bot.send_message(
        chat_id=chat_id,
        text=t("payment_confirmed_notify", lang, order_id=toss_order_id),
    )
    return HTMLResponse(_done_page(t("payment_success_page", lang), lang, success=True))


@app.get("/payments/fail", response_class=HTMLResponse)
def payment_fail(code: str = Query(""), message: str = Query(""), orderId: str = Query("")):
    logger.info("Payment failed for %s: %s %s", orderId, code, message)

    lang = DEFAULT_LANG
    if orderId:
        with get_session() as session:
            order = session.query(Order).filter_by(toss_order_id=orderId).first()
            if order is not None:
                lang = user_lang(order.user)

    full_message = f"{t('payment_failed_page', lang, message=message or code)} {t('payment_failed_retry_hint', lang)}"
    return HTMLResponse(_done_page(full_message, lang, success=False))
