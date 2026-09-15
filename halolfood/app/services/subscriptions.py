"""Obuna tizimining asosiy biznes mantig'i.

Bu yerdagi funksiyalar HECH QACHON qaysi to'lov provayderi ishlatilayotganini
bilmaydi — ular faqat "to'landi" signalini oladi (confirm_payment orqali).
"""
from __future__ import annotations

import random
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    CartItem,
    Delivery,
    DeliveryStatus,
    MenuSlot,
    Order,
    OrderItem,
    OrderStatus,
    Plan,
    Subscription,
    SubscriptionStatus,
    User,
)
from app.i18n import t

# 0/O, 1/I/L, 8/B kabi bir-biriga o'xshab ketadigan belgilar ATAYLAB chiqarib
# tashlangan — mijoz kodni qo'lda ko'chirib yozganda adashmasin.
_REFERENCE_ALPHABET = "ACDEFGHJKMNPQRTUVWXY2345679"


class BusinessError(Exception):
    """Foydalanuvchiga to'g'ridan-to'g'ri ko'rsatilishi mumkin bo'lgan, kutilgan xatolik."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def _week_start_and_weekday(d: date) -> tuple[date, int]:
    """Sananing shu haftadagi dushanba kunini va hafta kuni raqamini (0=dushanba) qaytaradi."""
    weekday = d.weekday()
    week_start = d - timedelta(days=weekday)
    return week_start, weekday


def is_before_cutoff(delivery_date: date, *, now: datetime, cutoff_hour: int) -> bool:
    """Berilgan kun uchun hali o'zgartirish/bekor qilish mumkinligini tekshiradi.

    Cheklov: yetkazish kunidan OLDINGI kuni soat `cutoff_hour`:00 dan keyin
    o'sha kunga tegishli hech narsa o'zgartirib bo'lmaydi.
    """
    deadline = datetime.combine(delivery_date - timedelta(days=1), time(hour=cutoff_hour))
    deadline = deadline.replace(tzinfo=now.tzinfo)
    return now < deadline


def _random_code(length: int = 6) -> str:
    return "".join(random.choice(_REFERENCE_ALPHABET) for _ in range(length))


async def generate_unique_reference(session: AsyncSession) -> str:
    """"HL" + 6 ta belgidan iborat, bazada takrorlanmaydigan buyurtma kodini yaratadi."""
    for _ in range(10):
        candidate = "HL" + _random_code()
        result = await session.execute(select(Order.id).where(Order.reference == candidate))
        if result.scalar_one_or_none() is None:
            return candidate
    raise BusinessError("Noyob buyurtma kodini yaratib bo'lmadi, qayta urinib ko'ring.")


# ---------------------------------------------------------------------------
# Savat
# ---------------------------------------------------------------------------


async def set_cart_item(
    session: AsyncSession,
    user: User,
    *,
    plan_id: int,
    delivery_date: date,
    menu_item_id: int,
    qty: int = 1,
) -> CartItem:
    """Bitta kunga taom tanlaydi.

    QOIDA: kuniga bitta ovqat. Agar shu kunga avval boshqa tanlov qilingan
    bo'lsa, u QO'SHILMAYDI — ALMASHTIRILADI.
    """
    result = await session.execute(
        select(CartItem).where(CartItem.user_id == user.id, CartItem.delivery_date == delivery_date)
    )
    for existing in result.scalars().all():
        await session.delete(existing)
    await session.flush()

    item = CartItem(
        user_id=user.id,
        plan_id=plan_id,
        delivery_date=delivery_date,
        menu_item_id=menu_item_id,
        qty=qty,
    )
    session.add(item)
    await session.flush()
    return item


async def remove_cart_item(session: AsyncSession, user: User, delivery_date: date) -> None:
    """Berilgan kundagi savat tanlovini bekor qiladi."""
    result = await session.execute(
        select(CartItem).where(CartItem.user_id == user.id, CartItem.delivery_date == delivery_date)
    )
    for item in result.scalars().all():
        await session.delete(item)


async def get_cart_items(session: AsyncSession, user: User, plan_id: int | None = None) -> list[CartItem]:
    """Foydalanuvchi savatidagi barcha tanlovlarni (sana bo'yicha tartiblangan) qaytaradi."""
    stmt = select(CartItem).where(CartItem.user_id == user.id).order_by(CartItem.delivery_date)
    if plan_id is not None:
        stmt = stmt.where(CartItem.plan_id == plan_id)
    result = await session.execute(stmt)
    return list(result.scalars().unique().all())


async def clear_cart(session: AsyncSession, user: User) -> None:
    """Foydalanuvchi savatini butunlay tozalaydi."""
    result = await session.execute(select(CartItem).where(CartItem.user_id == user.id))
    for item in result.scalars().all():
        await session.delete(item)


async def validate_cart_against_menu(session: AsyncSession, items: list[CartItem], *, lang: str = "uz") -> None:
    """Savatdagi har bir tanlov o'sha kunning e'lon qilingan menyusida bor-yo'qligini tekshiradi."""
    for ci in items:
        week_start, weekday = _week_start_and_weekday(ci.delivery_date)
        result = await session.execute(
            select(MenuSlot).where(
                MenuSlot.week_start == week_start,
                MenuSlot.weekday == weekday,
                MenuSlot.menu_item_id == ci.menu_item_id,
                MenuSlot.is_published.is_(True),
            )
        )
        if result.scalar_one_or_none() is None:
            raise BusinessError(t("error_item_not_on_menu", lang, date=ci.delivery_date.isoformat()))


# ---------------------------------------------------------------------------
# Obuna va to'lov
# ---------------------------------------------------------------------------


async def get_active_subscription(session: AsyncSession, user: User) -> Subscription | None:
    """Foydalanuvchining hozirgi faol obunasini qaytaradi (bo'lmasa None)."""
    result = await session.execute(
        select(Subscription)
        .where(Subscription.user_id == user.id, Subscription.status == SubscriptionStatus.ACTIVE)
        .order_by(Subscription.ends_on.desc())
    )
    return result.scalars().first()


async def get_order_by_reference(session: AsyncSession, reference: str) -> Order | None:
    """Buyurtma kodi bo'yicha buyurtmani qaytaradi."""
    result = await session.execute(select(Order).where(Order.reference == reference))
    return result.scalar_one_or_none()


async def create_order_from_cart(session: AsyncSession, user: User, plan_id: int, *, lang: str = "uz") -> Order:
    """Savatdagi tanlovlardan yangi buyurtma (Order) yaratadi — hali TO'LOVSIZ.

    Tekshiruvlar tartibi: ro'yxatdan to'liq o'tganmi (fabrikasi bo'lishi
    SHART — aks holda to'lov tasdiqlanganda Delivery yozuvi yaratib
    bo'lmaydi) -> savat bo'shmi -> tanlovlar soni reja bilan mos kelyaptimi
    -> har bir tanlov haqiqatan ham o'sha kunning menyusidami.
    """
    if not user.is_registered:
        raise BusinessError(t("error_not_registered", lang))

    plan = await session.get(Plan, plan_id)
    if plan is None or not plan.is_active:
        raise BusinessError(t("error_generic", lang))

    items = await get_cart_items(session, user, plan_id=plan_id)
    if not items:
        raise BusinessError(t("error_cart_empty", lang))

    if len(items) != plan.meals_count:
        raise BusinessError(t("error_cart_wrong_count", lang, selected=len(items), required=plan.meals_count))

    await validate_cart_against_menu(session, items, lang=lang)

    # Agar foydalanuvchida faol obuna bo'lsa, yangisi ESKISI TUGAGAN KUNNING
    # ERTASIGA boshlanadi — bir necha obuna bir vaqtda ishlamaydi.
    active_sub = await get_active_subscription(session, user)
    if active_sub is not None:
        starts_on = active_sub.ends_on + timedelta(days=1)
    else:
        starts_on = min(ci.delivery_date for ci in items)
    ends_on = starts_on + timedelta(days=plan.duration_days - 1)

    reference = await generate_unique_reference(session)
    order = Order(
        reference=reference,
        user_id=user.id,
        plan_id=plan.id,
        amount_krw=plan.price_krw,
        status=OrderStatus.AWAITING_PAYMENT,
        starts_on=starts_on,
        ends_on=ends_on,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=48),
    )
    session.add(order)
    await session.flush()

    for ci in items:
        session.add(
            OrderItem(
                order_id=order.id,
                delivery_date=ci.delivery_date,
                menu_item_id=ci.menu_item_id,
                qty=ci.qty,
                # Nom va narx shu yerda "suratga olinadi" — kelajakda menyu
                # o'zgarsa ham bu buyurtma tarixi o'zgarmaydi.
                item_name_snapshot=ci.menu_item.name(lang),
                unit_price_krw=plan.price_per_meal,
            )
        )
    await session.flush()
    return order


