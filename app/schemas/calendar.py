from datetime import datetime, date
from pydantic import BaseModel


class CalendarItem(BaseModel):
    item_type: str  # task / meeting
    id: int
    title: str
    date: date
    time: str | None = None
    status: str | None = None


class CalendarDayResponse(BaseModel):
    day: date
    items: list[CalendarItem]


class CalendarMonthDay(BaseModel):
    day: date
    items: list[CalendarItem]


class CalendarMonthResponse(BaseModel):
    year: int
    month: int
    days: list[CalendarMonthDay]
