from pydantic import BaseModel
from datetime import datetime


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    deadline: datetime | None = None
    executor_id: int


class TaskUpdate(BaseModel):
    title: str
    description: str | None = None
    deadline: datetime | None = None
    executor_id: int


class TaskOut(BaseModel):
    id: int
    title: str
    description: str | None
    deadline: datetime | None
    status: str
    author_id: int
    executor_id: int
    team_id: int
    created_at: datetime

    class Config:
        from_attributes = True
