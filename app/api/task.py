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
):
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
):
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
):
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
):
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only author can delete this task")

    delete_task(db, task)
    return {"detail": "Task deleted"}


@router.patch("/{task_id}/status", response_model=TaskOut)
def change_task_status(
    task_id: int,
    status_value: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
):
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
):
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
):
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
