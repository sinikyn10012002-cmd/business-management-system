from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session, selectinload

from app.models.meeting import Meeting
from app.models.user import User


def get_users_by_ids(db: Session, user_ids: list[int]) -> list[User]:
    result = db.execute(select(User).where(User.id.in_(user_ids)))
    return result.scalars().all()


def has_meeting_overlap(
    db: Session,
    user_id: int,
    start_time,
    end_time,
) -> bool:
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
    start_time,
    end_time,
    organizer_id: int,
    participant_ids: list[int],
):
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
    stmt = (
        select(Meeting)
        .options(selectinload(Meeting.participants))
        .where(Meeting.id == meeting_id)
    )
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def delete_meeting(db: Session, meeting: Meeting):
    db.delete(meeting)
    db.commit()
