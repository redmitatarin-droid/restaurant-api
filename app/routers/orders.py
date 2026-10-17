
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.database import get_session
from app.models import Order, User, OrderItem
from app.schemas import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
)
from app.security import get_current_user, require_admin
from app.services import order_service


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        order = order_service.create_order(
            session=session,
            user_id=current_user.id,
            order_data=order_data,
        )
        # явно подгружаем items.product, чтобы отдать их фронту
        _ = order.items
        for item in order.items:
            _ = item.product
        return {
            "id": order.id,
            "user_id": order.user_id,
            "total": order.total,
            "status": order.status,
            "created_at": order.created_at,
            "items": [
                {
                    "product_id": item.product_id,
                    "name": item.product.name if item.product else "Блюдо удалено",
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                }
                for item in order.items
            ],
        }
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("")
def get_orders(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product)
        )
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    )
    orders = session.scalars(statement).all()

    return [
        {
            "id": order.id,
            "total": order.total,
            "status": order.status,
            "created_at": order.created_at,
            "items": [
                {
                    "product_id": item.product_id,
                    "name": item.product.name if item.product else "Блюдо удалено",
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                }
                for item in order.items
            ],
        }
        for order in orders
    ]

@router.get("/admin")
def get_all_orders(
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    orders = (
        session.query(Order)
        .options(
            selectinload(Order.user),
            selectinload(Order.items).selectinload(OrderItem.product),
        )
        .order_by(Order.created_at.desc())
        .all()
    )

    return [
        {
            "id": order.id,
            "status": order.status,
            "created_at": order.created_at,
            "total": order.total,
            "customer": {
                "id": order.user.id,
                "name": order.user.name,
                "email": order.user.email,
            },
            "items": [
                {
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price": item.unit_price,
                }
                for item in order.items
            ],
        }
        for order in orders
    ]

@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    allowed_statuses = {
        "pending",
        "confirmed",
        "completed",
        "cancelled",
    }

    if data.new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Недопустимый статус заказа",
        )

    order = session.get(Order, order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Заказ не найден",
        )

    order.status = data.new_status
    session.commit()
    session.refresh(order)

    return {
        "id": order.id,
        "status": order.status,
    }


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    order = order_service.get_order(
        session=session,
        order_id=order_id,
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # Запрещаем доступ к чужому заказу.
    # Администратор может просматривать любой заказ.
    if (
        order.user_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order

@router.get("/my")
def get_my_orders(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product)
        )
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    )

    orders = session.scalars(statement).all()

    return [
        {
            "id": order.id,
            "total": order.total,
            "status": order.status,
            "created_at": order.created_at,
            "items": [
                {
                    "product_id": item.product_id,
                    "name": item.product.name if item.product else "Блюдо удалено",
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                }
                for item in order.items
            ],
        }
        for order in orders
    ]