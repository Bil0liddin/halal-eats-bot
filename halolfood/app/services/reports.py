"""Admin uchun statistika va hisobotlar (oshxona rejasi, kuryer ro'yxati)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Delivery, DeliveryStatus, Factory, MenuItem, Order, OrderStatus, Subscription, SubscriptionStatus, User


@dataclass
class Stats:
    """`/stats` buyrug'i uchun umumiy ko'rsatkichlar."""

    total_users: int
    registered_users: int
    active_subscriptions: int
    factories: int
    total_revenue_krw: int
    pending_payments: int

    @property
    def conversion_pct(self) -> float:
        """Ro'yxatdan o'tganlardan necha foizi to'lov qilganini hisoblaydi."""
        if self.registered_users == 0:
            return 0.0
        return round(self.active_subscriptions / self.registered_users * 100, 1)


async def get_stats(session: AsyncSession) -> Stats:
    """Botning umumiy holatini bir marta so'rov bilan hisoblaydi."""
    total_users = (await session.execute(select(func.count(User.id)))) .scalar_one()
    registered_users = (
        await session.execute(select(func.count(User.id)).where(User.registered_at.is_not(None)))
    ).scalar_one()
    active_subscriptions = (
        await session.execute(
            select(func.count(Subscription.id)).where(Subscription.status == SubscriptionStatus.ACTIVE)
        )
    ).scalar_one()
    factories = (await session.execute(select(func.count(Factory.id)).where(Factory.is_active.is_(True)))).scalar_one()
    total_revenue = (
        await session.execute(select(func.coalesce(func.sum(Order.amount_krw), 0)).where(Order.status == OrderStatus.PAID))
    ).scalar_one()
    pending_payments = (
        await session.execute(select(func.count(Order.id)).where(Order.status == OrderStatus.AWAITING_PAYMENT))
    ).scalar_one()

    return Stats(
        total_users=total_users,
        registered_users=registered_users,
        active_subscriptions=active_subscriptions,
        factories=factories,
        total_revenue_krw=int(total_revenue),
        pending_payments=pending_payments,
    )


@dataclass
class KitchenLine:
    """Oshxona rejasidagi bitta qator: fabrika -> taom -> soni."""

    factory_name: str
    dish_name: str
    count: int


async def get_kitchen_plan(session: AsyncSession, target_date: date, lang: str = "uz") -> list[KitchenLine]:
    """Berilgan kunga fabrika va taom bo'yicha guruhlangan ishlab chiqarish rejasini qaytaradi."""
    result = await session.execute(
        select(Factory.name, MenuItem, func.count(Delivery.id))
        .join(Factory, Delivery.factory_id == Factory.id)
        .join(MenuItem, Delivery.menu_item_id == MenuItem.id)
        .where(
            Delivery.delivery_date == target_date,
            Delivery.status.in_((DeliveryStatus.PLANNED, DeliveryStatus.CONFIRMED)),
        )
        .group_by(Factory.name, MenuItem.id)
        .order_by(Factory.name, MenuItem.id)
    )
    return [
        KitchenLine(factory_name=factory_name, dish_name=menu_item.name(lang), count=count)
        for factory_name, menu_item, count in result.all()
    ]


async def confirm_tomorrow_deliveries(session: AsyncSession, target_date: date) -> int:
    """Ertangi kun uchun barcha "planned" yetkazishlarni "confirmed" holatiga o'tkazadi (20:30 vazifasi)."""
    from sqlalchemy import update

    result = await session.execute(
        update(Delivery)
        .where(Delivery.delivery_date == target_date, Delivery.status == DeliveryStatus.PLANNED)
        .values(status=DeliveryStatus.CONFIRMED)
    )
    return result.rowcount or 0


@dataclass
class CourierRow:
    """Kuryer ro'yxatidagi bitta qator."""

    factory_name: str
    address: str
    delivery_window: str
    full_name: str
    phone: str
    delivery_note: str
    dish_name: str


async def get_courier_sheet(session: AsyncSession, target_date: date, lang: str = "uz") -> list[CourierRow]:
    """Berilgan kunga yetkazib berish uchun to'liq ro'yxatni (manzil, telefon, taom) qaytaradi."""
    result = await session.execute(
        select(Factory, User, MenuItem)
        .join(Factory, Delivery.factory_id == Factory.id)
        .join(User, Delivery.user_id == User.id)
        .join(MenuItem, Delivery.menu_item_id == MenuItem.id)
        .where(
            Delivery.delivery_date == target_date,
            Delivery.status.in_((DeliveryStatus.PLANNED, DeliveryStatus.CONFIRMED)),
        )
        .order_by(Factory.name, User.full_name)
    )
    rows = []
    for factory, user, menu_item in result.all():
        rows.append(
            CourierRow(
                factory_name=factory.name,
                address=factory.address,
                delivery_window=factory.delivery_window,
                full_name=user.full_name or "",
                phone=user.phone or "",
                delivery_note=user.delivery_note or "",
                dish_name=menu_item.name(lang),
            )
        )
    return rows
