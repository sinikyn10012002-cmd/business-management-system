from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.evaluation import Evaluation
from datetime import datetime


def create_evaluation(
    db: Session,
    task_id: int,
    manager_id: int,
    employee_id: int,
    score: int,
    comment: str | None,
):
    evaluation = Evaluation(
        task_id=task_id,
        manager_id=manager_id,
        employee_id=employee_id,
        score=score,
        comment=comment,
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation


def get_user_evaluations(db: Session, user_id: int):
    result = db.execute(select(Evaluation).where(Evaluation.employee_id == user_id))
    return result.scalars().all()


def get_average_score(db: Session, user_id: int):
    result = db.execute(
        select(func.avg(Evaluation.score)).where(Evaluation.employee_id == user_id)
    )
    return result.scalar()


def get_evaluation_by_task_id(db: Session, task_id: int) -> Evaluation | None:
    result = db.execute(select(Evaluation).where(Evaluation.task_id == task_id))
    return result.scalar_one_or_none()


def get_average_score_by_period(
    db: Session,
    user_id: int,
    date_from: datetime,
    date_to: datetime,
):
    result = db.execute(
        select(func.avg(Evaluation.score)).where(
            Evaluation.employee_id == user_id,
            Evaluation.created_at >= date_from,
            Evaluation.created_at <= date_to,
        )
    )
    return result.scalar()
