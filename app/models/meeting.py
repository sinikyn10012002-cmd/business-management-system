from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


meeting_participants = Table(
    "meeting_participants",
    Base.metadata,
    Column("meeting_id", ForeignKey("meetings.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    organizer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    organizer = relationship("User", foreign_keys=[organizer_id])
    participants = relationship(
        "User", secondary=meeting_participants, back_populates="meetings"
    )

    def __str__(self):
        return self.title
