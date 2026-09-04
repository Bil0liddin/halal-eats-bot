import os

from dotenv import load_dotenv

load_dotenv()


def _split_ids(raw: str) -> set[int]:
    return {int(x) for x in raw.split(",") if x.strip()}


BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_TELEGRAM_IDS = _split_ids(os.getenv("ADMIN_TELEGRAM_IDS", ""))

TOSS_CLIENT_KEY = os.environ["TOSS_CLIENT_KEY"]
TOSS_SECRET_KEY = os.environ["TOSS_SECRET_KEY"]
TOSS_CONFIRM_URL = "https://api.tosspayments.com/v1/payments/confirm"

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./halal_orders.db")
