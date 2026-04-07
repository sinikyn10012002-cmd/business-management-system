from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.meeting import Meeting
from app.models.user import User


def get_users_by_ids(db: Session, user_ids: list[int]) -> list[User]:
    """
    Получить пользователей по списку ID.

    :param db: Сессия базы данных
    :param user_ids: Список ID пользователей
    :return: Список найденных пользователей
    """
    result = db.execute(select(User).where(User.id.in_(user_ids)))
    return result.scalars().all()


def has_meeting_overlap(
    db: Session,
    user_id: int,
    start_time: datetime,
    end_time: datetime,
) -> bool:
    """
    Проверить, есть ли у пользователя пересечение встреч по времени.

    :param db: Сессия базы данных
    :param user_id: ID пользователя
    :param start_time: Время начала новой встречи
    :param end_time: Время окончания новой встречи
    :return: True, если есть пересечение, иначе False
    """
    stmt = (
        select(Meeting)
        .join(Meeting.participants)
        .where(
            User.id == user_id,
            Meeting.start_time < end_time,
            Meeting.end_time > start_time,
        )
    )
    result = db.execute(stmt).scalar_one_or_none()
    return result is not None


def create_meeting(
    db: Session,
    title: str,
    description: str | None,
    start_time: datetime,
    end_time: datetime,
    organizer_id: int,
    participant_ids: list[int],
) -> Meeting:
    """
    Создать встречу.

    :param db: Сессия базы данных
    :param title: Название встречи
    :param description: Описание встречи
    :param start_time: Время начала встречи
    :param end_time: Время окончания встречи
    :param organizer_id: ID организатора
    :param participant_ids: Список ID участников
    :return: Созданная встреча
    """
    participants = get_users_by_ids(db, participant_ids)

    meeting = Meeting(
        title=title,
        description=description,
        start_time=start_time,
        end_time=end_time,
        organizer_id=organizer_id,
        participants=participants,
    )

    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


def get_user_meetings(db: Session, user_id: int) -> list[Meeting]:
    """
    Получить все встречи пользователя.

    :param db: Сессия базы данных
    :param user_id: ID пользователя
    :return: Список встреч пользователя
    """
    stmt = (
        select(Meeting)
        .join(Meeting.participants)
        .options(selectinload(Meeting.participants))
        .where(User.id == user_id)
        .order_by(Meeting.start_time)
    )
    result = db.execute(stmt)
    return result.scalars().unique().all()


def get_meeting_by_id(db: Session, meeting_id: int) -> Meeting | None:
    """
    Получить встречу по ID.

    :param db: Сессия базы данных
    :param meeting_id: ID встречи
    :return: Встреча или None, если не найдена
    """
    stmt = (
        select(Meeting)
        .options(selectinload(Meeting.participants))
        .where(Meeting.id == meeting_id)
    )
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def delete_meeting(db: Session, meeting: Meeting) -> None:
    """
    Удалить встречу.

    :param db: Сессия базы данных
    :param meeting: Объект встречи
    :return: None
    """
    db.delete(meeting)
    db.commit()
