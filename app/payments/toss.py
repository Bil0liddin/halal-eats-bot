import base64

import httpx

from app.config import TOSS_CONFIRM_URL, TOSS_SECRET_KEY


def _auth_header() -> str:
    token = base64.b64encode(f"{TOSS_SECRET_KEY}:".encode()).decode()
    return f"Basic {token}"


async def confirm_payment(payment_key: str, order_id: str, amount: int) -> dict:
    """Server-to-server confirmation call, required to finalize a Toss card payment.

    See: https://docs.tosspayments.com/reference#payments-confirm
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOSS_CONFIRM_URL,
            json={"paymentKey": payment_key, "orderId": order_id, "amount": amount},
            headers={
                "Authorization": _auth_header(),
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )
    body = response.json()
    if response.status_code >= 400:
        raise TossPaymentError(body.get("code", "UNKNOWN_ERROR"), body.get("message", "Toss confirm failed"))
    return body


class TossPaymentError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
