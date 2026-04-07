from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task_comment import TaskComment


def create_comment(
    db: Session,
    text: str,
    task_id: int,
    user_id: int,
) -> TaskComment:
    """
    Создать комментарий к задаче.

    :param db: Сессия базы данных
    :param text: Текст комментария
    :param task_id: ID задачи
    :param user_id: ID пользователя (автора комментария)
    :return: Созданный комментарий
    """
    comment = TaskComment(
        text=text,
        task_id=task_id,
        user_id=user_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comments_by_task(db: Session, task_id: int) -> list[TaskComment]:
    """
    Получить все комментарии для задачи.

    :param db: Сессия базы данных
    :param task_id: ID задачи
    :return: Список комментариев
    """
    result = db.execute(select(TaskComment).where(TaskComment.task_id == task_id))
    return result.scalars().all()
