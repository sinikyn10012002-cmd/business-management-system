from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class EvaluationCreate(BaseModel):
    task_id: int
    score: int
    comment: str | None = None

    @field_validator("score")
    @classmethod
    def validate_score(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Score must be between 1 and 5")
        return v


class EvaluationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    manager_id: int
    employee_id: int
    score: int
    comment: str | None
    created_at: datetime
