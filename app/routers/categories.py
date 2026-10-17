from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import User
from app.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.security import require_admin
from app.services import category_service

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get(
    "/",
    response_model=list[CategoryResponse],
)
def read_categories(
    session: Session = Depends(get_session),
):
    return category_service.get_active_categories(session)


@router.get(
    "/admin/all",
    response_model=list[CategoryResponse],
)
def read_all_categories(
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    return category_service.get_all_categories(session)


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_category(
    category_data: CategoryCreate,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    try:
        return category_service.create_category(
            session,
            category_data,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
)
def edit_category(
    category_id: int,
    category_data: CategoryUpdate,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    category = category_service.get_category_by_id(
        session,
        category_id,
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена",
        )

    try:
        return category_service.update_category(
            session,
            category,
            category_data,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error