from sqlalchemy.orm import Session

from app.models.user import User


def update_user_role(db: Session, user: User, role: str) -> User:
    """
    Обновить роль пользователя.

    :param db: Сессия базы данных
    :param user: Объект пользователя
    :param role: Новая роль пользователя
    :return: Обновленный пользователь
    """
    user.role = role
    db.commit()
    db.refresh(user)
    return user
