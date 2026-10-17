
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Order, OrderItem, Product
from app.schemas import OrderCreate


def create_order(
    session: Session,
    user_id: int,
    order_data: OrderCreate,
) -> Order:
    # Защита от пустого заказа.
    if not order_data.items:
        raise ValueError("Order must contain at least one item")

    validated_items: list[tuple[Product, int]] = []
    total = 0

    # Сначала проверяем ВСЕ товары, ещё не создавая заказ.
    for item_data in order_data.items:
        product = session.get(Product, item_data.product_id)

        if product is None:
            raise ValueError(
                f"Product {item_data.product_id} not found"
            )

        if not product.is_active:
            raise ValueError(
                f"Product {product.id} is not available"
            )

        quantity = item_data.quantity

        # Цена берётся из базы, а не из запроса frontend.
        total += product.price * quantity

        validated_items.append((product, quantity))

    # Создаём заказ только после успешной проверки товаров.
    order = Order(
        user_id=user_id,
        total=total,
        status="pending",
    )

    session.add(order)

    # Создаём позиции заказа.
    for product, quantity in validated_items:
        order_item = OrderItem(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=product.price,
        )
        session.add(order_item)

    try:
        session.commit()
        session.refresh(order)

        # Загружаем позиции для ответа API.
        statement = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order.id)
        )
        order = session.scalars(statement).one()

    except Exception:
        session.rollback()
        raise

    return order


def get_order(
    session: Session,
    order_id: int,
) -> Order | None:
    statement = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )

    return session.scalars(statement).first()


def get_orders_for_user(
    session: Session,
    user_id: int,
) -> list[Order]:
    statement = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc(), Order.id.desc())
    )

    return list(session.scalars(statement).all())


def get_all_orders(
    session: Session,
) -> list[Order]:
    statement = (
        select(Order)
        .options(selectinload(Order.items)) #как работает selectinload()
        .order_by(Order.created_at.desc(), Order.id.desc())
    )

    return list(session.scalars(statement).all())


def update_order_status(
    session: Session,
    order: Order,
    new_status: str,
) -> Order:
    order.status = new_status

    try:
        session.commit()
        session.refresh(order)

    except Exception:
        session.rollback()
        raise

    return order
