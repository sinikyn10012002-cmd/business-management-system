from datetime import datetime
from sqlalchemy import ForeignKey, Integer, DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    __table_args__ = (UniqueConstraint("task_id", name="uq_evaluations_task_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    score: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    task = relationship("Task")
    manager = relationship("User", foreign_keys=[manager_id])
    employee = relationship("User", foreign_keys=[employee_id])