async def generate_deliveries(session: AsyncSession, subscription: Subscription, order_id: int) -> None:
    """Buyurtmadagi har bir kun uchun Delivery (yetkazib berish) yozuvini yaratadi."""
    result = await session.execute(select(OrderItem).where(OrderItem.order_id == order_id))
    order_items = result.scalars().all()

    user = await session.get(User, subscription.user_id)
    for oi in order_items:
        session.add(
            Delivery(
                subscription_id=subscription.id,
                user_id=subscription.user_id,
                factory_id=user.factory_id,
                delivery_date=oi.delivery_date,
                menu_item_id=oi.menu_item_id,
                status=DeliveryStatus.PLANNED,
            )
        )
    await session.flush()


async def confirm_payment(
    session: AsyncSession,
    order: Order,
    *,
    provider_payment_id: str | None = None,
    lang: str = "uz",
) -> Subscription:
    """To'lovni tasdiqlaydi: Order'ni Subscription'ga aylantiradi.

    ENG MUHIM QOIDA: bu funksiya IDEMPOTENT bo'lishi shart. To'lov
    provayderlarining webhooklari deyarli har doim BIR NECHA MARTA keladi —
    agar buyurtma ALLAQACHON to'langan bo'lsa, mavjud obunani qaytaramiz,
    hech qachon ikkinchi marta yangi obuna YARATMAYMIZ.
    """
    if order.status == OrderStatus.PAID:
        result = await session.execute(select(Subscription).where(Subscription.order_id == order.id))
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing
        raise BusinessError(t("error_generic", lang))  # nazariy jihatdan bo'lmasligi kerak holat

    if order.status in (OrderStatus.CANCELLED, OrderStatus.REFUNDED, OrderStatus.EXPIRED):
        raise BusinessError(t("error_order_not_payable", lang))

    order.status = OrderStatus.PAID
    order.paid_at = datetime.now(timezone.utc)
    if provider_payment_id:
        order.provider_payment_id = provider_payment_id
    await session.flush()

    plan = await session.get(Plan, order.plan_id)
    subscription = Subscription(
        user_id=order.user_id,
        plan_id=order.plan_id,
        order_id=order.id,
        starts_on=order.starts_on,
        ends_on=order.ends_on,
        meals_total=plan.meals_count,
        meals_used=0,
        status=SubscriptionStatus.ACTIVE,
    )
    session.add(subscription)
    await session.flush()

    await generate_deliveries(session, subscription, order.id)

    user = await session.get(User, order.user_id)
    await clear_cart(session, user)

    return subscription


