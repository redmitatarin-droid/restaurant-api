from sqlalchemy import select
from sqlalchemy.orm import Session
from app.security import hash_password
from app.models import User
from app.schemas import UserCreate


def get_users(
    session: Session
):
    statement = select(User)

    users = session.scalars(
        statement
    ).all()
    return users


def get_user(
    session: Session,
    user_id: int
):
    user = session.get(
        User,
        user_id
    )
    return user


def create_user(
    session: Session,
    user_data: UserCreate
):
    password = user_data.password
    hashed_password = hash_password(password)
    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        role="customer" )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_email(
        session: Session,
        email: str
):
    statement = select(User).where(User.email == email)
    user = session.scalar(statement)
    return user