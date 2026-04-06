from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.roles import role_required
from app.models.user import User
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from app.crud.task import (
    create_task,
    get_all_tasks,
    get_tasks_by_team,
    get_tasks_by_executor,
    get_task_by_id,
    update_task,
    delete_task,
)
from app.crud.user import get_user_by_id
from app.schemas.comment import CommentCreate, CommentOut
from app.crud.comment import create_comment, get_comments_by_task

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskOut)
def create_new_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("manager")),
) -> TaskOut:
    """
    Создать новую задачу.

    Менеджер может создавать задачи только для участников своей команды.
    Исполнитель задачи должен состоять в той же команде, что и менеджер.

    :param data: Данные задачи
    :param db: Сессия базы данных
    :param current_user: Текущий пользователь с ролью manager
    :return: Созданная задача
    """
    if current_user.team_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Manager is not in a team",
        )

    executor = get_user_by_id(db, data.executor_id)
    if not executor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Executor not found",
        )

    if executor.team_id != current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Executor is not in your team",
        )

    task = create_task(
        db=db,
        title=data.title,
        description=data.description,
        deadline=data.deadline,
        author_id=current_user.id,
        executor_id=executor.id,
        team_id=current_user.team_id,
    )
    return task


@router.get("/", response_model=list[TaskOut])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[TaskOut]:
    """
    Получить список задач.

    - Администратор видит все задачи
    - Менеджер видит задачи своей команды
    - Пользователь видит только свои задачи

    :param db: Сессия базы данных
    :param current_user: Текущий пользователь
    :return: Список задач
    """
    if current_user.role == "admin":
        return get_all_tasks(db)

    if current_user.role == "manager":
        if current_user.team_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manager is not in a team",
            )
        return get_tasks_by_team(db, current_user.team_id)

    return get_tasks_by_executor(db, current_user.id)


@router.patch("/{task_id}", response_model=TaskOut)
def update_task_by_author(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskOut:
    """
    Обновить задачу.

    Редактировать задачу может только ее автор.
    Новый исполнитель должен состоять в той же команде, что и задача.

    :param task_id: ID задачи
    :param data: Новые данные задачи
    :param db: Сессия базы данных
    :param current_user: Текущий пользователь
    :return: Обновленная задача
    """
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only author can update this task",
        )

    executor = get_user_by_id(db, data.executor_id)
    if not executor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Executor not found",
        )

    if executor.team_id != task.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Executor is not in this task team",
        )

    return update_task(
        db=db,
        task=task,
        title=data.title,
        description=data.description,
        deadline=data.deadline,
        executor_id=data.executor_id,
    )


@router.delete("/{task_id}")
def delete_task_by_author(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Удалить задачу.

    Удалить задачу может только ее автор.

    :param task_id: ID задачи
    :param db: Сессия базы данных
    :param current_user: Текущий пользователь
    :return: Сообщение об удалении
    """
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only author can delete this task",
        )

    delete_task(db, task)
    return {"detail": "Task deleted"}


@router.patch("/{task_id}/status", response_model=TaskOut)
def change_task_status(
    task_id: int,
    status_value: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskOut:
    """
    Изменить статус задачи.

    Изменять статус может только исполнитель задачи.
    Возможные статусы: open, in_progress, done.

    :param task_id: ID задачи
    :param status_value: Новый статус
    :param db: Сессия базы данных
    :param current_user: Текущий пользователь
    :return: Обновленная задача
    """
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.executor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only executor can change status",
        )

    if status_value not in ("open", "in_progress", "done"):
        raise HTTPException(status_code=400, detail="Invalid status")

    task.status = status_value
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/comments", response_model=CommentOut)
def add_comment(
    task_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentOut:
    """
    Добавить комментарий к задаче.

    Комментарии могут оставлять только участники команды задачи
    или администратор.

    :param task_id: ID задачи
    :param data: Данные комментария
    :param db: Сессия базы данных
    :param current_user: Текущий пользователь
    :return: Созданный комментарий
    """
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if current_user.role != "admin":
        if current_user.team_id != task.team_id:
            raise HTTPException(status_code=403, detail="Not your team task")

    return create_comment(
        db=db,
        text=data.text,
        task_id=task_id,
        user_id=current_user.id,
    )


@router.get("/{task_id}/comments", response_model=list[CommentOut])
def get_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[CommentOut]:
    """
    Получить список комментариев к задаче.

    :param task_id: ID задачи
    :param db: Сессия базы данных
    :param current_user: Текущий пользователь
    :return: Список комментариев
    """
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if current_user.role != "admin":
        if current_user.team_id != task.team_id:
            raise HTTPException(status_code=403, detail="Not your team task")

    return get_comments_by_task(db, task_id)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskOut:
    """
    Получить задачу по ID.

    Задачу могут просматривать участники команды или администратор.

    :param task_id: ID задачи
    :param db: Сессия базы данных
    :param current_user: Текущий пользователь
    :return: Задача
    """
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if current_user.role != "admin":
        if current_user.team_id != task.team_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your team task",
            )

    return task
