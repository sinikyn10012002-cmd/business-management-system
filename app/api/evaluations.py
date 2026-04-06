from datetime import datetime
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.evaluation import (
    create_evaluation,
    get_average_score,
    get_user_evaluations,
    get_evaluation_by_task_id,
    get_average_score_by_period,
)
from app.crud.task import get_task_by_id
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.roles import role_required
from app.models.user import User
from app.schemas.evaluation import EvaluationCreate, EvaluationOut

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.post("/", response_model=EvaluationOut)
def evaluate_task(
    data: EvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("manager")),
) -> EvaluationOut:
    """
    Оценить выполненную задачу.

    Менеджер может поставить оценку только выполненной задаче своей команды.
    Повторная оценка одной и той же задачи запрещена.

    :param data: Данные оценки (task_id, score, comment)
    :param db: Сессия базы данных
    :param current_user: Текущий пользователь с ролью manager
    :return: Созданная оценка
    """
    task = get_task_by_id(db, data.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != "done":
        raise HTTPException(status_code=400, detail="Task is not completed")

    if current_user.team_id != task.team_id:
        raise HTTPException(status_code=403, detail="Not your team task")

    existing_evaluation = get_evaluation_by_task_id(db, task.id)
    if existing_evaluation:
        raise HTTPException(status_code=400, detail="Task already evaluated")

    return create_evaluation(
        db=db,
        task_id=task.id,
        manager_id=current_user.id,
        employee_id=task.executor_id,
        score=data.score,
        comment=data.comment,
    )


@router.get("/my", response_model=List[EvaluationOut])
def my_evaluations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[EvaluationOut]:
    """
    Получить список оценок текущего пользователя.

    :param db: Сессия базы данных
    :param current_user: Текущий авторизованный пользователь
    :return: Список оценок пользователя
    """
    return get_user_evaluations(db, current_user.id)


@router.get("/average")
def average_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, float]:
    """
    Получить среднюю оценку текущего пользователя.

    :param db: Сессия базы данных
    :param current_user: Текущий авторизованный пользователь
    :return: Средняя оценка
    """
    avg = get_average_score(db, current_user.id)
    return {"average_score": avg or 0.0}


@router.get("/average-by-period")
def average_score_by_period(
    date_from: datetime,
    date_to: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, float]:
    """
    Получить среднюю оценку пользователя за указанный период.

    :param date_from: Начальная дата периода
    :param date_to: Конечная дата периода
    :param db: Сессия базы данных
    :param current_user: Текущий авторизованный пользователь
    :return: Средняя оценка за период
    """
    avg = get_average_score_by_period(
        db=db,
        user_id=current_user.id,
        date_from=date_from,
        date_to=date_to,
    )
    return {"average_score": avg or 0.0}