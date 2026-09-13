"""Biznes mantiqni sinovdan o'tkazish — pytest SHART EMAS, PostgreSQL yoki
Telegramga ulanish TALAB QILINMAYDI. Ishlatish: `python tests/test_business_logic.py`

Sinovlar ro'yxati:
1. savatga 5 ta ovqat qo'shish
2. bir xil kunni qayta tanlash dublikat yaratmasligi
3. buyurtma yaratish va kod (reference) formati
4. to'lov ko'rsatmalarida buyurtma kodi va bank ma'lumotlari borligi
5. to'lovni tasdiqlash obunani ochishi
6. IDEMPOTENTLIK: bir xil to'lovni ikki marta tasdiqlash faqat 1 ta obuna berishi
7. yetkazishlar (Delivery) yaratilishi
8. checkout'dan keyin savat tozalanishi
9. oshxona hisoboti
10. bitta kunni bekor qilish (skip)
11. bo'sh savatdan checkout xato berishi
12. statistika so'rovi
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Loyiha ildizini sys.path'ga qo'shamiz — shunda bu fayl to'g'ridan-to'g'ri
# `python tests/test_business_logic.py` deb ishga tushirilganda ham `app`
# paketini topa oladi.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Sozlamalar app.config import qilinishidan OLDIN o'rnatilishi kerak — shunda
# haqiqiy .env fayli mavjud bo'lsa ham, testlar doim SQLite'da, hech qanday
# tashqi xizmatga ulanmasdan ishlaydi.
os.environ["BOT_TOKEN"] = "123456:TEST_TOKEN"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./_test_business_logic.db"
os.environ.setdefault("WEBAPP_URL", "https://example.com")
os.environ.setdefault("ADMIN_IDS", "1")

import asyncio
from datetime import date, datetime, timedelta, timezone

from app.db.models import Factory, MealCategory, MenuItem, MenuSlot, Plan, PlanPeriod
from app.db.session import SessionMaker, engine, init_models
from app.services import subscriptions as sub_service
from app.services import users as user_service
from app.services.payments import get_provider
from app.services.reports import get_kitchen_plan, get_stats


async def setup_fixtures():
    """Sinovlar uchun boshlang'ich ma'lumotlarni yaratadi: 1 fabrika, 1 reja (5 ovqat), 5 taom, 5 kunlik menyu."""
    async with SessionMaker() as session:
        factory = Factory(name="Test Zavodi", city="Ansan", address="Test manzil")
        session.add(factory)

        plan = Plan(
            code="TEST5",
            name_uz="Test reja",
            name_ru="Тестовый план",
            name_ko="테스트 플랜",
            period=PlanPeriod.WEEKLY,
            meals_count=5,
            duration_days=7,
            price_krw=45000,
        )
        session.add(plan)

        items = []
        for i in range(5):
            item = MenuItem(
                code=f"ITEM{i}",
                name_uz=f"Taom {i}",
                name_ru=f"Блюдо {i}",
                name_ko=f"음식 {i}",
                category=MealCategory.MAIN,
            )
            items.append(item)
            session.add(item)
        await session.flush()

        today = date.today()
        monday = today + timedelta(days=(7 - today.weekday()) % 7 or 7)
        for weekday in range(5):
            session.add(MenuSlot(week_start=monday, weekday=weekday, menu_item_id=items[weekday].id))
        # Dushanba kuniga IKKINCHI variantni ham qo'shamiz — 2-sinov (qayta
        # tanlash) haqiqiy almashtirishni tekshira olishi uchun (ikkalasi ham
        # menyuda mavjud bo'lgan taomlar bo'lishi kerak).
        session.add(MenuSlot(week_start=monday, weekday=0, menu_item_id=items[1].id))

        await session.commit()
        return factory.id, plan.id, [i.id for i in items], monday


async def main() -> None:
    await init_models()
    factory_id, plan_id, item_ids, monday = await setup_fixtures()

    try:
        await _run_checks(factory_id, plan_id, item_ids, monday)
    finally:
        await engine.dispose()


async def _run_checks(factory_id: int, plan_id: int, item_ids: list[int], monday: date) -> None:
    async with SessionMaker() as session:
        user = await user_service.get_or_create_user(session, telegram_id=111222333, username="tester")
        await user_service.complete_registration(
            session, user, full_name="Test Ishchi", phone="010-1111-2222", factory_id=factory_id, delivery_note="1-sex"
        )
        await session.commit()

        # ---- 1. Savatga 5 ta ovqat qo'shish ----
        for i in range(5):
            await sub_service.set_cart_item(
                session, user, plan_id=plan_id, delivery_date=monday + timedelta(days=i), menu_item_id=item_ids[i]
            )
        await session.commit()
        items = await sub_service.get_cart_items(session, user, plan_id=plan_id)
        assert len(items) == 5, f"5 ta ovqat kutilgan edi, {len(items)} ta topildi"
        print("1. OK: savatga 5 ta ovqat qo'shildi")

        # ---- 2. Bir xil kunni qayta tanlash dublikat yaratmasligi ----
        await sub_service.set_cart_item(
            session, user, plan_id=plan_id, delivery_date=monday, menu_item_id=item_ids[1]
        )
        await session.commit()
        items = await sub_service.get_cart_items(session, user, plan_id=plan_id)
        assert len(items) == 5, "Qayta tanlash dublikat yaratmasligi kerak edi"
        monday_item = next(ci for ci in items if ci.delivery_date == monday)
        assert monday_item.menu_item_id == item_ids[1], "Dushanba kunidagi tanlov ALMASHTIRILGAN bo'lishi kerak edi"
        print("2. OK: bir xil kunni qayta tanlash almashtiradi, dublikat yaratmaydi")

        # ---- 3. Buyurtma yaratish va kod formati ----
        order = await sub_service.create_order_from_cart(session, user, plan_id, lang="uz")
        await session.commit()
        assert order.reference.startswith("HL"), "Kod 'HL' bilan boshlanishi kerak"
        assert len(order.reference) == 8, f"Kod uzunligi 8 bo'lishi kerak, {len(order.reference)} topildi"
        print(f"3. OK: buyurtma yaratildi, kod={order.reference}")

        # ---- 4. To'lov ko'rsatmalarida kod va bank ma'lumotlari borligi ----
        provider = get_provider("manual")
        intent = await provider.create_payment(
            reference=order.reference, amount_krw=order.amount_krw, description="test", lang="uz"
        )
        assert order.reference in intent.instructions, "Ko'rsatmalarda buyurtma kodi bo'lishi kerak"
        assert "KB Kookmin Bank" in intent.instructions, "Ko'rsatmalarda bank nomi bo'lishi kerak"
        print("4. OK: to'lov ko'rsatmalarida kod va bank ma'lumotlari bor")

        # ---- 5. To'lovni tasdiqlash obunani ochadi ----
        subscription = await sub_service.confirm_payment(session, order, lang="uz")
        await session.commit()
        assert subscription.meals_total == 5
        assert subscription.status.value == "active"
        print(f"5. OK: obuna ochildi, id={subscription.id}, meals_total={subscription.meals_total}")

        # ---- 6. IDEMPOTENTLIK: bir xil to'lovni ikki marta tasdiqlash ----
        subscription_again = await sub_service.confirm_payment(session, order, lang="uz")
        await session.commit()
        assert subscription.id == subscription_again.id, "IDEMPOTENTLIK BUZILDI: ikkinchi marta yangi obuna yaratildi!"
        print("6. OK: idempotentlik ishlayapti — ikkinchi tasdiqlash yangi obuna yaratmadi")

        # ---- 7. Yetkazishlar (Delivery) yaratilishi ----
        from sqlalchemy import select

        from app.db.models import Delivery

        result = await session.execute(select(Delivery).where(Delivery.subscription_id == subscription.id))
        deliveries = result.scalars().all()
        assert len(deliveries) == 5, f"5 ta yetkazish kutilgan edi, {len(deliveries)} ta topildi"
        print("7. OK: 5 ta Delivery yozuvi yaratildi")

        # ---- 8. Checkout'dan keyin savat tozalanishi ----
        cart_after = await sub_service.get_cart_items(session, user)
        assert len(cart_after) == 0, "Checkout'dan keyin savat bo'sh bo'lishi kerak edi"
        print("8. OK: checkout'dan keyin savat tozalandi")

        # ---- 9. Oshxona hisoboti ----
        first_delivery_date = min(d.delivery_date for d in deliveries)
        kitchen_rows = await get_kitchen_plan(session, first_delivery_date, lang="uz")
        assert len(kitchen_rows) >= 1, "Oshxona hisobotida kamida 1 qator bo'lishi kerak edi"
        assert kitchen_rows[0].count >= 1
        print(f"9. OK: oshxona hisoboti ishlayapti ({len(kitchen_rows)} qator)")

        # ---- 10. Bitta kunni bekor qilish (skip) ----
        first_delivery = next(d for d in deliveries if d.delivery_date == first_delivery_date)
        ends_on_before = subscription.ends_on
        now_early = datetime.combine(first_delivery.delivery_date - timedelta(days=2), datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        await sub_service.skip_delivery(session, first_delivery, now=now_early, cutoff_hour=20, lang="uz")
        await session.commit()
        assert first_delivery.status.value == "skipped"
        await session.refresh(subscription)
        assert subscription.ends_on == ends_on_before + timedelta(days=1), "Obuna muddati 1 kunga uzaytirilishi kerak edi"
        print("10. OK: kun bekor qilindi, obuna muddati 1 kunga uzaytirildi")

        # ---- 11. Bo'sh savatdan checkout xato berishi ----
        try:
            await sub_service.create_order_from_cart(session, user, plan_id, lang="uz")
            raise AssertionError("Bo'sh savatdan checkout xato berishi kerak edi, lekin bermadi!")
        except sub_service.BusinessError:
            print("11. OK: bo'sh savatdan checkout to'g'ri xato beradi")

        # ---- 12. Statistika so'rovi ----
        stats = await get_stats(session)
        assert stats.total_users >= 1
        assert stats.registered_users >= 1
        assert stats.active_subscriptions >= 1
        assert stats.total_revenue_krw >= order.amount_krw
        print(
            f"12. OK: statistika ishlayapti (users={stats.total_users}, "
            f"subs={stats.active_subscriptions}, revenue={stats.total_revenue_krw})"
        )

    print("\nHAMMA 12 TA SINOV MUVAFFAQIYATLI O'TDI ✅")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        # Test bazasi faylini tozalab qo'yamiz (Windows'da fayl hali ochiq
        # bo'lib qolishi mumkin, shuning uchun xatoni e'tiborsiz qoldiramiz)
        db_path = "./_test_business_logic.db"
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except OSError:
            pass
