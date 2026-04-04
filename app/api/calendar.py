from datetime import datetime

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
):
    target_date = datetime.strptime(day, "%Y-%m-%d").date()
    items = build_day_calendar(db, current_user.id, target_date)

    return {
        "day": target_date,
        "items": items,
    }


@router.get("/month", response_model=CalendarMonthResponse)
def get_calendar_month(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    days = build_month_calendar(db, current_user.id, year, month)

    return {
        "year": year,
        "month": month,
        "days": days,
    }
