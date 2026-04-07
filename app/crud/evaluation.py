from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.evaluation import Evaluation


def create_evaluation(
    db: Session,
    task_id: int,
    manager_id: int,
    employee_id: int,
    score: int,
    comment: str | None,
) -> Evaluation:
    """
    Создать оценку для выполненной задачи.

    :param db: Сессия базы данных
    :param task_id: ID задачи
    :param manager_id: ID менеджера, выставившего оценку
    :param employee_id: ID сотрудника, которому выставлена оценка
    :param score: Оценка (например, от 1 до 5)
    :param comment: Комментарий к оценке
    :return: Созданная оценка
    """
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


def get_user_evaluations(db: Session, user_id: int) -> list[Evaluation]:
    """
    Получить все оценки пользователя.

    :param db: Сессия базы данных
    :param user_id: ID пользователя
    :return: Список оценок пользователя
    """
    result = db.execute(select(Evaluation).where(Evaluation.employee_id == user_id))
    return result.scalars().all()


def get_average_score(db: Session, user_id: int) -> float | None:
    """
    Получить среднюю оценку пользователя.

    :param db: Сессия базы данных
    :param user_id: ID пользователя
    :return: Средняя оценка или None, если оценок нет
    """
    result = db.execute(
        select(func.avg(Evaluation.score)).where(Evaluation.employee_id == user_id)
    )
    return result.scalar()


def get_evaluation_by_task_id(db: Session, task_id: int) -> Evaluation | None:
    """
    Получить оценку по ID задачи.

    :param db: Сессия базы данных
    :param task_id: ID задачи
    :return: Оценка или None, если не найдена
    """
    result = db.execute(select(Evaluation).where(Evaluation.task_id == task_id))
    return result.scalar_one_or_none()


def get_average_score_by_period(
    db: Session,
    user_id: int,
    date_from: datetime,
    date_to: datetime,
) -> float | None:
    """
    Получить среднюю оценку пользователя за период.

    :param db: Сессия базы данных
    :param user_id: ID пользователя
    :param date_from: Начало периода
    :param date_to: Конец периода
    :return: Средняя оценка за период или None, если оценок нет
    """
    result = db.execute(
        select(func.avg(Evaluation.score)).where(
            Evaluation.employee_id == user_id,
            Evaluation.created_at >= date_from,
            Evaluation.created_at <= date_to,
        )
    )
    return result.scalar()
