"""Seed the database with a sample halal menu. Run once: python seed.py"""

from app.db import get_session, init_db
from app.models import Product

SAMPLE_PRODUCTS = [
    ("Tovuq Biryani", 12000, "Halal tovuq go'shtli mazali ziravorli guruch"),
    ("Qo'y Kabob Tarelkasi", 15000, "Guruch va salat bilan grilda pishirilgan halal qo'y kabob shishlari"),
    ("Falafel O'rami", 8000, "Xrustik falafel, xummus va yangi sabzavotlar bilan o'ralgan"),
    ("Tovuq Shaurma", 9500, "Sarimsoqli sous bilan halal tovuq shaurma"),
    ("Sabzavotli Somsa (3 dona)", 5000, "Ziravorli sabzavot ichlik bilan xrustik somsa"),
]


def main() -> None:
    init_db()
    with get_session() as session:
        for name, price, description in SAMPLE_PRODUCTS:
            exists = session.query(Product).filter_by(name=name).first()
            if not exists:
                session.add(Product(name=name, price=price, description=description))
    print(f"{len(SAMPLE_PRODUCTS)} ta mahsulot qo'shildi (mavjudlari o'tkazib yuborildi).")


if __name__ == "__main__":
    main()
