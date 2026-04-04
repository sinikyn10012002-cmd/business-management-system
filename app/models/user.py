from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)

    team = relationship("Team", back_populates="members")

    meetings = relationship(
        "Meeting", secondary="meeting_participants", back_populates="participants"
    )

    organized_meetings = relationship("Meeting", foreign_keys="Meeting.organizer_id")

    def __str__(self):
        return self.email