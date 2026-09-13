"""Barcha ma'lumotlar bazasi jadvallari shu yerda.

Eng muhim arxitektura qarori: Order (buyurtma niyati) va Subscription (to'langan,
faol obuna) — ALOHIDA jadvallar. To'lov tasdiqlanganda Order Subscription'ga
aylanadi. Shu tufayli to'lov provayderi almashtirilganda biznes mantiqqa
tegilmaydi — u faqat "to'landi" signalini oladi, pulni KIM yig'gani haqida
umuman bilmaydi.
"""
from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import BigInteger
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


# ---------------------------------------------------------------------------
# Enumlar — barchasi native_enum=False bilan saqlanadi (VARCHAR sifatida),
# shunda SQLite (testlar) va PostgreSQL (prod) ikkalasida ham bir xil ishlaydi
# va kelajakda yangi qiymat qo'shish uchun DB migratsiyasi shart emas.
# ---------------------------------------------------------------------------


class Lang(str, enum.Enum):
    UZ = "uz"
    RU = "ru"
    KO = "ko"


class PlanPeriod(str, enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class OrderStatus(str, enum.Enum):
    DRAFT = "draft"
    AWAITING_PAYMENT = "awaiting_payment"
    PAID = "paid"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REFUNDED = "refunded"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class DeliveryStatus(str, enum.Enum):
    PLANNED = "planned"
    CONFIRMED = "confirmed"
    DELIVERED = "delivered"
    SKIPPED = "skipped"
    FAILED = "failed"


class MealCategory(str, enum.Enum):
    MAIN = "main"
    SOUP = "soup"
    SIDE = "side"
    BREAD = "bread"
    DRINK = "drink"


# ---------------------------------------------------------------------------
# Jadvallar
# ---------------------------------------------------------------------------


class User(Base, TimestampMixin):
    """Botdan foydalanuvchi — fabrikada ishlovchi mijoz."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    lang: Mapped[Lang] = mapped_column(SAEnum(Lang, native_enum=False), default=Lang.UZ)
    factory_id: Mapped[int | None] = mapped_column(ForeignKey("factories.id"), nullable=True)
    delivery_note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    registered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    factory: Mapped["Factory | None"] = relationship(back_populates="users")

    @property
    def is_registered(self) -> bool:
        """To'liq ro'yxatdan o'tgan hisoblanadi: ism, telefon va fabrika to'ldirilgan bo'lsa."""
        return bool(self.full_name and self.phone and self.factory_id)


class Factory(Base, TimestampMixin):
    """Fabrika — yetkazib berish nuqtasi."""

    __tablename__ = "factories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    city: Mapped[str] = mapped_column(String(64))
    address: Mapped[str] = mapped_column(String(255))
    delivery_window: Mapped[str] = mapped_column(String(32), default="12:00-12:30")
    min_orders: Mapped[int] = mapped_column(Integer, default=5)  # yangi nuqtani ochish uchun minimal buyurtma soni
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    users: Mapped[list["User"]] = relationship(back_populates="factory")


class Plan(Base, TimestampMixin):
    """Obuna rejasi — haftalik yoki oylik."""

    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name_uz: Mapped[str] = mapped_column(String(128))
    name_ru: Mapped[str] = mapped_column(String(128))
    name_ko: Mapped[str] = mapped_column(String(128))
    period: Mapped[PlanPeriod] = mapped_column(SAEnum(PlanPeriod, native_enum=False))
    meals_count: Mapped[int] = mapped_column(Integer)
    duration_days: Mapped[int] = mapped_column(Integer)
    price_krw: Mapped[int] = mapped_column(Integer)  # pul — HAR DOIM Integer (won), float ISHLATILMAYDI
    cost_krw: Mapped[int] = mapped_column(Integer, default=0)  # tannarx — marja tahlili uchun kerak
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def name(self, lang: str) -> str:
        """Berilgan tildagi nomni qaytaradi."""
        return {"uz": self.name_uz, "ru": self.name_ru, "ko": self.name_ko}.get(lang, self.name_uz)

    @property
    def price_per_meal(self) -> int:
        """Bitta ovqatning taxminiy narxi (yaxlitlangan)."""
        return round(self.price_krw / self.meals_count) if self.meals_count else 0


class MenuItem(Base, TimestampMixin):
    """Taom — menyudagi bitta pozitsiya."""

    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name_uz: Mapped[str] = mapped_column(String(128))
    name_ru: Mapped[str] = mapped_column(String(128))
    name_ko: Mapped[str] = mapped_column(String(128))
    description_uz: Mapped[str] = mapped_column(Text, default="")
    description_ru: Mapped[str] = mapped_column(Text, default="")
    description_ko: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[MealCategory] = mapped_column(SAEnum(MealCategory, native_enum=False))
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_halal_certified: Mapped[bool] = mapped_column(Boolean, default=True)
    contains_beef: Mapped[bool] = mapped_column(Boolean, default=False)
    contains_chicken: Mapped[bool] = mapped_column(Boolean, default=False)
    contains_lamb: Mapped[bool] = mapped_column(Boolean, default=False)
    is_vegetarian: Mapped[bool] = mapped_column(Boolean, default=False)
    spicy_level: Mapped[int] = mapped_column(Integer, default=0)  # 0 (achchiq emas) — 3 (juda achchiq)
    allergens: Mapped[str] = mapped_column(String(255), default="")
    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def name(self, lang: str) -> str:
        return {"uz": self.name_uz, "ru": self.name_ru, "ko": self.name_ko}.get(lang, self.name_uz)

    def description(self, lang: str) -> str:
        return {
            "uz": self.description_uz,
            "ru": self.description_ru,
            "ko": self.description_ko,
        }.get(lang, self.description_uz)


class MenuSlot(Base, TimestampMixin):
    """Qaysi taom qaysi haftaning qaysi kunida beriladi."""

    __tablename__ = "menu_slots"
    __table_args__ = (
        UniqueConstraint("week_start", "weekday", "menu_item_id", name="uq_menu_slot"),
        Index("ix_menu_slot_week_weekday", "week_start", "weekday"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    week_start: Mapped[date] = mapped_column(Date)  # shu haftaning dushanba kuni
    weekday: Mapped[int] = mapped_column(Integer)  # 0=dushanba ... 6=yakshanba
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    capacity: Mapped[int] = mapped_column(Integer, default=999)  # oshxonaning kunlik ishlab chiqarish quvvati
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)

    menu_item: Mapped["MenuItem"] = relationship(lazy="joined")


class CartItem(Base, TimestampMixin):
    """Foydalanuvchining vaqtinchalik (to'lovgacha bo'lgan) savati."""

    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("user_id", "delivery_date", "menu_item_id", name="uq_cart_user_date_item"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    delivery_date: Mapped[date] = mapped_column(Date)
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    qty: Mapped[int] = mapped_column(Integer, default=1)

    menu_item: Mapped["MenuItem"] = relationship(lazy="joined")


class Order(Base, TimestampMixin):
    """Xarid qilish niyati. To'lovsiz ham mavjud bo'lishi mumkin (draft holatda)."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    amount_krw: Mapped[int] = mapped_column(Integer)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus, native_enum=False), default=OrderStatus.DRAFT)

    # Quyidagi uchta maydon ATAYLAB umumiy (generic) qilib qo'yilgan — istalgan
    # to'lov provayderi uchun shu uchtasi yetarli. Provayderga xos alohida
    # jadval yaratish SHART EMAS.
    provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    provider_payment_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    provider_payload: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON matn ko'rinishida

    starts_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    ends_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    user: Mapped["User"] = relationship()
    plan: Mapped["Plan"] = relationship()


class OrderItem(Base, TimestampMixin):
    """Buyurtma tarkibidagi bitta kunlik taom.

    DIQQAT: nomi va narxi shu yerda "suratga olinadi" (snapshot). Kelajakda
    menyu yoki narx o'zgarsa ham, eski buyurtmalar tarixi o'zgarmay qoladi.
    """

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    delivery_date: Mapped[date] = mapped_column(Date)
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    qty: Mapped[int] = mapped_column(Integer, default=1)
    item_name_snapshot: Mapped[str] = mapped_column(String(128))
    unit_price_krw: Mapped[int] = mapped_column(Integer)

    order: Mapped["Order"] = relationship(back_populates="items")


class Subscription(Base, TimestampMixin):
    """To'lovi tasdiqlangan, faol obuna."""

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    starts_on: Mapped[date] = mapped_column(Date)
    ends_on: Mapped[date] = mapped_column(Date, index=True)
    meals_total: Mapped[int] = mapped_column(Integer)
    meals_used: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[SubscriptionStatus] = mapped_column(
        SAEnum(SubscriptionStatus, native_enum=False), default=SubscriptionStatus.ACTIVE, index=True
    )
    renewal_reminded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship()
    plan: Mapped["Plan"] = relationship()

    @property
    def meals_left(self) -> int:
        """Necha ta ovqat ishlatilmay qolganini hisoblaydi."""
        return max(self.meals_total - self.meals_used, 0)


class Delivery(Base, TimestampMixin):
    """Bitta kunlik yetkazib berish yozuvi."""

    __tablename__ = "deliveries"
    __table_args__ = (
        UniqueConstraint("subscription_id", "delivery_date", name="uq_delivery_sub_date"),  # kuniga bitta ovqat
        Index("ix_delivery_date_factory", "delivery_date", "factory_id"),  # oshxona hisoboti uchun
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id"))
    delivery_date: Mapped[date] = mapped_column(Date, index=True)
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    status: Mapped[DeliveryStatus] = mapped_column(
        SAEnum(DeliveryStatus, native_enum=False), default=DeliveryStatus.PLANNED, index=True
    )
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    menu_item: Mapped["MenuItem"] = relationship(lazy="joined")
    user: Mapped["User"] = relationship()
    factory: Mapped["Factory"] = relationship()
    subscription: Mapped["Subscription"] = relationship()


class Feedback(Base, TimestampMixin):
    """Yetkazib berilgan ovqat haqida fikr-mulohaza."""

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    delivery_id: Mapped[int] = mapped_column(ForeignKey("deliveries.id"))
    rating: Mapped[int] = mapped_column(Integer)  # 1 dan 5 gacha
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)


class BroadcastLog(Base, TimestampMixin):
    """Bir xil avtomatik xabarni ikki marta yubormaslik uchun jurnal."""

    __tablename__ = "broadcast_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(64), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    ref_date: Mapped[date] = mapped_column(Date)
