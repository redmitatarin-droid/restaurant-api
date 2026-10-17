from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from sqlalchemy.orm import Session
from app.database import get_session
from app.schemas import (
    TokenResponse
)
from app.services import user_service
from app.security import (
    verify_password,
    create_access_token
)
from app.schemas import RefreshRequest, LogoutRequest
from fastapi.security import OAuth2PasswordRequestForm
from app.services import token_service
from app.models import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post('/login', response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = user_service.get_user_by_email(
        session,
        form_data.username,         
    )
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    password_is_correct = verify_password(
        form_data.password,
        user.password_hash
    )
    if not password_is_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    try:
        access_token = create_access_token(user.id)

        refresh_token = token_service.create_refresh_session(
            session,
            user
        )
        session.commit()
    except Exception:
        session.rollback()
        raise

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post(
    "/refresh",
    response_model=TokenResponse
) # НИХУЯ НЕПОНЯТНО, ПОТОМ ПОВТОРИТЬ
def refresh_tokens(
    refresh_data: RefreshRequest,
    session: Session = Depends(get_session)
):
    old_session = token_service.get_active_refresh_session(
        session,
        refresh_data.refresh_token
    )

    if old_session is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )
    user = session.get(User, old_session.user_id)

    if user is None:
        old_session.revoked = True
        session.commit()

        raise HTTPException(
            status_code=401,
            detail="Invalid refresh session"
        )
    try:
        old_session.revoked = True
        new_refresh_token = token_service.create_refresh_session(
            session,
            user
        )
        new_access_token = create_access_token(user.id)
        session.commit()

    except Exception:
        session.rollback()
        raise

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(
    logout_data: LogoutRequest,
    session: Session = Depends(get_session)
):
    refresh_session = token_service.get_active_refresh_session(
        session,
        logout_data.refresh_token
    )
    if refresh_session is None:
        return {"message": "Logged out"}
    refresh_session.revoked = True

    session.commit()

    return {"message": "Logged out"}