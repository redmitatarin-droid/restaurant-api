from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RefreshSession, User
from app.security import (
    create_refresh_token,
    hash_refresh_token
)


REFRESH_TOKEN_DAYS = 7


def create_refresh_session(
    session: Session,
    user: User
) -> str:
    raw_token = create_refresh_token()

    token_hash = hash_refresh_token(raw_token)

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_DAYS
    )

    refresh_session = RefreshSession(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked=False,
        created_at=datetime.now(timezone.utc)
    )

    session.add(refresh_session)
    session.flush()
    return raw_token