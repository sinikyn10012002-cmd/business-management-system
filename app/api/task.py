from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.roles import role_required
from app.models.user import User
from app.schemas.task import TaskCreate, TaskOut
from app.crud.task import create_task
from app.crud.user import get_user_by_id

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
