from sqlalchemy.orm import Session
from app.models.task import Task


def create_task(
    db: Session,
    title: str,
    description: str | None,
    deadline,
    author_id: int,
    executor_id: int,
    team_id: int,
) -> Task:
    task = Task(
        title=title,
        description=description,
        deadline=deadline,
        author_id=author_id,
        executor_id=executor_id,
        team_id=team_id,
        status="open",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
