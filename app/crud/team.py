import random
import string

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.team import Team
from app.models.user import User


def generate_team_code(length: int = 6) -> str:
    """
    Сгенерировать уникальный код команды.

    :param length: Длина кода
    :return: Строка с кодом (буквы и цифры)
    """
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def create_team(db: Session, name: str) -> Team:
    """
    Создать команду.

    :param db: Сессия базы данных
    :param name: Название команды
    :return: Созданная команда
    """
    code = generate_team_code()

    team = Team(
        name=name,
        code=code,
    )

    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def get_team_by_code(db: Session, code: str) -> Team | None:
    """
    Получить команду по коду.

    :param db: Сессия базы данных
    :param code: Код команды
    :return: Команда или None, если не найдена
    """
    result = db.execute(select(Team).where(Team.code == code))
    return result.scalar_one_or_none()


def add_user_to_team(db: Session, user: User, team: Team) -> User:
    """
    Добавить пользователя в команду.

    :param db: Сессия базы данных
    :param user: Объект пользователя
    :param team: Объект команды
    :return: Обновленный пользователь
    """
    user.team_id = team.id
    db.commit()
    db.refresh(user)
    return user


def remove_user_from_team(db: Session, user: User) -> User:
    """
    Удалить пользователя из команды.

    :param db: Сессия базы данных
    :param user: Объект пользователя
    :return: Обновленный пользователь
    """
    user.team_id = None
    user.role = "user"
    db.commit()
    db.refresh(user)
    return user
