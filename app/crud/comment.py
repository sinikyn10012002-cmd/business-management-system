from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task_comment import TaskComment


def create_comment(db: Session, text: str, task_id: int, user_id: int):
    comment = TaskComment(
        text=text,
        task_id=task_id,
        user_id=user_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comments_by_task(db: Session, task_id: int):
    result = db.execute(select(TaskComment).where(TaskComment.task_id == task_id))
    return result.scalars().all()
