"""Seed the database with a sample halal menu. Run once: python seed.py"""

from app.db import get_session, init_db
from app.models import Product

SAMPLE_PRODUCTS = [
    ("Chicken Biryani", 12000, "Fragrant spiced rice with halal chicken"),
    ("Lamb Kebab Plate", 15000, "Grilled halal lamb skewers with rice and salad"),
    ("Falafel Wrap", 8000, "Crispy falafel, hummus, and fresh veggies in a wrap"),
    ("Chicken Shawarma", 9500, "Halal chicken shawarma with garlic sauce"),
    ("Vegetable Samosa (3pc)", 5000, "Crispy pastries with spiced vegetable filling"),
]


def main() -> None:
    init_db()
    with get_session() as session:
        for name, price, description in SAMPLE_PRODUCTS:
            exists = session.query(Product).filter_by(name=name).first()
            if not exists:
                session.add(Product(name=name, price=price, description=description))
    print(f"Seeded {len(SAMPLE_PRODUCTS)} products (skipping any that already existed).")


if __name__ == "__main__":
    main()
