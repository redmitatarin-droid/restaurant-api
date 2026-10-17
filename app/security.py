
import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_session
from app.models import User, RefreshSession
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.config import SECRET_KEY


load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(
    password: str,
    hashed_password: str
) -> bool:

    return password_hash.verify(
        password,
        hashed_password
    )


ACCESS_TOKEN_MINUTES = 15
def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    # Токен действует ограниченное время.
    expires = now + timedelta(
        minutes=ACCESS_TOKEN_MINUTES
    )
    payload = {
        "sub": str(user_id),
        # iat — время выдачи токена.
        "iat": now,
        # exp — время, после которого токен недействителен.
        "exp": expires
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256"
    )

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials"
        )
    user_id = payload.get("sub")

    if not isinstance(user_id, str) or not user_id.isdigit():
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id = int(user_id)

    user = session.get(
        User,
        user_id
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

def require_admin(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user
    
def create_refresh_token() -> str:
    return secrets.token_urlsafe(48)

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

def get_active_refresh_session(
    session: Session,
    raw_token: str
): # НИХУЯ НЕПОНЯТНО
    token_hash = hash_refresh_token(raw_token)
    statement = select(RefreshSession).where(
        RefreshSession.token_hash == token_hash
    )
    refresh_session = session.scalars(statement).first()
    if refresh_session is None:
        return None
    if refresh_session.revoked:
        return None
    now = datetime.now(timezone.utc)
    expires_at = refresh_session.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= now:
        return None

    return refresh_session