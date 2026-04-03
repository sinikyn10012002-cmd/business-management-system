from sqlalchemy.orm import Session
from app.models.task import Task
from sqlalchemy import select


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


def get_all_tasks(db: Session) -> list[Task]:
    result = db.execute(select(Task))
    return result.scalars().all()


def get_tasks_by_team(db: Session, team_id: int) -> list[Task]:
    result = db.execute(select(Task).where(Task.team_id == team_id))
    return result.scalars().all()


def get_tasks_by_executor(db: Session, executor_id: int) -> list[Task]:
    result = db.execute(select(Task).where(Task.executor_id == executor_id))
    return result.scalars().all()


def get_task_by_id(db: Session, task_id: int) -> Task | None:
    result = db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


def update_task(
    db: Session,
    task: Task,
    title: str,
    description: str | None,
    deadline,
    executor_id: int,
) -> Task:
    task.title = title
    task.description = description
    task.deadline = deadline
    task.executor_id = executor_id
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task):
    db.delete(task)
    db.commit()
