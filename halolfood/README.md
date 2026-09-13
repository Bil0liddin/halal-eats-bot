# Halol Food — Obuna asosidagi tushlik yetkazib berish boti

Janubiy Koreyadagi fabrikalarda ishlaydigan o'zbek ishchilar uchun halol
tushlikni haftalik yoki oylik obuna asosida yetkazib berish tizimi.

Tizim ikki qismdan iborat:

- **Telegram bot** (aiogram 3) — ro'yxatdan o'tish, obuna holatini ko'rish,
  jadvalni boshqarish, admin buyruqlari.
- **Mini App API** (FastAPI) — Telegram Mini App (allaqachon mavjud frontend)
  uchun menyu, savat va buyurtma endpointlari.

To'lov tizimi hozircha ulanmagan — buning o'rniga **qo'lda bank o'tkazmasi**
provayderi ishlaydi (pastdagi "To'lov provayderini keyinroq qo'shish"
bo'limiga qarang).

---

## 1. O'rnatish

### Talablar

- Python 3.11+
- PostgreSQL (yoki lokal test uchun SQLite — pastga qarang)
- Redis (ixtiyoriy — bo'lmasa bot avtomatik xotiradagi saqlashga o'tadi)

### Qadamlar

```bash
# 1. Virtual muhit yaratish
python -m venv .venv
.venv\Scripts\activate          # Windows
# yoki: source .venv/bin/activate   # Linux/Mac

# 2. Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 3. .env faylini sozlash
cp .env.example .env
# .env faylini oching va BOT_TOKEN, WEBAPP_URL, ADMIN_IDS'ni to'ldiring

# 4. Postgres va Redis'ni ishga tushirish (Docker orqali eng oson yo'l)
docker compose up -d

# 5. Jadvallarni yaratish va namuna ma'lumotlar bilan to'ldirish
python seed.py

# 6. Botni ishga tushirish
python -m app.bot.main

# 7. (Alohida terminalda) Mini App API'ni ishga tushirish
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Tezkor tekshirish (PostgreSQL'siz)

Agar hali Postgres o'rnatmagan bo'lsangiz, `.env` faylida quyidagini yozib,
tizimni SQLite bilan sinab ko'rishingiz mumkin:

```
DATABASE_URL=sqlite+aiosqlite:///./halolfood.db
```

Bu FAQAT sinov uchun — asosiy ishlab chiqarishda PostgreSQL tavsiya etiladi.

---

## 2. Fayl tuzilishi

```
halolfood/
├── app/
│   ├── config.py              — .env'dan o'qiladigan barcha sozlamalar
│   ├── db/
│   │   ├── base.py            — Base klass va TimestampMixin
│   │   ├── models.py          — barcha jadvallar (User, Order, Subscription...)
│   │   └── session.py         — async engine va sessiya boshqaruvi
│   ├── i18n/__init__.py       — 3 tildagi (uz/ru/ko) barcha matnlar
│   ├── bot/
│   │   ├── main.py            — botni ishga tushirish
│   │   ├── keyboards.py       — barcha klaviaturalar
│   │   ├── states.py          — FSM holatlari
│   │   ├── middlewares.py     — DB sessiya, foydalanuvchi, xato ushlash
│   │   ├── notify.py          — xavfsiz xabar yuborish (bloklash, flood-limit)
│   │   └── handlers/
│   │       ├── start.py       — ro'yxatdan o'tish
│   │       ├── subscription.py— obuna, jadval, "to'ladim" tugmasi
│   │       ├── profile.py     — profil, til o'zgartirish
│   │       └── admin.py       — /stats, /kitchen, /sheet, /pending, /ok
│   ├── api/
│   │   ├── main.py            — FastAPI ilova, CORS, webhook
│   │   ├── auth.py            — initData imzosini tekshirish (ENG MUHIM FAYL)
│   │   └── routes/
│   │       ├── menu.py        — GET /plans, GET /menu
│   │       ├── cart.py        — GET/PUT/DELETE /cart
│   │       └── orders.py      — POST /orders/checkout, GET /orders/{ref}
│   ├── services/
│   │   ├── users.py           — foydalanuvchi va fabrika amallari
│   │   ├── subscriptions.py   — ASOSIY BIZNES MANTIQ
│   │   ├── reports.py         — statistika, oshxona rejasi, kuryer ro'yxati
│   │   └── payments/
│   │       ├── base.py        — TO'LOV ABSTRAKSIYASI (eng muhim fayl)
│   │       └── manual.py      — qo'lda bank o'tkazmasi
│   └── scheduler/jobs.py      — 4 ta rejalashtirilgan vazifa
├── tests/
│   ├── test_business_logic.py — 12 ta sinov, SQLite, Telegram shart emas
│   └── test_miniapp_auth.py   — 5 ta sinov, imzo tekshiruvi
├── seed.py                    — jadvallarni yaratish + namuna ma'lumotlar
├── requirements.txt
├── docker-compose.yml         — Postgres + Redis
└── .env.example
```

---

## 3. Asosiy oqim (ASCII diagramma)

```
Foydalanuvchi                    Bot                         Mini App API
     |                            |                                |
     |-- /start ----------------->|                                |
     |<-- til tanlash -----------|                                 |
     |-- til, ism, telefon,      |                                 |
     |   fabrika, joylashuv ---->|                                 |
     |<-- ro'yxatdan o'tildi ----|                                 |
     |                            |                                |
     |-- "Menyu va obuna" ------->| (Mini App ochiladi)            |
     |------------------------------------------------------------>|
     |<-- rejalar, menyu --------------------------------------------|
     |-- savatga taom qo'shish -------------------------------------->|
     |-- checkout -------------------------------------------------->|
     |                            |    Order yaratiladi (draft)     |
     |                            |    PaymentProvider.create_payment|
     |<-- to'lov ko'rsatmasi -----|<-------------------------------|
     |-- pul o'tkazadi ---------->| (bank orqali, botdan tashqarida)|
     |-- "To'ladim" bosadi ------>|                                |
     |                            |-- adminga xabar --------------->|
     |                       Admin -- /ok KOD yoki tugma ---------->|
     |                            |    confirm_payment()            |
     |                            |    Order -> Subscription        |
     |                            |    Delivery'lar yaratiladi      |
     |<-- "Obuna faollashtirildi"-|                                |
     |                            |                                |
     |   [har kuni 19:00] <-- "Ertaga X yetkaziladi" eslatmasi     |
     |   [har kuni 20:30] --      oshxona rejasi adminlarga        |
     |   [har kuni 09:00] <-- obuna tugash eslatmasi (kerak bo'lsa)|
     |   [har kuni 03:00] --      muddati o'tganlar avtomatik yopiladi
```

**Muhim arxitektura qarori**: `Order` (xarid niyati) va `Subscription`
(to'langan, faol obuna) — ALOHIDA jadvallar. To'lov tasdiqlanganda Order
Subscription'ga aylanadi. Shu tufayli to'lov provayderi almashtirilganda
biznes mantiqqa (jadval, eslatmalar, kuryer ro'yxati) HECH TEGILMAYDI — u
faqat "to'landi" signalini oladi, pulni KIM yig'gani haqida bilmaydi.

---

## 4. To'lov provayderini keyinroq qo'shish

Hozir faqat "qo'lda bank o'tkazmasi" (`manual`) provayderi bor. Haqiqiy
to'lov tizimini (Toss, KakaoPay, PortOne va h.k.) ulash uchun UCHTA qadam
kifoya:

**1-qadam**: `app/services/payments/toss.py` (yoki boshqa nom) faylini yozing:

```python
"""Toss Payments orqali karta bilan to'lash."""
from __future__ import annotations

from app.services.payments.base import PaymentIntent, PaymentProvider, PaymentResult, register_provider


@register_provider
class TossPayments(PaymentProvider):
    name = "toss"
    auto_confirm = True  # webhook to'lovni o'zi tasdiqlaydi

    async def create_payment(self, *, reference, amount_krw, description, lang="uz", **extra) -> PaymentIntent:
        # Toss API'siga so'rov yuborib, checkout_url oling
        checkout_url = await _create_toss_checkout(reference, amount_krw, description)
        return PaymentIntent(provider=self.name, checkout_url=checkout_url, provider_payment_id=reference)

    async def verify_callback(self, payload: dict) -> PaymentResult:
        # Toss webhook imzosini tekshiring, keyin natijani qaytaring
        is_valid, order_ref, amount = _verify_toss_signature(payload)
        return PaymentResult(success=is_valid, order_reference=order_ref, amount_krw=amount)
```

**2-qadam**: `app/services/payments/__init__.py` fayliga bitta qator qo'shing:

```python
from app.services.payments import toss  # noqa: F401
```

**3-qadam**: `.env` faylida:

```
PAYMENT_PROVIDER=toss
```

Tamom. `app/bot/handlers/subscription.py`, `app/services/subscriptions.py` —
bularning HECH BIRIGA tegilmaydi, chunki ular provayder nomini umuman
bilishmaydi, faqat `get_provider()` orqali mavhum interfeys bilan ishlashadi.

---

## 5. Admin buyruqlari

| Buyruq | Vazifasi |
|---|---|
| `/stats` | Umumiy statistika: foydalanuvchilar, faol obunalar, konversiya, tushum |
| `/kitchen` | Ertangi kun uchun oshxona ishlab chiqarish rejasi (fabrika → taom → soni) |
| `/kitchen_today` | Bugungi kun uchun xuddi shunday reja |
| `/sheet` | Ertangi kuryer ro'yxati — CSV fayl (Excel'da to'g'ri ochilishi uchun UTF-8-SIG) |
| `/pending` | To'lov kutayotgan barcha buyurtmalar ro'yxati |
| `/ok KOD` | Buyurtmani qo'lda tasdiqlaydi (masalan `/ok HL7X9K2M`) |

Inline tugmalar: har bir "To'ladim" xabaridagi ✅/❌ tugmalari xuddi
`/ok`/rad etish bilan bir xil ishlaydi.

---

## 6. Rejalashtirilgan vazifalar (Asia/Seoul vaqti)

| Vaqt | Vazifa |
|---|---|
| 19:00 | Ertangi ovqat haqida eslatma (BroadcastLog orqali bir martalik) |
| 20:30 | Barcha "planned" yetkazishlarni "confirmed" qiladi + oshxona rejasini adminlarga yuboradi |
| 09:00 | Obunasi tez orada tugaydiganlarga yangilash eslatmasi (bir marta) |
| 03:00 | Muddati o'tgan buyurtma va obunalarni avtomatik yopadi |

---

## 7. Mini App'dan API'ni chaqirish (JavaScript)

Mini App HAR BIR so'rovga Telegram'ning `initData`sini `X-Telegram-Init-Data`
sarlavhasi (header) orqali yuborishi SHART — aks holda so'rov 401 xatosi bilan
rad etiladi:

```javascript
const tg = window.Telegram.WebApp;

async function apiRequest(path, options = {}) {
  const response = await fetch(`https://your-api-domain.example.com/api${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Telegram-Init-Data": tg.initData,
      ...(options.headers || {}),
    },
  });
  if (!response.ok) {
    throw new Error(`API xatosi: ${response.status}`);
  }
  return response.json();
}

// Misollar:
const plans = await apiRequest("/plans");
const menu = await apiRequest("/menu?week_start=2026-09-14");

await apiRequest("/cart", {
  method: "PUT",
  body: JSON.stringify({ plan_id: 1, delivery_date: "2026-09-14", menu_item_id: 3, qty: 1 }),
});

const checkout = await apiRequest("/orders/checkout", {
  method: "POST",
  body: JSON.stringify({ plan_id: 1 }),
});
// checkout.instructions yoki checkout.checkout_url'ni foydalanuvchiga ko'rsating
```

---

## 8. Testlarni ishga tushirish

Ikkala test fayli ham **pytest talab qilmaydi**, PostgreSQL yoki Telegramga
ulanish shart emas — ular ichki ravishda vaqtinchalik SQLite baza yaratadi:

```bash
python tests/test_business_logic.py
python tests/test_miniapp_auth.py
```

---

## 9. Ishga tushirishdan oldingi tekshiruv ro'yxati (pre-launch checklist)

- [ ] `.env` faylida haqiqiy `BOT_TOKEN` va `WEBAPP_URL` to'ldirilgan
- [ ] `ADMIN_IDS`ga kamida bitta haqiqiy Telegram ID kiritilgan
- [ ] PostgreSQL ishga tushirilgan va `DATABASE_URL` to'g'ri sozlangan
- [ ] Redis ishga tushirilgan (ixtiyoriy, lekin production uchun tavsiya etiladi)
- [ ] `MANUAL_BANK_NAME`, `MANUAL_BANK_ACCOUNT`, `MANUAL_BANK_HOLDER` — haqiqiy bank ma'lumotlari bilan to'ldirilgan
- [ ] `python seed.py` ishga tushirilib, kamida bitta fabrika, reja va taom qo'shilgan
- [ ] `python tests/test_business_logic.py` va `python tests/test_miniapp_auth.py` xatosiz o'tadi
- [ ] Mini App frontend `WEBAPP_URL` orqali ochilib, API bilan bog'lana olishi tekshirilgan
- [ ] Bot va API ikkalasi ham serverda doimiy ishlaydigan qilib sozlangan (masalan systemd, Docker, yoki PM2)
- [ ] Haqiqiy pul bilan sinov: kamida bitta test foydalanuvchi bilan to'liq oqim (ro'yxatdan o'tish → obuna → to'lov → admin tasdig'i → yetkazib berish) qo'lda tekshirilgan
