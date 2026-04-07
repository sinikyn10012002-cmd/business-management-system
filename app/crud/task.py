from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task


def create_task(
    db: Session,
    title: str,
    description: str | None,
    deadline: datetime,
    author_id: int,
    executor_id: int,
    team_id: int,
) -> Task:
    """
    Создать задачу.

    :param db: Сессия базы данных
    :param title: Название задачи
    :param description: Описание задачи
    :param deadline: Срок выполнения задачи
    :param author_id: ID автора задачи
    :param executor_id: ID исполнителя задачи
    :param team_id: ID команды
    :return: Созданная задача
    """
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
    """
    Получить все задачи.

    :param db: Сессия базы данных
    :return: Список всех задач
    """
    result = db.execute(select(Task))
    return result.scalars().all()


def get_tasks_by_team(db: Session, team_id: int) -> list[Task]:
    """
    Получить задачи по команде.

    :param db: Сессия базы данных
    :param team_id: ID команды
    :return: Список задач команды
    """
    result = db.execute(select(Task).where(Task.team_id == team_id))
    return result.scalars().all()


def get_tasks_by_executor(db: Session, executor_id: int) -> list[Task]:
    """
    Получить задачи по исполнителю.

    :param db: Сессия базы данных
    :param executor_id: ID исполнителя
    :return: Список задач исполнителя
    """
    result = db.execute(select(Task).where(Task.executor_id == executor_id))
    return result.scalars().all()


def get_task_by_id(db: Session, task_id: int) -> Task | None:
    """
    Получить задачу по ID.

    :param db: Сессия базы данных
    :param task_id: ID задачи
    :return: Задача или None, если не найдена
    """
    result = db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


def update_task(
    db: Session,
    task: Task,
    title: str,
    description: str | None,
    deadline: datetime,
    executor_id: int,
) -> Task:
    """
    Обновить задачу.

    :param db: Сессия базы данных
    :param task: Объект задачи
    :param title: Новое название задачи
    :param description: Новое описание задачи
    :param deadline: Новый срок выполнения
    :param executor_id: Новый исполнитель
    :return: Обновленная задача
    """
    task.title = title
    task.description = description
    task.deadline = deadline
    task.executor_id = executor_id
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    """
    Удалить задачу.

    :param db: Сессия базы данных
    :param task: Объект задачи
    :return: None
    """
    db.delete(task)
    db.commit()
