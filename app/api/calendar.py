from datetime import datetime, date
from typing import Dict, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.crud.calendar import build_day_calendar, build_month_calendar
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.calendar import CalendarDayResponse, CalendarMonthResponse

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.get("/day", response_model=CalendarDayResponse)
def get_calendar_day(
    day: str = Query(..., description="Дата в формате YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CalendarDayResponse:
    """
    Получить календарь пользователя на конкретный день.

    Преобразует строку даты в объект date и формирует список
    событий, задач и встреч на выбранный день.

    :param day: Дата в формате YYYY-MM-DD
    :param db: Сессия базы данных
    :param current_user: Текущий авторизованный пользователь
    :return: Данные календаря за день
    """
    target_date: date = datetime.strptime(day, "%Y-%m-%d").date()
    items = build_day_calendar(db, current_user.id, target_date)

    return {
        "day": target_date,
        "items": items,
    }


@router.get("/month", response_model=CalendarMonthResponse)
def get_calendar_month(
    year: int = Query(..., description="Год"),
    month: int = Query(..., ge=1, le=12, description="Месяц (1-12)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CalendarMonthResponse:
    """
    Получить календарь пользователя на месяц.

    Формирует календарь по дням и возвращает список событий,
    задач и встреч на каждый день месяца.

    :param year: Год
    :param month: Месяц (1-12)
    :param db: Сессия базы данных
    :param current_user: Текущий авторизованный пользователь
    :return: Данные календаря за месяц
    """
    days = build_month_calendar(db, current_user.id, year, month)

    return {
        "year": year,
        "month": month,
        "days": days,
    }
