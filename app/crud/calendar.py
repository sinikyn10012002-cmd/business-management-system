from datetime import date, datetime, time, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.meeting import Meeting
from app.models.user import User


def get_day_bounds(target_date: date) -> tuple[datetime, datetime]:
    """
    Возвращает начало и конец указанного дня.

    :target_date: Дата, для которой нужно определить временные границы.
    :returns:Кортеж из двух объектов datetime:
        - начало дня (00:00:00),
        - конец дня (23:59:59.999999).
    """
    start_dt = datetime.combine(target_date, time.min)
    end_dt = datetime.combine(target_date, time.max)
    return start_dt, end_dt


def get_tasks_for_day(db: Session, user_id: int, target_date: date) -> list[Task]:
    """Получает список задач пользователя на указанную дату.

    Выбираются задачи, у которых исполнитель совпадает с user_id,
    а дедлайн попадает в границы target_date.

    :db: Сессия базы данных.
    :user_id: Идентификатор пользователя.
    :target_date: Дата, за которую нужно получить задачи.

    :returns: Список задач пользователя, отсортированный по дедлайну.
    """
    start_dt, end_dt = get_day_bounds(target_date)

    stmt = (
        select(Task)
        .where(
            Task.executor_id == user_id,
            Task.deadline >= start_dt,
            Task.deadline <= end_dt,
        )
        .order_by(Task.deadline)
    )
    result = db.execute(stmt)
    return result.scalars().all()


def get_meetings_for_day(db: Session, user_id: int, target_date: date) -> list[Meeting]:
    """Получает список встреч пользователя на указанную дату.

    Выбираются встречи, в которых пользователь является участником,
    а время начала встречи попадает в границы target_date.

    :db: Сессия базы данных.
    :user_id: Идентификатор пользователя.
    :target_date: Дата, за которую нужно получить встречи.

    :returns: Список уникальных встреч, отсортированный по времени начала.
    """
    start_dt, end_dt = get_day_bounds(target_date)

    stmt = (
        select(Meeting)
        .join(Meeting.participants)
        .where(
            User.id == user_id,
            Meeting.start_time >= start_dt,
            Meeting.start_time <= end_dt,
        )
        .order_by(Meeting.start_time)
    )
    result = db.execute(stmt)
    return result.scalars().unique().all()


def build_day_calendar(
    db: Session,
    user_id: int,
    target_date: date,
) -> list[dict[str, Any]]:
    """Формирует календарь пользователя за один день.

    В итоговый список включаются задачи и встречи в едином формате.
    Элементы сортируются по дате и времени.

    :db: Сессия базы данных.
    :user_id: Идентификатор пользователя.
    :target_date: Дата, за которую формируется календарь.

    :returns: Список словарей с данными о задачах и встречах за день.
    """
    tasks = get_tasks_for_day(db, user_id, target_date)
    meetings = get_meetings_for_day(db, user_id, target_date)

    items: list[dict[str, Any]] = []

    for task in tasks:
        items.append(
            {
                "item_type": "task",
                "id": task.id,
                "title": task.title,
                "date": task.deadline.date(),
                "time": task.deadline.strftime("%H:%M") if task.deadline else None,
                "status": getattr(task, "status", None),
            }
        )

    for meeting in meetings:
        items.append(
            {
                "item_type": "meeting",
                "id": meeting.id,
                "title": meeting.title,
                "date": meeting.start_time.date(),
                "time": meeting.start_time.strftime("%H:%M"),
                "status": None,
            }
        )

    items.sort(key=lambda x: (x["date"], x["time"] or "99:99"))
    return items


def build_month_calendar(
    db: Session,
    user_id: int,
    year: int,
    month: int,
) -> list[dict[str, Any]]:
    """Формирует календарь пользователя за месяц.

    Для каждого дня месяца собирается список задач и встреч.

    db: Сессия базы данных.
    user_id: Идентификатор пользователя.
    year: Год календаря.
    month: Месяц календаря.

    :returns: Список словарей, где каждый словарь содержит:
        - day: дата,
        - items: список событий за эту дату.
    """
    first_day = date(year, month, 1)

    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    current_day = first_day
    days: list[dict[str, Any]] = []

    while current_day < next_month:
        items = build_day_calendar(db, user_id, current_day)
        days.append(
            {
                "day": current_day,
                "items": items,
            }
        )
        current_day += timedelta(days=1)

    return days
