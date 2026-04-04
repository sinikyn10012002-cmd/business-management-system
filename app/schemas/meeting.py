from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class MeetingCreate(BaseModel):
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    participant_ids: list[int]

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v, info):
        start_time = info.data.get("start_time")
        if start_time and v <= start_time:
            raise ValueError("Время окончания должно быть больше времени начала")
        return v


class MeetingResponse(BaseModel):
    id: int
    title: str
    description: str | None
    start_time: datetime
    end_time: datetime
    organizer_id: int

    model_config = ConfigDict(from_attributes=True)


class MeetingParticipant(BaseModel):
    id: int
    email: str
    full_name: str | None

    model_config = ConfigDict(from_attributes=True)


class MeetingResponse(BaseModel):
    id: int
    title: str
    description: str | None
    start_time: datetime
    end_time: datetime
    organizer_id: int
    participants: list[MeetingParticipant]

    model_config = ConfigDict(from_attributes=True)
