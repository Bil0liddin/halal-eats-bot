from sqlalchemy.orm import Session, joinedload
from telegram import User as TgUser

from app.models import CartItem, Order, OrderItem, OrderStatus, Product, User


def get_or_create_user(session: Session, tg_user: TgUser, chat_id: int) -> User:
    user = session.query(User).filter_by(telegram_id=tg_user.id).first()
    if user is None:
        user = User(telegram_id=tg_user.id, chat_id=chat_id, display_name=tg_user.full_name)
        session.add(user)
        session.flush()
    elif user.chat_id != chat_id:
        user.chat_id = chat_id
    return user


def list_active_products(session: Session) -> list[Product]:
    return session.query(Product).filter_by(is_active=True).order_by(Product.id).all()


def add_to_cart(session: Session, user: User, product_id: int, qty: int = 1) -> None:
    item = session.query(CartItem).filter_by(user_id=user.id, product_id=product_id).first()
    if item is None:
        session.add(CartItem(user_id=user.id, product_id=product_id, quantity=qty))
    else:
        item.quantity += qty


def remove_from_cart(session: Session, user: User, product_id: int) -> None:
    item = session.query(CartItem).filter_by(user_id=user.id, product_id=product_id).first()
    if item is None:
        return
    if item.quantity > 1:
        item.quantity -= 1
    else:
        session.delete(item)


def get_cart_items(session: Session, user: User) -> list[CartItem]:
    return (
        session.query(CartItem)
        .options(joinedload(CartItem.product))
        .filter_by(user_id=user.id)
        .order_by(CartItem.id)
        .all()
    )


def cart_total(items: list[CartItem]) -> int:
    return sum(ci.product.price * ci.quantity for ci in items)


def clear_cart(session: Session, user: User) -> None:
    session.query(CartItem).filter_by(user_id=user.id).delete()


def create_order_from_cart(session: Session, user: User) -> Order | None:
    items = get_cart_items(session, user)
    if not items:
        return None

    order = Order(user_id=user.id, status=OrderStatus.PENDING_PAYMENT, total_amount=cart_total(items))
    session.add(order)
    session.flush()

    for ci in items:
        session.add(
            OrderItem(
                order_id=order.id,
                product_id=ci.product_id,
                product_name=ci.product.name,
                unit_price=ci.product.price,
                quantity=ci.quantity,
            )
        )
    clear_cart(session, user)
    session.flush()
    return order


def list_user_orders(session: Session, user: User, limit: int = 10) -> list[Order]:
    return (
        session.query(Order)
        .filter_by(user_id=user.id)
        .order_by(Order.created_at.desc())
        .limit(limit)
        .all()
    )


def list_orders_by_status(session: Session, statuses: tuple[str, ...]) -> list[Order]:
    return (
        session.query(Order)
        .filter(Order.status.in_(statuses))
        .order_by(Order.created_at.asc())
        .all()
    )
