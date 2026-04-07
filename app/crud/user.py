from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Получить пользователя по email.

    :param db: Сессия базы данных
    :param email: Email пользователя
    :return: Пользователь или None, если не найден
    """
    result = db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Создать нового пользователя.

    :param db: Сессия базы данных
    :param user_in: Данные для создания пользователя
    :return: Созданный пользователь
    """
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
    """
    Аутентифицировать пользователя по email и паролю.

    :param db: Сессия базы данных
    :param email: Email пользователя
    :param password: Пароль пользователя
    :return: Пользователь, если данные верны, иначе None
    """
    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Получить пользователя по ID.

    :param db: Сессия базы данных
    :param user_id: ID пользователя
    :return: Пользователь или None, если не найден
    """
    result = db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    """
    Обновить данные пользователя.

    :param db: Сессия базы данных
    :param user: Объект пользователя
    :param user_in: Новые данные пользователя
    :return: Обновленный пользователь
    """
    if user_in.full_name is not None:
        user.full_name = user_in.full_name

    if user_in.email is not None:
        user.email = user_in.email

    if user_in.password is not None:
        user.hashed_password = hash_password(user_in.password)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    """
    Удалить пользователя.

    :param db: Сессия базы данных
    :param user: Объект пользователя
    :return: None
    """
    db.delete(user)
    db.commit()


def get_users_by_team_id(db: Session, team_id: int) -> list[User]:
    """
    Получить всех пользователей команды.

    :param db: Сессия базы данных
    :param team_id: ID команды
    :return: Список пользователей команды
    """
    result = db.execute(select(User).where(User.team_id == team_id))
    return result.scalars().all()
