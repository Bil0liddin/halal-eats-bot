import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from telegram import Bot

from app.config import BASE_URL, BOT_TOKEN, TOSS_CLIENT_KEY
from app.db import get_session
from app.i18n import DEFAULT_LANG, status_label, t, user_lang
from app.models import Order, OrderStatus, Payment
from app.payments.toss import TossPaymentError, confirm_payment

logger = logging.getLogger(__name__)
app = FastAPI(title="Halal Food Ordering - Payment Backend")
notifier_bot = Bot(token=BOT_TOKEN)


def _order_name(order: Order) -> str:
    if len(order.items) == 1:
        return order.items[0].product_name
    return f"{order.items[0].product_name} +{len(order.items) - 1}"


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
            return HTMLResponse(f"<h1>{t('payment_failed_page', lang, message=exc.message)}</h1>", status_code=400)

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
    return HTMLResponse(f"<h1>{t('payment_success_page', lang)}</h1>")


@app.get("/payments/fail", response_class=HTMLResponse)
def payment_fail(code: str = Query(""), message: str = Query(""), orderId: str = Query("")):
    logger.info("Payment failed for %s: %s %s", orderId, code, message)

    lang = DEFAULT_LANG
    if orderId:
        with get_session() as session:
            order = session.query(Order).filter_by(toss_order_id=orderId).first()
            if order is not None:
                lang = user_lang(order.user)

    return HTMLResponse(
        f"<h1>{t('payment_failed_page', lang, message=message or code)}</h1>"
        f"<p>{t('payment_failed_retry_hint', lang)}</p>"
    )