async def mark_delivered(session: AsyncSession, delivery: Delivery) -> None:
    """Yetkazib berish amalga oshirilganini belgilaydi va obunadagi ishlatilgan ovqat sonini oshiradi."""
    if delivery.status == DeliveryStatus.DELIVERED:
        return  # allaqachon belgilangan — ikki marta hisoblanmasin
    delivery.status = DeliveryStatus.DELIVERED
    subscription = await session.get(Subscription, delivery.subscription_id)
    subscription.meals_used += 1
    await session.flush()


async def skip_delivery(
    session: AsyncSession,
    delivery: Delivery,
    *,
    now: datetime,
    cutoff_hour: int,
    lang: str = "uz",
) -> None:
    """Bitta kunlik yetkazishni bekor qiladi.

    Cheklov: yetkazish kunidan OLDINGI kuni soat `cutoff_hour`:00 dan keyin
    bekor qilib bo'lmaydi. Bekor qilingan ovqat YO'QOTILMAYDI — obuna muddati
    bir kunga uzaytiriladi.
    """
    if not is_before_cutoff(delivery.delivery_date, now=now, cutoff_hour=cutoff_hour):
        raise BusinessError(t("skip_too_late", lang, cutoff=cutoff_hour))

    if delivery.status != DeliveryStatus.PLANNED:
        raise BusinessError(t("error_generic", lang))

    delivery.status = DeliveryStatus.SKIPPED

    subscription = await session.get(Subscription, delivery.subscription_id)
    subscription.ends_on = subscription.ends_on + timedelta(days=1)

    await session.flush()


