# Halal Eats Korea — Telegram Ordering Bot

A Telegram bot for ordering halal food, with card payment via Toss Payments.

## Architecture

- **Bot** (`app/bot`): `python-telegram-bot`, long-polling. Handles browsing the menu, cart, checkout, order status, and an admin flow for managing products/orders.
- **Backend** (`app/web`): FastAPI. Serves the Toss checkout page and the payment success/fail callbacks. Confirms payments server-side and notifies the buyer on Telegram once paid.
- **DB**: SQLite via SQLAlchemy (swap `DATABASE_URL` for Postgres later without code changes).

Toss Payments' card checkout is browser-based (their JS SDK opens a hosted payment window), so the bot sends the buyer a "Pay Now" link to a page served by the FastAPI backend rather than handling payment in-chat.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
- `BOT_TOKEN`: from [@BotFather](https://t.me/BotFather)
- `ADMIN_TELEGRAM_IDS`: comma-separated Telegram user IDs allowed to run admin commands
- `TOSS_CLIENT_KEY` / `TOSS_SECRET_KEY`: from https://developers.tosspayments.com (test keys are free, no business registration needed for sandbox testing)
- `BASE_URL`: public URL of the FastAPI backend (see below)

Seed a sample menu:

```bash
python seed.py
```

## Running locally

You need **two processes** running at once:

```bash
# Terminal 1 — the Telegram bot
python -m app.bot.main

# Terminal 2 — the payment backend
uvicorn app.web.server:app --reload --port 8000
```

Toss needs to redirect the buyer's browser back to your `successUrl`/`failUrl`, so `BASE_URL` must be reachable from the public internet — `localhost` only works if you also open the checkout link from the same machine. For real testing, expose port 8000 with a tunnel:

```bash
ngrok http 8000
# then set BASE_URL in .env to the printed https://*.ngrok-free.app URL, and restart both processes
```

## Admin usage

From an account listed in `ADMIN_TELEGRAM_IDS`:
- `/addproduct Name|Price|Description` — add a menu item, e.g. `/addproduct Chicken Biryani|12000|Spicy halal chicken biryani`
- `/adminorders` — list active (paid/preparing/ready) orders with a button to advance each to its next status; the buyer gets a Telegram notification on every status change

## Order flow

1. Buyer taps **Browse Menu**, adds items to their cart
2. **Cart** → **Checkout** creates an order and returns a **Pay Now** link
3. Buyer pays by card on the Toss-hosted checkout page
4. Toss redirects to `/payments/success`, the backend confirms the payment server-side, marks the order `paid`, and messages the buyer
5. Admin advances the order through `preparing` → `ready` → `completed` via `/adminorders`, notifying the buyer at each step

## Notes / next steps

- Payment confirmation currently has no webhook signature verification beyond Toss's confirm-API round trip — fine for test keys, but review [Toss's webhook docs](https://docs.tosspayments.com/guides/webhook) before going live with real money.
- Single-vendor menu for now; multi-vendor would mean adding a `Vendor` model and scoping products/orders to it.
- No auth on `/adminorders` beyond the Telegram user ID allowlist — reasonable for an internal admin flow via bot, but don't expose the FastAPI backend's routes as a public admin panel without adding real auth.
