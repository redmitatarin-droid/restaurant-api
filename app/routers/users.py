from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from sqlalchemy.orm import Session
from app.database import get_session
from app.schemas import (
    UserCreate,
    UserResponse
)
from app.services import user_service
from app.security import get_current_user
from app.models import User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }


@router.get(
    "",
    response_model=list[UserResponse]
)
def get_users(
    session: Session = Depends(get_session)
):
    return user_service.get_users(
        session
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    session: Session = Depends(get_session)
):
    user = user_service.get_user(
        session,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=201
)
def create_user(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    return user_service.create_user(
        session=session,
        user_data=user_data
    )


