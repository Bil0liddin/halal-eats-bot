"""Ma'lumotlar bazasida jadvallarni yaratadi va namuna (test) ma'lumotlar bilan to'ldiradi.

Ishlatish: python seed.py
"""
from __future__ import annotations

import asyncio
from datetime import date, timedelta

from sqlalchemy import select

from app.db.models import Factory, MealCategory, MenuItem, MenuSlot, Plan, PlanPeriod
from app.db.session import SessionMaker, init_models

FACTORIES = [
    dict(
        name="Ansan 1-sonli sanoat zonasi",
        city="Ansan",
        address="Gyeonggi-do, Ansan-si, Danwon-gu",
        delivery_window="12:00-12:30",
    ),
    dict(
        name="Hwaseong logistika markazi",
        city="Hwaseong",
        address="Gyeonggi-do, Hwaseong-si",
        delivery_window="12:30-13:00",
    ),
]

PLANS = [
    dict(
        code="WEEKLY5",
        name_uz="Haftalik reja (5 kun)",
        name_ru="Недельный план (5 дней)",
        name_ko="주간 플랜 (5일)",
        period=PlanPeriod.WEEKLY,
        meals_count=5,
        duration_days=7,
        price_krw=45000,
        cost_krw=27000,
        sort_order=1,
    ),
    dict(
        code="MONTHLY22",
        name_uz="Oylik reja (22 ish kuni)",
        name_ru="Месячный план (22 рабочих дня)",
        name_ko="월간 플랜 (22 근무일)",
        period=PlanPeriod.MONTHLY,
        meals_count=22,
        duration_days=30,
        price_krw=176000,
        cost_krw=110000,
        sort_order=2,
    ),
]

MENU_ITEMS = [
    dict(
        code="OSH",
        name_uz="O'zbek Palovi",
        name_ru="Узбекский плов",
        name_ko="우즈벡 팔로프",
        description_uz="Guruch, mol go'shti, sabzi va piyoz bilan tayyorlangan O'zbekistonning milliy taomi",
        description_ru="Рис с говядиной, морковью и луком — национальное блюдо Узбекистана",
        description_ko="소고기, 당근, 양파를 넣은 우즈베키스탄 전통 쌀 요리",
        category=MealCategory.MAIN,
        contains_beef=True,
        calories=650,
        allergens="",
        spicy_level=0,
    ),
    dict(
        code="MANTI",
        name_uz="Manti",
        name_ru="Манты",
        name_ko="만티",
        description_uz="Bug'da pishirilgan qiymali xamir cho'ntaklari",
        description_ru="Паровые пельмени с мясной начинкой",
        description_ko="다진 고기를 넣어 찐 만두",
        category=MealCategory.MAIN,
        contains_beef=True,
        calories=450,
        allergens="Bug'doy (gluten), tuxum",
        spicy_level=0,
    ),
    dict(
        code="LAGMON",
        name_uz="Lag'mon",
        name_ru="Лагман",
        name_ko="라그몬",
        description_uz="Qo'lda cho'zilgan lag'mon, mol go'shti va sabzavotlar bilan",
        description_ru="Домашняя лапша с говядиной и овощами",
        description_ko="손으로 뽑은 면과 소고기, 채소 볶음",
        category=MealCategory.MAIN,
        contains_beef=True,
        calories=550,
        allergens="Bug'doy (gluten)",
        spicy_level=1,
    ),
    dict(
        code="SHASHLIK",
        name_uz="Shashlik",
        name_ru="Шашлык",
        name_ko="샤슬릭",
        description_uz="Cho'g'da pishirilgan mol go'shti shashligi",
        description_ru="Шашлык из говядины, приготовленный на углях",
        description_ko="숯불에 구운 소고기 꼬치",
        category=MealCategory.MAIN,
        contains_beef=True,
        calories=500,
        allergens="",
        spicy_level=1,
    ),
    dict(
        code="CHUCHVARA",
        name_uz="Chuchvara",
        name_ru="Чучвара",
        name_ko="추치바라",
        description_uz="Mayda go'shtli chuchvara, issiq sho'rvada",
        description_ru="Маленькие мясные пельмени в горячем бульоне",
        description_ko="따뜻한 육수에 담긴 작은 고기 만두",
        category=MealCategory.SOUP,
        contains_beef=True,
        calories=400,
        allergens="Bug'doy (gluten), tuxum",
        spicy_level=0,
    ),
    dict(
        code="SOMSA",
        name_uz="Somsa",
        name_ru="Самса",
        name_ko="솜사",
        description_uz="Tandirda pishirilgan qiymali xamir pirogi",
        description_ru="Слоёное тесто с мясной начинкой, запечённое в тандыре",
        description_ko="화덕에서 구운 다진 고기 페이스트리",
        category=MealCategory.MAIN,
        contains_beef=True,
        calories=480,
        allergens="Bug'doy (gluten)",
        spicy_level=0,
    ),
]


def _next_monday() -> date:
    """Bugundan keyingi eng yaqin dushanba sanasini qaytaradi."""
    today = date.today()
    days_ahead = (7 - today.weekday()) % 7 or 7
    return today + timedelta(days=days_ahead)


async def main() -> None:
    await init_models()

    async with SessionMaker() as session:
        factories = []
        for data in FACTORIES:
            result = await session.execute(select(Factory).where(Factory.name == data["name"]))
            existing = result.scalar_one_or_none()
            factories.append(existing or Factory(**data))
            if existing is None:
                session.add(factories[-1])

        for data in PLANS:
            result = await session.execute(select(Plan).where(Plan.code == data["code"]))
            if result.scalar_one_or_none() is None:
                session.add(Plan(**data))

        menu_items = []
        for data in MENU_ITEMS:
            result = await session.execute(select(MenuItem).where(MenuItem.code == data["code"]))
            existing = result.scalar_one_or_none()
            menu_items.append(existing or MenuItem(**data))
            if existing is None:
                session.add(menu_items[-1])

        await session.flush()

        # Keyingi 2 haftaga namuna menyu jadvalini tuzamiz — har bir kunga
        # BITTA emas, 3 TA taom varianti beriladi, shunda foydalanuvchi
        # haqiqatan ham tanlov qila oladi (aylanma oyna: har kun uchun
        # ro'yxatdagi 3 ta ketma-ket taom, boshqa kunlarda siljiydi).
        options_per_day = 3
        monday = _next_monday()
        for week_offset in range(2):
            week_start = monday + timedelta(weeks=week_offset)
            for weekday in range(7):
                for offset in range(options_per_day):
                    item = menu_items[(weekday + offset) % len(menu_items)]
                    result = await session.execute(
                        select(MenuSlot).where(
                            MenuSlot.week_start == week_start,
                            MenuSlot.weekday == weekday,
                            MenuSlot.menu_item_id == item.id,
                        )
                    )
                    if result.scalar_one_or_none() is None:
                        session.add(MenuSlot(week_start=week_start, weekday=weekday, menu_item_id=item.id))

        await session.commit()

    print("Namuna ma'lumotlar muvaffaqiyatli qo'shildi:")
    print(f"  - {len(FACTORIES)} ta fabrika")
    print(f"  - {len(PLANS)} ta obuna rejasi")
    print(f"  - {len(MENU_ITEMS)} ta taom")
    print("  - Keyingi 2 haftalik menyu jadvali")


if __name__ == "__main__":
    asyncio.run(main())
