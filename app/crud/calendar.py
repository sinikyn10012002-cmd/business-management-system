from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.meeting import Meeting
from app.models.user import User


def get_day_bounds(target_date: date):
    start_dt = datetime.combine(target_date, time.min)
    end_dt = datetime.combine(target_date, time.max)
    return start_dt, end_dt


def get_tasks_for_day(db: Session, user_id: int, target_date: date):
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


def get_meetings_for_day(db: Session, user_id: int, target_date: date):
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


def build_day_calendar(db: Session, user_id: int, target_date: date):
    tasks = get_tasks_for_day(db, user_id, target_date)
    meetings = get_meetings_for_day(db, user_id, target_date)

    items = []

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


def build_month_calendar(db: Session, user_id: int, year: int, month: int):
    first_day = date(year, month, 1)

    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    current_day = first_day
    days = []

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
