from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CommentCreate(BaseModel):
    text: str


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    created_at: datetime
    task_id: int
    user_id: int
