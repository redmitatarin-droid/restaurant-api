from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_session
from app.logger import logger
from app.models import User
from app.schemas import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.security import require_admin
from app.services import product_service


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.get(
    "",
    response_model=list[ProductResponse],
)
def get_products(
    session: Session = Depends(get_session),
    category_id: int | None = Query(
        default=None,
        ge=1,
        description="ID категории для фильтрации",
    ),
):

    return product_service.get_products(
        session=session,
        category_id=category_id,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    session: Session = Depends(get_session),
):
    product = product_service.get_product(
        session=session,
        product_id=product_id,
    )

    if product is None:
        logger.warning(
            "Активный товар с ID %s не найден",
            product_id,
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product_data: ProductCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    try:
        return product_service.create_product(
            session=session,
            product_data=product_data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
)
def edit_product(
    product_id: int,
    product_data: ProductUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    product = product_service.get_product(
        session=session,
        product_id=product_id,
        include_inactive=True,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    if not product_data.model_fields_set:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Передай хотя бы одно поле для обновления",
        )

    try:
        return product_service.update_product(
            session=session,
            product=product,
            product_data=product_data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

