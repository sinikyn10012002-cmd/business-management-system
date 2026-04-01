from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password


def get_user_by_email(db: Session, email: str) -> User | None:
    result = db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


def create_user(db: Session, user_in: UserCreate):
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    result = db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none
