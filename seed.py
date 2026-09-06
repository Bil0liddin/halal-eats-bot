"""Seed the database with a sample halal menu. Run once: python seed.py"""

from app.db import get_session, init_db
from app.models import Product

SAMPLE_PRODUCTS = [
    ("O'zbek Palovi", 15000, "Guruch, mol go'shti, sabzi va piyoz bilan tayyorlangan O'zbekistonning milliy taomi"),
    ("Manti", 12000, "Bug'da pishirilgan, qiymali xamir cho'ntaklari"),
    ("Lag'mon", 13000, "Qo'lda cho'zilgan lag'mon, mol go'shti va sabzavotlar bilan"),
    ("Somsa", 6000, "Tandirda pishirilgan, qiymali xamir pirogi"),
    ("Shashlik", 14000, "Cho'g'da pishirilgan mol go'shti shashligi"),
    ("Chuchvara", 10000, "Mayda go'shtli chuchvara, issiq sho'rvada"),
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