async def change_delivery_meal(
    session: AsyncSession,
    delivery: Delivery,
    menu_item_id: int,
    *,
    now: datetime,
    cutoff_hour: int,
    lang: str = "uz",
) -> None:
    """Faol obunadagi bitta kunning ovqatini almashtiradi ("Mening obunam" bo'limidan, to'lovdan KEYIN).

    Kesim vaqti va yangi ovqatning o'sha kun menyusida borligi tekshiriladi —
    xuddi `set_cart_item` + `validate_cart_against_menu` kabi, faqat bu safar
    savat emas, ALLAQACHON to'langan Delivery yozuvi ustida ishlaydi.
    """
    if not is_before_cutoff(delivery.delivery_date, now=now, cutoff_hour=cutoff_hour):
        raise BusinessError(t("skip_too_late", lang, cutoff=cutoff_hour))

    if delivery.status != DeliveryStatus.PLANNED:
        raise BusinessError(t("error_generic", lang))

    week_start, weekday = _week_start_and_weekday(delivery.delivery_date)
    result = await session.execute(
        select(MenuSlot).where(
            MenuSlot.week_start == week_start,
            MenuSlot.weekday == weekday,
            MenuSlot.menu_item_id == menu_item_id,
            MenuSlot.is_published.is_(True),
        )
    )
    if result.scalar_one_or_none() is None:
        raise BusinessError(t("error_item_not_on_menu", lang, date=delivery.delivery_date.isoformat()))

    delivery.menu_item_id = menu_item_id
    await session.flush()


async def cancel_subscription(session: AsyncSession, subscription: Subscription, *, today: date) -> None:
    """Obunani butunlay bekor qiladi.

    Kelajakdagi, hali yetkazilmagan kunlar ham "skipped" qilinadi — aks holda
    oshxona rejasi va kuryer ro'yxati bekor qilingan obuna uchun ham
    ovqat tayyorlashni davom ettirar edi.
    """
    subscription.status = SubscriptionStatus.CANCELLED

    result = await session.execute(
        select(Delivery).where(
            Delivery.subscription_id == subscription.id,
            Delivery.status.in_((DeliveryStatus.PLANNED, DeliveryStatus.CONFIRMED)),
            Delivery.delivery_date >= today,
        )
    )
    for delivery in result.scalars().all():
        delivery.status = DeliveryStatus.SKIPPED

    await session.flush()


# ---------------------------------------------------------------------------
# Rejalashtirilgan vazifalar uchun ommaviy (bulk) yangilashlar
# ---------------------------------------------------------------------------


async def expire_stale_orders(session: AsyncSession, *, now: datetime) -> int:
    """Muddati (48 soat) o'tgan, hali to'lanmagan buyurtmalarni "expired" qiladi."""
    result = await session.execute(
        update(Order)
        .where(Order.status == OrderStatus.AWAITING_PAYMENT, Order.expires_at < now)
        .values(status=OrderStatus.EXPIRED)
    )
    return result.rowcount or 0


async def expire_finished_subscriptions(session: AsyncSession, *, today: date) -> int:
    """Amal qilish muddati tugagan faol obunalarni "expired" holatiga o'tkazadi."""
    result = await session.execute(
        update(Subscription)
        .where(Subscription.status == SubscriptionStatus.ACTIVE, Subscription.ends_on < today)
        .values(status=SubscriptionStatus.EXPIRED)
    )
    return result.rowcount or 0
